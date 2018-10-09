"""add_POst.body_html

Revision ID: 4dfdf09dc5ce
Revises: 00e6f6f1c05d
Create Date: 2018-10-09 23:17:44.580375

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4dfdf09dc5ce'
down_revision = '00e6f6f1c05d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('body_html', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('body_html')

    # ### end Alembic commands ###