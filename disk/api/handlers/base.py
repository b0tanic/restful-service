from aiohttp.web_exceptions import HTTPNotFound
from aiohttp.web_urldispatcher import View
from asyncpgsa import PG
from sqlalchemy import exists, select

from disk.db.schema import import_history_table


class BaseView(View):
    URL_PATH: str

    @property
    def pg(self) -> PG:
        return self.request.app['pg']


class BaseImportView(BaseView):
    @property
    def id(self):
        return str(self.request.match_info.get('id'))

    async def check_import_exists(self):
        query = select([
            exists().where(import_history_table.c.id == self.id)
        ])
        if not await self.pg.fetchval(query):
            raise HTTPNotFound()
