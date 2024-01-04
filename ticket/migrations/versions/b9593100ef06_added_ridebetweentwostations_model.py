"""Added RideBetweenTwoStations model

Revision ID: b9593100ef06
Revises: b729b621efc6
Create Date: 2024-01-04 23:23:58.802469

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9593100ef06'
down_revision = 'b729b621efc6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ride_between_two_stations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('start_station_id', sa.Integer(), nullable=False),
    sa.Column('end_station_id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['end_station_id'], ['station.id'], ),
    sa.ForeignKeyConstraint(['start_station_id'], ['station.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ride_between_two_stations')
    # ### end Alembic commands ###