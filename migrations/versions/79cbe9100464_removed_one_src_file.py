"""removed one src file

Revision ID: 79cbe9100464
Revises: 2ef8a797edfb
Create Date: 2017-11-18 05:36:41.635382

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79cbe9100464'
down_revision = '2ef8a797edfb'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('posts') as batch_op:
        # ### commands auto generated by Alembic - please adjust! ###
        batch_op.drop_column('tactic_url_1200px')
        batch_op.drop_column('tactic_pic_992px')
        batch_op.drop_column('tactic_url_lt768px')
        batch_op.drop_column('tactic_pic_lt768px')
        batch_op.drop_column('tactic_url_768px')
        batch_op.drop_column('tactic_url_992px')
        batch_op.drop_column('tactic_pic_1200px')
        batch_op.drop_column('tactic_pic_768px')
        batch_op.add_column(sa.Column('tactic_pic_1575px', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('tactic_pic_1750px', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('tactic_pic_875px', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('tactic_url_1575px', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('tactic_url_1750px', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('tactic_url_875px', sa.String(length=64), nullable=True))
        # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('tactic_pic_768px', sa.VARCHAR(length=64), nullable=True))
    op.add_column('posts', sa.Column('tactic_pic_1200px', sa.VARCHAR(length=64), nullable=True))
    op.add_column('posts', sa.Column('tactic_url_992px', sa.VARCHAR(length=64), nullable=True))
    op.add_column('posts', sa.Column('tactic_url_768px', sa.VARCHAR(length=64), nullable=True))
    op.add_column('posts', sa.Column('tactic_pic_lt768px', sa.VARCHAR(length=64), nullable=True))
    op.add_column('posts', sa.Column('tactic_url_lt768px', sa.VARCHAR(length=64), nullable=True))
    op.add_column('posts', sa.Column('tactic_pic_992px', sa.VARCHAR(length=64), nullable=True))
    op.add_column('posts', sa.Column('tactic_url_1200px', sa.VARCHAR(length=64), nullable=True))
    op.drop_column('posts', 'tactic_url_875px')
    op.drop_column('posts', 'tactic_url_1750px')
    op.drop_column('posts', 'tactic_url_1575px')
    op.drop_column('posts', 'tactic_pic_875px')
    op.drop_column('posts', 'tactic_pic_1750px')
    op.drop_column('posts', 'tactic_pic_1575px')
    # ### end Alembic commands ###