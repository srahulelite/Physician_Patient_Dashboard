"""Password Hash Migration

Revision ID: 8c25653d5a94
Revises: 
Create Date: 2023-05-15 13:10:00.061514

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c25653d5a94'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin',
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('role', sa.String(length=100), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('email')
    )
    op.create_table('stages',
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('client',
    sa.Column('case_id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('stage_name', sa.String(), nullable=False),
    sa.Column('admin_email', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['admin_email'], ['admin.email'], ),
    sa.ForeignKeyConstraint(['stage_name'], ['stages.name'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('case_id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('client')
    op.drop_table('stages')
    op.drop_table('admin')
    # ### end Alembic commands ###
