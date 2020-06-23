"""empty message

Revision ID: 82352504251d
Revises:
Create Date: 2020-06-21 16:52:46.263651

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82352504251d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment') as batch_op:
        batch_op.alter_column( 'post_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_foreign_key(None, 'comment', 'post', ['post_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'comment', type_='foreignkey')
    op.alter_column('comment', 'post_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###