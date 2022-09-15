from sqlalchemy import and_, func, select

from disk.db.schema import imports_table, parents_table


CITIZENS_QUERY = select([
    imports_table.c.citizen_id,
    imports_table.c.name,
    imports_table.c.birth_date,
    imports_table.c.gender,
    imports_table.c.town,
    imports_table.c.street,
    # В результате LEFT JOIN у жителей не имеющих родственников список
    # relatives будет иметь значение [None]. Чтобы удалить это значение
    # из списка, используется функция array_remove.
    func.array_remove(
        func.array_agg(parents_table.c.relative_id),
        None
    ).label('relatives')
]).select_from(
    imports_table.outerjoin(
        parents_table, and_(
            imports_table.c.import_id == imports_table.c.import_id,
            imports_table.c.citizen_id == parents_table.c.citizen_id
        )
    )
).group_by(
    imports_table.c.import_id,
    imports_table.c.citizen_id
)
