"""Section table

Revision ID: 7586aa9285e7
Revises: 1d9f43ddcb4c
Create Date: 2023-11-07 11:26:44.852064

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7586aa9285e7'
down_revision = '1d9f43ddcb4c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('section',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('startStation', sa.Integer(), nullable=True),
    sa.Column('endStation', sa.Integer(), nullable=True),
    sa.Column('fee', sa.Float(), nullable=True),
    sa.Column('distance', sa.Float(), nullable=True),
    sa.Column('maxSpeed', sa.Integer(), nullable=True),
    sa.Column('trackWidth', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['endStation'], ['station.id'], ),
    sa.ForeignKeyConstraint(['startStation'], ['station.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('section')
    # ### end Alembic commands ###