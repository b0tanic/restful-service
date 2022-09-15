from http import HTTPStatus
from typing import Generator
from pandas import DataFrame

from aiohttp.web_response import Response
from aiohttp_apispec import docs, request_schema, response_schema
from aiomisc import chunk_list

from disk.api.schema import ImportsSchema
from disk.db.schema import parents_table, imports_table, import_history_table
from disk.utils.pg import MAX_QUERY_ARGS

from .base import BaseView


class ImportsView(BaseView):
    URL_PATH = '/imports'
    # Так как данных может быть много, а postgres поддерживает только
    # MAX_QUERY_ARGS аргументов в одном запросе, писать в БД необходимо
    # частями.
    # Максимальное кол-во строк для вставки можно рассчитать как отношение
    # MAX_QUERY_ARGS к кол-ву вставляемых в таблицу столбцов.
    MAX_IMPORTS_PER_INSERT = MAX_QUERY_ARGS // len(imports_table.columns)
    MAX_PARENTS_PER_INSERT = MAX_QUERY_ARGS // len(parents_table.columns)
    MAX_HISTORIES_PER_INSERT = MAX_QUERY_ARGS // len(import_history_table.columns)

    @classmethod
    def make_imports_table_rows(cls, items) -> Generator:
        """
        Генерирует данные готовые для вставки в таблицу imports.
        """
        for item in items:
            yield {
                'id': item['id'],
                'parent_id': item['parentId'],
                'url': item['url'],
                'size': item['size'],
                'type': item['type'],
                'update_date': item['updateDate'],
            }

    @classmethod
    def make_parents_table_rows(cls, items) -> Generator:
        """
        Генерирует данные готовые для вставки в таблицу parents.
        """
        df = DataFrame(items)
        for item in df.groupby('parentId', as_index=False).sum():
            yield {
                'id': item['parentId'],
                'size': item['size'],
            }

    @classmethod
    def make_history_table_rows(cls, items, update_date) -> Generator:
        """
        Генерирует данные готовые для вставки в таблицу imports.
        """
        for item in items:
            yield {
                'import_id': item['id'],
                'update_date': update_date,
            }

    @docs(summary='Импортирует элементы файловой системы')
    @request_schema(ImportsSchema())
    @response_schema(None, code=HTTPStatus.CREATED.value)
    async def post(self):
        # Транзакция требуется чтобы в случае ошибки (или отключения клиента,
        # не дождавшегося ответа) откатить частично добавленные изменения.
        async with self.pg.transaction() as conn:
            # Создаем выгрузку
            # query = import_history_table.insert().returning(import_history_table.c.id)
            # history_id = await conn.fetchval(query)

            # Генераторы make_imports_table_rows и make_parents_table_rows
            # лениво генерируют данные, готовые для вставки в таблицы imports
            # и parents на основе данных отправленных клиентом.
            items = self.request['data']['items']
            update_date = self.request['data']['updateDate']
            import_rows = self.make_imports_table_rows(items)
            parent_rows = self.make_parents_table_rows(items)
            history_rows = self.make_history_table_rows(items, update_date)

            # Чтобы уложиться в ограничение кол-ва аргументов в запросе к
            # postgres, а также сэкономить память и избежать создания полной
            # копии данных присланных клиентом во время подготовки - используем
            # генератор chunk_list.
            # Он будет получать из генератора make_imports_table_rows только
            # необходимый для 1 запроса объем данных.
            chunked_import_rows = chunk_list(import_rows, self.MAX_IMPORTS_PER_INSERT)
            chunked_parent_rows = chunk_list(parent_rows, self.MAX_PARENTS_PER_INSERT)
            chunked_history_rows = chunk_list(history_rows, self.MAX_HISTORIES_PER_INSERT)

            query = parents_table.insert()
            for chunk in chunked_parent_rows:
                await conn.execute(query.values(list(chunk)))

            query = imports_table.insert()
            for chunk in chunked_import_rows:
                await conn.execute(query.values(list(chunk)))

            query = import_history_table.insert()
            for chunk in chunked_history_rows:
                await conn.execute(query.values(list(chunk)))

        return Response(status=HTTPStatus.CREATED)
