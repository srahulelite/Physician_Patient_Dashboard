"""Last Visit date automatd

Revision ID: 9c1def4a8bf4
Revises: 307e5833a64d
Create Date: 2023-05-16 20:20:45.396469

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c1def4a8bf4'
down_revision = '307e5833a64d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('patient', schema=None) as batch_op:
        batch_op.alter_column('last_visit_date',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('patient', schema=None) as batch_op:
        batch_op.alter_column('last_visit_date',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)

    # ### end Alembic commands ###
