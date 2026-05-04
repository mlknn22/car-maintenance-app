"""relationships, ondelete cascade, car.user_id FK NOT NULL

Revision ID: 401ca60eef58
Revises: fec1d6cad09c
Create Date: 2026-05-04 21:41:50.369553

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '401ca60eef58'
down_revision: Union[str, Sequence[str], None] = 'fec1d6cad09c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # cars.user_id becomes NOT NULL with FK on users.id; existing dev rows
    # have user_id IS NULL and there are no users yet, so TRUNCATE is the
    # cleanest path. CASCADE drops dependent rows in devices, alerts,
    # maintenance_records and (transitively) telemetry_logs.
    op.execute("TRUNCATE TABLE cars CASCADE")

    op.drop_constraint(op.f('alerts_car_id_fkey'), 'alerts', type_='foreignkey')
    op.create_foreign_key(
        'alerts_car_id_fkey', 'alerts', 'cars',
        ['car_id'], ['id'], ondelete='CASCADE',
    )

    op.alter_column('cars', 'user_id', existing_type=sa.INTEGER(), nullable=False)
    op.create_foreign_key(
        'cars_user_id_fkey', 'cars', 'users',
        ['user_id'], ['id'], ondelete='CASCADE',
    )

    op.drop_constraint(op.f('devices_car_id_fkey'), 'devices', type_='foreignkey')
    op.create_foreign_key(
        'devices_car_id_fkey', 'devices', 'cars',
        ['car_id'], ['id'], ondelete='CASCADE',
    )

    op.create_index(
        op.f('ix_maintenance_records_car_id'),
        'maintenance_records', ['car_id'], unique=False,
    )
    op.drop_constraint(op.f('maintenance_records_car_id_fkey'), 'maintenance_records', type_='foreignkey')
    op.create_foreign_key(
        'maintenance_records_car_id_fkey', 'maintenance_records', 'cars',
        ['car_id'], ['id'], ondelete='CASCADE',
    )

    op.drop_constraint(op.f('telemetry_logs_device_id_fkey'), 'telemetry_logs', type_='foreignkey')
    op.create_foreign_key(
        'telemetry_logs_device_id_fkey', 'telemetry_logs', 'devices',
        ['device_id'], ['id'], ondelete='CASCADE',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('telemetry_logs_device_id_fkey', 'telemetry_logs', type_='foreignkey')
    op.create_foreign_key(
        'telemetry_logs_device_id_fkey', 'telemetry_logs', 'devices',
        ['device_id'], ['id'],
    )

    op.drop_constraint('maintenance_records_car_id_fkey', 'maintenance_records', type_='foreignkey')
    op.create_foreign_key(
        'maintenance_records_car_id_fkey', 'maintenance_records', 'cars',
        ['car_id'], ['id'],
    )
    op.drop_index(op.f('ix_maintenance_records_car_id'), table_name='maintenance_records')

    op.drop_constraint('devices_car_id_fkey', 'devices', type_='foreignkey')
    op.create_foreign_key(
        'devices_car_id_fkey', 'devices', 'cars',
        ['car_id'], ['id'],
    )

    op.drop_constraint('cars_user_id_fkey', 'cars', type_='foreignkey')
    op.alter_column('cars', 'user_id', existing_type=sa.INTEGER(), nullable=True)

    op.drop_constraint('alerts_car_id_fkey', 'alerts', type_='foreignkey')
    op.create_foreign_key(
        'alerts_car_id_fkey', 'alerts', 'cars',
        ['car_id'], ['id'],
    )
