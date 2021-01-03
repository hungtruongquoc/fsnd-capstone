"""empty message

Revision ID: 70561a5b2703
Revises: 9f8e7197eb3b
Create Date: 2021-01-03 17:29:41.266124

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70561a5b2703'
down_revision = '9f8e7197eb3b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Actors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('age', sa.SmallInteger(), nullable=True),
    sa.Column('gender', sa.Enum('Male', 'Female', 'Unspecified', name='genderenum'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Actors')
    # ### end Alembic commands ###