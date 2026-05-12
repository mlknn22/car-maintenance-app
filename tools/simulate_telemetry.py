"""
Симулятор телеметрии: бэкфилит историю поездок через POST /telemetry-logs/.

Каждый POST уносит собственный `timestamp` (UTC, tz-aware), сервер записывает
лог и алерты строго с этой меткой — телеметрия и история алертов выходят
согласованными во времени.

Сценарии:
    normal             — обычная езда (прогрев → крейсер). Аномалий нет.
    dying_alternator   — напряжение бортсети плавно деградирует с 13.5В до 11.0В
                         по ходу окна симуляции → battery_low_running warn→crit.
    summer_overheat    — со второй трети поездки coolant ползёт 90→115°C →
                         coolant_high warn→crit.
    cold_revving       — короткие поездки с агрессивными оборотами на холодную
                         (rpm > 3500 при coolant < 60) → cold_revving warning.
    all                — циклически чередует все четыре по дням.

Пример:
    python tools/simulate_telemetry.py \\
        --base-url http://127.0.0.1:8000 \\
        --token "$TOKEN" \\
        --device-id 1 \\
        --scenario dying_alternator \\
        --days 3 \\
        --trips-per-day 2 \\
        --step-seconds 10
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import requests


for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except Exception:
        pass


SCENARIOS = ("normal", "dying_alternator", "summer_overheat", "cold_revving", "all")
ROTATION = ("normal", "cold_revving", "summer_overheat", "dying_alternator")


@dataclass(frozen=True)
class SimConfig:
    base_url: str
    token: str
    device_id: int
    scenario: str
    days: int
    trips_per_day: int
    step_seconds: int
    start: datetime
    end: datetime
    seed: int | None
    dry_run: bool


def parse_args() -> SimConfig:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--base-url", default=os.environ.get("CRMA_BASE_URL", "http://127.0.0.1:8000"))
    p.add_argument("--token", default=os.environ.get("CRMA_TOKEN"),
                   help="JWT access token. Можно через env CRMA_TOKEN.")
    p.add_argument("--device-id", type=int, required=True)
    p.add_argument("--scenario", choices=SCENARIOS, default="normal")
    p.add_argument("--days", type=int, default=1, help="Дней истории заканчивая 'сейчас'")
    p.add_argument("--trips-per-day", type=int, default=2)
    p.add_argument("--step-seconds", type=int, default=10, help="Шаг семплирования в сим-времени")
    p.add_argument("--end", type=str, default=None,
                   help="ISO datetime конца окна (UTC). По умолчанию — текущий момент.")
    p.add_argument("--seed", type=int, default=None, help="seed для воспроизводимости")
    p.add_argument("--dry-run", action="store_true", help="Не отправлять, только вывести количество логов")
    args = p.parse_args()

    if not args.token and not args.dry_run:
        p.error("--token is required (or set CRMA_TOKEN env var)")
    if args.days < 1:
        p.error("--days must be >= 1")
    if args.trips_per_day < 1:
        p.error("--trips-per-day must be >= 1")
    if args.step_seconds < 1:
        p.error("--step-seconds must be >= 1")

    end = (
        datetime.fromisoformat(args.end).astimezone(timezone.utc)
        if args.end
        else datetime.now(timezone.utc)
    )
    start = end - timedelta(days=args.days)
    return SimConfig(
        base_url=args.base_url.rstrip("/"),
        token=args.token or "",
        device_id=args.device_id,
        scenario=args.scenario,
        days=args.days,
        trips_per_day=args.trips_per_day,
        step_seconds=args.step_seconds,
        start=start,
        end=end,
        seed=args.seed,
        dry_run=args.dry_run,
    )


def _trip_windows(cfg: SimConfig) -> list[tuple[datetime, datetime, str]]:
    """
    Расписание поездок: для каждого дня — N равноотстоящих поездок.
    Возвращает [(trip_start, trip_end, scenario_for_trip), ...]
    """
    windows: list[tuple[datetime, datetime, str]] = []
    day = cfg.start.replace(hour=0, minute=0, second=0, microsecond=0)
    while day < cfg.end:
        for i in range(cfg.trips_per_day):
            hour = 8 + int(i * (12 / cfg.trips_per_day))  # 08:00, 14:00, 20:00...
            minute = random.randint(0, 30)
            t0 = day.replace(hour=hour, minute=minute)
            scenario = _resolve_scenario(cfg.scenario, (day - cfg.start).days)
            duration_min = (
                random.randint(10, 18) if scenario == "cold_revving"
                else random.randint(25, 45)
            )
            t1 = t0 + timedelta(minutes=duration_min)
            if t1 <= cfg.start or t0 >= cfg.end:
                continue
            t0 = max(t0, cfg.start)
            t1 = min(t1, cfg.end)
            windows.append((t0, t1, scenario))
        day += timedelta(days=1)
    return windows


def _resolve_scenario(scenario: str, day_index: int) -> str:
    if scenario == "all":
        return ROTATION[day_index % len(ROTATION)]
    return scenario


def make_log(
    scenario: str,
    t: datetime,
    trip_start: datetime,
    trip_end: datetime,
    sim_start: datetime,
    sim_end: datetime,
) -> dict:
    elapsed = (t - trip_start).total_seconds()
    duration = max((trip_end - trip_start).total_seconds(), 1.0)
    trip_progress = elapsed / duration
    sim_progress = (t - sim_start).total_seconds() / max((sim_end - sim_start).total_seconds(), 1.0)

    # Базовая "нормальная" езда
    if elapsed < 300:  # warmup 5 минут
        coolant = 30 + (90 - 30) * (elapsed / 300) + random.uniform(-1.5, 1.5)
        rpm = 700 + random.uniform(-50, 250)
        speed = random.uniform(0, 30)
        load = random.uniform(15, 40)
    else:
        coolant = 90 + random.uniform(-3, 4)
        rpm = random.uniform(1500, 3300)
        speed = random.uniform(40, 95)
        load = random.uniform(25, 60)
    battery = 13.9 + random.uniform(-0.2, 0.4)

    # Сценарные оверлеи
    if scenario == "dying_alternator":
        # Линейная деградация по всему окну симуляции
        battery = 13.5 - 2.6 * sim_progress + random.uniform(-0.15, 0.15)
    elif scenario == "summer_overheat":
        # После прогрева и середины поездки coolant ползёт вверх
        if elapsed >= 300 and trip_progress > 0.4:
            climb = (trip_progress - 0.4) / 0.6  # 0..1
            coolant = 92 + climb * 25 + random.uniform(-1, 1)  # 92..117
    elif scenario == "cold_revving":
        # Первые 2 минуты — короткие "выстрелы" оборотов на холодную
        if elapsed < 120 and random.random() < 0.6:
            rpm = random.uniform(3200, 4100)
            speed = random.uniform(0, 15)
            load = random.uniform(45, 75)
            # coolant остаётся низким (warmup только начат)
            coolant = 30 + (55 - 30) * (elapsed / 120) + random.uniform(-1, 1)

    return {
        "device_id": 0,  # подставится из cfg
        "timestamp": t.isoformat(),
        "coolant_temp": round(coolant, 1),
        "rpm": round(rpm),
        "battery_voltage": round(battery, 2),
        "speed": round(speed, 1),
        "engine_load": round(load, 1),
    }


def post_log(session: requests.Session, cfg: SimConfig, payload: dict) -> None:
    payload = {**payload, "device_id": cfg.device_id}
    url = f"{cfg.base_url}/telemetry-logs/"
    for attempt in range(4):
        try:
            r = session.post(url, json=payload, timeout=10)
            if r.status_code == 201:
                return
            if 400 <= r.status_code < 500:
                raise SystemExit(
                    f"HTTP {r.status_code} on {url}: {r.text}\n"
                    f"payload={payload}\n"
                    "Конфигурационная ошибка (токен/устройство/схема). Останавливаюсь."
                )
            print(f"warn: HTTP {r.status_code} attempt {attempt + 1}: {r.text[:200]}",
                  file=sys.stderr)
        except requests.RequestException as e:
            print(f"warn: network error attempt {attempt + 1}: {e}", file=sys.stderr)
        time.sleep(0.5 * (2 ** attempt))
    raise SystemExit(f"Дали 4 попытки, всё легло. Останавливаюсь.")


def run(cfg: SimConfig) -> None:
    if cfg.seed is not None:
        random.seed(cfg.seed)

    windows = _trip_windows(cfg)
    if not windows:
        raise SystemExit("Пустое окно симуляции — нечего отправлять.")

    total_logs = sum(
        max(int((t1 - t0).total_seconds() // cfg.step_seconds), 1)
        for t0, t1, _ in windows
    )
    print(f"Сценарий: {cfg.scenario}")
    print(f"Окно: {cfg.start.isoformat()} → {cfg.end.isoformat()}")
    print(f"Поездок: {len(windows)}, логов всего: {total_logs}, шаг: {cfg.step_seconds}s")
    print(f"device_id={cfg.device_id}, base_url={cfg.base_url}")
    if cfg.dry_run:
        print("[dry-run] выход без отправки.")
        return

    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {cfg.token}"

    sent = 0
    started = time.monotonic()
    for trip_idx, (t0, t1, scen) in enumerate(windows, 1):
        print(f"[{trip_idx}/{len(windows)}] {scen}: "
              f"{t0.isoformat()} → {t1.isoformat()}")
        t = t0
        while t < t1:
            payload = make_log(scen, t, t0, t1, cfg.start, cfg.end)
            post_log(session, cfg, payload)
            sent += 1
            if sent % 100 == 0:
                elapsed = time.monotonic() - started
                rate = sent / elapsed if elapsed else 0
                print(f"    ... отправлено {sent}/{total_logs} ({rate:.0f} log/s)")
            t += timedelta(seconds=cfg.step_seconds)

    elapsed = time.monotonic() - started
    print(f"Готово: {sent} логов за {elapsed:.1f}s "
          f"({sent / elapsed:.0f} log/s).")


if __name__ == "__main__":
    run(parse_args())
