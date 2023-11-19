"""Initial migration

Revision ID: a3f5a8aa25fe
Revises: 
Create Date: 2023-11-19 09:07:05.628153

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3f5a8aa25fe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('maintenance',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.Column('assigned_employees', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('train',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('position', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('wagon',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('track_width', sa.Integer(), nullable=False),
    sa.Column('wagon_type', sa.String(length=20), nullable=True),
    sa.Column('train_id', sa.Integer(), nullable=True),
    sa.Column('max_traction', sa.Float(), nullable=False),
    sa.Column('max_weight', sa.Float(), nullable=False),
    sa.Column('number_of_seats', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['train_id'], ['train.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wagon')
    op.drop_table('train')
    op.drop_table('maintenance')
    # ### end Alembic commands ###
