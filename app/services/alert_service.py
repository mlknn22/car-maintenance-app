from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.thresholds import DEFAULT_THRESHOLDS, Thresholds
from app.models.alert import Alert
from app.models.telemetry_log import TelemetryLog


def _engine_running(log: TelemetryLog, thresholds: Thresholds) -> bool | None:
    if log.rpm is None:
        return None
    return log.rpm > thresholds.engine_running_rpm


def check_thresholds(
    log: TelemetryLog,
    car_id: int,
    thresholds: Thresholds = DEFAULT_THRESHOLDS,
) -> list[Alert]:
    alerts: list[Alert] = []

    if log.coolant_temp is not None:
        if log.coolant_temp > thresholds.coolant_crit:
            alerts.append(Alert(
                car_id=car_id,
                type="coolant_high",
                severity="critical",
                message=f"Критический перегрев двигателя: {log.coolant_temp:.1f} °C",
            ))
        elif log.coolant_temp > thresholds.coolant_warn:
            alerts.append(Alert(
                car_id=car_id,
                type="coolant_high",
                severity="warning",
                message=f"Высокая температура двигателя: {log.coolant_temp:.1f} °C",
            ))

    if log.battery_voltage is not None:
        running = _engine_running(log, thresholds)
        if running is True:
            if log.battery_voltage < thresholds.battery_running_crit:
                alerts.append(Alert(
                    car_id=car_id,
                    type="battery_low_running",
                    severity="critical",
                    message=(
                        f"Критически низкое напряжение бортсети при работающем "
                        f"двигателе: {log.battery_voltage:.2f} В "
                        f"(вероятна неисправность генератора)"
                    ),
                ))
            elif log.battery_voltage < thresholds.battery_running_warn:
                alerts.append(Alert(
                    car_id=car_id,
                    type="battery_low_running",
                    severity="warning",
                    message=(
                        f"Пониженное напряжение бортсети при работающем "
                        f"двигателе: {log.battery_voltage:.2f} В"
                    ),
                ))
        elif running is False:
            if log.battery_voltage < thresholds.battery_idle_crit:
                alerts.append(Alert(
                    car_id=car_id,
                    type="battery_low_idle",
                    severity="critical",
                    message=(
                        f"Критически низкое напряжение АКБ в покое: "
                        f"{log.battery_voltage:.2f} В (возможна глубокая разрядка)"
                    ),
                ))
            elif log.battery_voltage < thresholds.battery_idle_warn:
                alerts.append(Alert(
                    car_id=car_id,
                    type="battery_low_idle",
                    severity="warning",
                    message=f"Пониженное напряжение АКБ в покое: {log.battery_voltage:.2f} В",
                ))

    if log.rpm is not None and log.rpm > thresholds.overrev_crit:
        alerts.append(Alert(
            car_id=car_id,
            type="overrev",
            severity="critical",
            message=f"Превышение оборотов: {log.rpm:.0f} RPM",
        ))

    if (
        log.rpm is not None
        and log.coolant_temp is not None
        and log.rpm > thresholds.cold_rev_rpm
        and log.coolant_temp < thresholds.cold_rev_coolant_max
    ):
        alerts.append(Alert(
            car_id=car_id,
            type="cold_revving",
            severity="warning",
            message=(
                f"Высокие обороты на непрогретом двигателе: {log.rpm:.0f} RPM "
                f"при температуре охлаждающей жидкости {log.coolant_temp:.1f} °C"
            ),
        ))

    return alerts


async def filter_recent_duplicates(
    db: AsyncSession,
    candidates: list[Alert],
    window_seconds: int = 60,
) -> list[Alert]:
    if not candidates:
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(seconds=window_seconds)
    fresh: list[Alert] = []
    for alert in candidates:
        stmt = (
            select(Alert.id)
            .where(
                Alert.car_id == alert.car_id,
                Alert.type == alert.type,
                Alert.severity == alert.severity,
                Alert.is_read == False,
                Alert.timestamp >= cutoff,
            )
            .limit(1)
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing is None:
            fresh.append(alert)
    return fresh
