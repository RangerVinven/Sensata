"""Add session_token row.

Revision ID: 53ba04d9c52a
Revises: 0f33bd639aa7
Create Date: 2024-11-06 19:28:28.405878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '53ba04d9c52a'
down_revision: Union[str, None] = '0f33bd639aa7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_session', sa.Column('session_token', sa.Uuid(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_session', 'session_token')
    # ### end Alembic commands ###