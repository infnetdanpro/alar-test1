"""empty message

Revision ID: 17368e2f9103
Revises: 
Create Date: 2019-09-08 05:31:16.448810

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17368e2f9103'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE SCHEMA alar')
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    schema='alar'
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('password', sa.String(length=32), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username'),
    schema='alar'
    )
    op.create_table('user_roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['alar.roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['alar.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id'),
    schema='alar'
    )
    # ### end Alembic commands ###
    op.execute("INSERT INTO alar.roles (name, level) VALUES ('guest', 2)")
    op.execute("INSERT INTO alar.roles (name, level) VALUES ('admin', 1)")


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_roles', schema='alar')
    op.drop_table('users', schema='alar')
    op.drop_table('roles', schema='alar')
    # ### end Alembic commands ###
    op.execute('DROP SCHEMA alar')
