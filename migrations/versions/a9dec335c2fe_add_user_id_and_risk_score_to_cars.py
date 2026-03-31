"""add user_id and risk_score to cars

Revision ID: a9dec335c2fe
Revises: 411173f32a8a
Create Date: 2026-03-31 14:04:17.268681

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9dec335c2fe'
down_revision: Union[str, Sequence[str], None] = '411173f32a8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('cars', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('cars', sa.Column('risk_score', sa.Float(), nullable=True))
    op.create_index(op.f('ix_cars_user_id'), 'cars', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_cars_user_id'), table_name='cars')
    op.drop_column('cars', 'risk_score')
    op.drop_column('cars', 'user_id')
