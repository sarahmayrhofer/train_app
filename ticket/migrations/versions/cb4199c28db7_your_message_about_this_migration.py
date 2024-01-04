"""Your message about this migration

Revision ID: cb4199c28db7
Revises: 01d3240780ab
Create Date: 2024-01-04 20:25:05.142911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb4199c28db7'
down_revision = '01d3240780ab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('fahrtdurchführung',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('datum', sa.Date(), nullable=False),
    sa.Column('zeit', sa.Time(), nullable=True),
    sa.Column('endzeit', sa.Time(), nullable=True),
    sa.Column('zug_id', sa.Integer(), nullable=True),
    sa.Column('line', sa.Integer(), nullable=True),
    sa.Column('mitarbeiter_ids', sa.String(), nullable=True),
    sa.Column('preise', sa.String(), nullable=True),
    sa.Column('bahnhof_ids', sa.String(), nullable=True),
    sa.Column('zeiten', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('streckenhalteplan',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('start_station_id', sa.Integer(), nullable=True),
    sa.Column('end_station_id', sa.Integer(), nullable=True),
    sa.Column('original_line_id', sa.Integer(), nullable=True),
    sa.Column('travel_duration', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('train',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('position', sa.String(length=50), nullable=True),
    sa.Column('price_per_km', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('maintenance',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.Column('train_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['train_id'], ['train.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('wagon',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('track_width', sa.Integer(), nullable=False),
    sa.Column('wagon_type', sa.String(length=20), nullable=True),
    sa.Column('train_id', sa.Integer(), nullable=True),
    sa.Column('max_traction', sa.Float(), nullable=True),
    sa.Column('max_weight', sa.Float(), nullable=True),
    sa.Column('number_of_seats', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['train_id'], ['train.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('maintenance_user_association',
    sa.Column('maintenance_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['maintenance_id'], ['maintenance.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('maintenance_user_association')
    op.drop_table('wagon')
    op.drop_table('maintenance')
    op.drop_table('train')
    op.drop_table('streckenhalteplan')
    op.drop_table('fahrtdurchführung')
    # ### end Alembic commands ###