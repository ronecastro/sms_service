"""empty message

Revision ID: 3698ca6e4a22
Revises: 
Create Date: 2022-04-19 14:54:29.622275

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3698ca6e4a22'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rules',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rule', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    op.create_table('notifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('expiration', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('pv', sa.String(), nullable=True),
    sa.Column('rule_id', sa.String(), nullable=True),
    sa.Column('limit', sa.String(), nullable=True),
    sa.Column('subrule', sa.String(), nullable=True),
    sa.Column('last_sent', sa.DateTime(), nullable=True),
    sa.Column('interval', sa.Integer(), nullable=True),
    sa.Column('persistent', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['rule_id'], ['rules.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notifications')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    op.drop_table('rules')
    # ### end Alembic commands ###
