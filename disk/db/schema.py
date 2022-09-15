from enum import Enum, unique

from sqlalchemy import (
    Column, Date, Enum as PgEnum, ForeignKey, ForeignKeyConstraint, Integer,
    MetaData, String, Table,
)


# SQLAlchemy рекомендует использовать единый формат для генерации названий для
# индексов и внешних ключей.
# https://docs.sqlalchemy.org/en/13/core/constraints.html#configuring-constraint-naming-conventions
convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': 'fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s',
    'pk': 'pk__%(table_name)s'
}

metadata = MetaData(naming_convention=convention)


@unique
class ImportType(Enum):
    file = 'FILE'
    folder = 'FOLDER'


parents_table = Table(
    'parents',
    metadata,
    Column('id', String, primary_key=True),
    Column('size', Integer, nullable=False)
)

imports_table = Table(
    'imports',
    metadata,
    Column('parent_id', String, ForeignKey('parents.id', ondelete="CASCADE"), nullable=True),
    Column('id', String, primary_key=True),
    Column('url', String, nullable=True),
    Column('size', Integer, nullable=True),
    Column('update_date', Date, nullable=False, index=True),
    Column('type', PgEnum(ImportType, name='type'), nullable=False)
)

import_history_table = Table(
    'import_history',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('import_id', ForeignKey('imports.id', ondelete="CASCADE"), nullable=False),
    Column('update_date', Date, nullable=False, index=True)
)
