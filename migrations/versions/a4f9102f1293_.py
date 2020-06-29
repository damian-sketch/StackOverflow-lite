"""empty message

Revision ID: a4f9102f1293
Revises: 
Create Date: 2020-06-24 06:48:29.140808

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4f9102f1293'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'comment', 'post', ['post_id'], ['id'])
    op.add_column('user', sa.Column('sent_on', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'sent_on')
    op.drop_constraint(None, 'comment', type_='foreignkey')
    # ### end Alembic commands ###