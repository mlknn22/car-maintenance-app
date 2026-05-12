from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.thresholds import DEFAULT_THRESHOLDS, Thresholds
from app.models.alert import Alert
from app.models.telemetry_log import TelemetryLog


SEVERITY_RANK = {"info": 0, "warning": 1, "critical": 2}


def _engine_running(log: TelemetryLog, thresholds: Thresholds) -> bool | None:
    if log.rpm is None:
        return None
    return log.rpm > thresholds.engine_running_rpm


def check_thresholds(
    log: TelemetryLog,
    car_id: int,
    now: datetime | None = None,
    thresholds: Thresholds = DEFAULT_THRESHOLDS,
) -> list[Alert]:
    if now is None:
        now = datetime.now(timezone.utc)
    alerts: list[Alert] = []

    if log.coolant_temp is not None:
        if log.coolant_temp > thresholds.coolant_crit:
            alerts.append(Alert(
                car_id=car_id,
                type="coolant_high",
                severity="critical",
                message=f"Критический перегрев двигателя: {log.coolant_temp:.1f} °C",
                timestamp=now,
            ))
        elif log.coolant_temp > thresholds.coolant_warn:
            alerts.append(Alert(
                car_id=car_id,
                type="coolant_high",
                severity="warning",
                message=f"Высокая температура двигателя: {log.coolant_temp:.1f} °C",
                timestamp=now,
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
                    timestamp=now,
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
                    timestamp=now,
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
                    timestamp=now,
                ))
            elif log.battery_voltage < thresholds.battery_idle_warn:
                alerts.append(Alert(
                    car_id=car_id,
                    type="battery_low_idle",
                    severity="warning",
                    message=f"Пониженное напряжение АКБ в покое: {log.battery_voltage:.2f} В",
                    timestamp=now,
                ))

    if log.rpm is not None and log.rpm > thresholds.overrev_crit:
        alerts.append(Alert(
            car_id=car_id,
            type="overrev",
            severity="critical",
            message=f"Превышение оборотов: {log.rpm:.0f} RPM",
            timestamp=now,
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
            timestamp=now,
        ))

    return alerts


def current_violation_types(
    log: TelemetryLog,
    thresholds: Thresholds = DEFAULT_THRESHOLDS,
) -> dict[str, bool | None]:
    """
    Возвращает словарь {alert_type: violation_state} для каждого типа алерта,
    который умеет производить check_thresholds.

    Значения:
      - True  — сейчас в нарушении (новый алерт уместен)
      - False — сейчас в норме (active алерт этого типа можно резолвить)
      - None  — недостаточно данных (active алерт трогать нельзя)
    """
    result: dict[str, bool | None] = {}

    if log.coolant_temp is None:
        result["coolant_high"] = None
    else:
        result["coolant_high"] = log.coolant_temp > thresholds.coolant_warn

    running = _engine_running(log, thresholds)
    if log.battery_voltage is None or running is None:
        result["battery_low_running"] = None
        result["battery_low_idle"] = None
    elif running:
        result["battery_low_running"] = log.battery_voltage < thresholds.battery_running_warn
        result["battery_low_idle"] = False
    else:
        result["battery_low_running"] = False
        result["battery_low_idle"] = log.battery_voltage < thresholds.battery_idle_warn

    if log.rpm is None:
        result["overrev"] = None
    else:
        result["overrev"] = log.rpm > thresholds.overrev_crit

    if log.rpm is None or log.coolant_temp is None:
        result["cold_revving"] = None
    else:
        result["cold_revving"] = (
            log.rpm > thresholds.cold_rev_rpm
            and log.coolant_temp < thresholds.cold_rev_coolant_max
        )

    return result


async def resolve_recovered_alerts(
    db: AsyncSession,
    log: TelemetryLog,
    car_id: int,
    now: datetime | None = None,
    thresholds: Thresholds = DEFAULT_THRESHOLDS,
) -> int:
    if now is None:
        now = datetime.now(timezone.utc)
    violations = current_violation_types(log, thresholds)
    recovered_types = [t for t, v in violations.items() if v is False]
    if not recovered_types:
        return 0

    stmt = (
        update(Alert)
        .where(
            Alert.car_id == car_id,
            Alert.type.in_(recovered_types),
            Alert.resolved_at.is_(None),
        )
        .values(resolved_at=now)
        .execution_options(synchronize_session=False)
    )
    result = await db.execute(stmt)
    return result.rowcount


async def merge_with_active_state(
    db: AsyncSession,
    candidates: list[Alert],
    now: datetime | None = None,
) -> list[Alert]:
    if not candidates:
        return []
    if now is None:
        now = datetime.now(timezone.utc)

    fresh: list[Alert] = []
    for candidate in candidates:
        stmt = (
            select(Alert)
            .where(
                Alert.car_id == candidate.car_id,
                Alert.type == candidate.type,
                Alert.resolved_at.is_(None),
            )
            .limit(1)
        )
        active = (await db.execute(stmt)).scalar_one_or_none()

        if active is None:
            fresh.append(candidate)
            continue

        if SEVERITY_RANK[candidate.severity] > SEVERITY_RANK[active.severity]:
            active.resolved_at = now
            fresh.append(candidate)
        # severity не повысилась → существующий active покрывает событие
    return fresh
