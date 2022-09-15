"""initial
Revision ID: d5f704ed4610
Revises:
Create Date: 2022-09-13 19:53:01.172834
"""
from alembic import op
from sqlalchemy import (
    Column, Date, Enum, ForeignKeyConstraint, Integer, PrimaryKeyConstraint,
    String,
)


# revision identifiers, used by Alembic.
revision = 'd5f704ed4610'
down_revision = None
branch_labels = None
depends_on = None


ImportType = Enum('FILE', 'FOLDER', name='type')


def upgrade():
    op.create_table(
        'parents',
        Column('id', String(), nullable=False),
        Column('size', Integer(), nullable=False),
        PrimaryKeyConstraint('id', name=op.f('pk__parents'))
    )
    op.create_table(
        'imports',
        Column('parent_id', String(), nullable=True),
        Column('id', String(), nullable=False),
        Column('url', String(), nullable=True),
        Column('size', Integer(), nullable=True),
        Column('update_date', Date(), nullable=False),
        Column('type', ImportType, nullable=False),

        PrimaryKeyConstraint('id', name=op.f('pk__imports')),
        ForeignKeyConstraint(('parent_id', ), ['parents.id'],
                             name=op.f('fk__imports__parent_id__parents'))
    )
    op.create_index(op.f('ix__imports__update_date'), 'imports', ['update_date'],
                    unique=False)

    op.create_table(
        'import_history',
        Column('id', Integer(), nullable=False),
        Column('import_id', String(), nullable=False),
        Column('update_date', Date(), nullable=False),

        PrimaryKeyConstraint('id', name=op.f('pk__import_history')),
        ForeignKeyConstraint(('import_id', ), ['imports.id'],
            name=op.f('fk__import_history__import_id__imports')),
    )
    op.create_index(op.f('ix__import_history__update_date'), 'import_history', ['update_date'],
                    unique=False)


def downgrade():
    op.drop_table('parents_table')
    op.drop_table('imports')
    op.drop_table('import_history')
    ImportType.drop(op.get_bind(), checkfirst=False)
