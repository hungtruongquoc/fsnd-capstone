"""empty message

Revision ID: 9f8e7197eb3b
Revises: cd92db73ab1f
Create Date: 2021-01-03 17:15:04.419637

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9f8e7197eb3b'
down_revision = 'cd92db73ab1f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Actors')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Actors',
                    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Actors_id_seq"\'::regclass)'),
                              autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('age', sa.SMALLINT(), autoincrement=False, nullable=True),
                    sa.Column('gender', postgresql.ENUM('one', 'two', 'three', name='genderenum'), autoincrement=False,
                              nullable=True),
                    sa.PrimaryKeyConstraint('id', name='Actors_pkey')
                    )
    # ### end Alembic commands ###
