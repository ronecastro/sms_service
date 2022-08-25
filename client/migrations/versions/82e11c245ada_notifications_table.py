"""notifications table

Revision ID: 82e11c245ada
Revises: 3698ca6e4a22
Create Date: 2022-05-24 15:21:47.308544

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82e11c245ada'
down_revision = '3698ca6e4a22'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notifications', schema=None) as batch_op:
        batch_op.add_column(sa.Column('notification', sa.String(), nullable=True))
        batch_op.drop_column('limit')
        batch_op.drop_column('interval')
        batch_op.drop_column('persistent')
        batch_op.drop_column('pv')
        batch_op.drop_column('expiration')
        batch_op.drop_column('created')
        batch_op.drop_column('subrule')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notifications', schema=None) as batch_op:
        batch_op.add_column(sa.Column('subrule', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('created', sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column('expiration', sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column('pv', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('persistent', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('interval', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('limit', sa.VARCHAR(), nullable=True))
        batch_op.drop_column('notification')

    # ### end Alembic commands ###
