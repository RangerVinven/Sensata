"""Remove nullability on time_added.

Revision ID: 0f33bd639aa7
Revises: 15dab0de5718
Create Date: 2024-10-30 19:32:45.499657

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0f33bd639aa7'
down_revision: Union[str, None] = '15dab0de5718'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('sensor_data', 'time_added',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('sensor_data', 'unique_id',
               existing_type=sa.UUID(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('sensor_data', 'unique_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('sensor_data', 'time_added',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    # ### end Alembic commands ###
