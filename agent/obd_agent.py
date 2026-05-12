"""
OBD-агент: читает PID-ы с ELM327 и POST-ит на сервер.

Запуск перед поездкой (ноут/телефон в машине рядом с адаптером):
    python agent/obd_agent.py \\
        --base-url http://127.0.0.1:8000 \\
        --token "$TOKEN" \\
        --device-id 1 \\
        --port "socket://192.168.0.10:35000" \\
        --interval 5

Адаптер автодетектится, если --port не задан (для USB/Bluetooth-вариантов).
Для тестов без машины: --mock — генерируется правдоподобная «обычная поездка»
со старта (rpm/coolant прогреваются), сетевой пайплайн отрабатывается полностью.
"""

from __future__ import annotations

import argparse
import os
import random
import signal
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone

import requests


for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except Exception:
        pass


# PID-ы → ключи payload'а телеметрии. Импорт obd ленивый (когда не --mock).
PID_MAP = {
    "RPM": "rpm",
    "COOLANT_TEMP": "coolant_temp",
    "CONTROL_MODULE_VOLTAGE": "battery_voltage",
    "SPEED": "speed",
    "ENGINE_LOAD": "engine_load",
}


@dataclass
class AgentConfig:
    base_url: str
    token: str
    device_id: int
    port: str | None
    interval: int
    mock: bool


def parse_args() -> AgentConfig:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--base-url", default=os.environ.get("CRMA_BASE_URL", "http://127.0.0.1:8000"))
    p.add_argument("--token", default=os.environ.get("CRMA_TOKEN"),
                   help="JWT access token. Можно через env CRMA_TOKEN.")
    p.add_argument("--device-id", type=int, required=True)
    p.add_argument("--port", default=None,
                   help="Порт ELM327 (например, socket://IP:PORT, COM3, /dev/rfcomm0). "
                        "Если не задан — автодетект python-OBD.")
    p.add_argument("--interval", type=int, default=5, help="Период опроса в секундах")
    p.add_argument("--mock", action="store_true",
                   help="Не подключаться к адаптеру, генерить фейковые значения.")
    args = p.parse_args()

    if not args.token:
        p.error("--token is required (or set CRMA_TOKEN env var)")
    if args.interval < 1:
        p.error("--interval must be >= 1")

    return AgentConfig(
        base_url=args.base_url.rstrip("/"),
        token=args.token,
        device_id=args.device_id,
        port=args.port,
        interval=args.interval,
        mock=args.mock,
    )


class OBDReader:
    """Тонкая обёртка над python-OBD. Возвращает значения PID-ов как Python-float."""

    def __init__(self, port: str | None):
        import obd  
        self._obd = obd
        print(f"Подключаюсь к ELM327 (port={port or 'auto-detect'})...")
        self.connection = obd.OBD(port) if port else obd.OBD()
        if not self.connection.is_connected():
            raise SystemExit(
                "Не удалось подключиться к адаптеру. Проверь питание/спаривание/IP."
            )
        print(f"Подключено. Статус: {self.connection.status()}")

    def read(self) -> dict[str, float | None]:
        out: dict[str, float | None] = {}
        for pid_name, payload_key in PID_MAP.items():
            cmd = getattr(self._obd.commands, pid_name, None)
            if cmd is None:
                out[payload_key] = None
                continue
            resp = self.connection.query(cmd)
            if resp.is_null() or resp.value is None:
                out[payload_key] = None
                continue
            
            try:
                out[payload_key] = float(resp.value.magnitude)
            except AttributeError:
                out[payload_key] = float(resp.value)
        return out

    def close(self) -> None:
        try:
            self.connection.close()
        except Exception:
            pass


class MockReader:
    """Имитирует поездку: прогрев, потом крейсер. Без аномалий."""

    def __init__(self) -> None:
        self.started = time.monotonic()

    def read(self) -> dict[str, float | None]:
        elapsed = time.monotonic() - self.started
        if elapsed < 60:  # «прогрев» сжат до 1 минуты
            coolant = 30 + (90 - 30) * (elapsed / 60) + random.uniform(-1, 1)
            rpm = 700 + random.uniform(-50, 250)
            speed = random.uniform(0, 25)
            load = random.uniform(15, 35)
        else:
            coolant = 90 + random.uniform(-3, 3)
            rpm = random.uniform(1500, 3000)
            speed = random.uniform(40, 85)
            load = random.uniform(25, 55)
        return {
            "coolant_temp": round(coolant, 1),
            "rpm": round(rpm),
            "battery_voltage": round(13.9 + random.uniform(-0.2, 0.3), 2),
            "speed": round(speed, 1),
            "engine_load": round(load, 1),
        }

    def close(self) -> None:
        pass


def post_log(session: requests.Session, cfg: AgentConfig, payload: dict) -> bool:
    url = f"{cfg.base_url}/telemetry-logs/"
    try:
        r = session.post(url, json=payload, timeout=10)
    except requests.RequestException as e:
        print(f"  network error: {e}", file=sys.stderr)
        return False
    if r.status_code == 201:
        return True
    if 400 <= r.status_code < 500:
        print(f"  HTTP {r.status_code}: {r.text[:200]}", file=sys.stderr)
        print("  4xx — конфигурационная ошибка, останавливаюсь.", file=sys.stderr)
        raise SystemExit(1)
    print(f"  HTTP {r.status_code}: {r.text[:200]}", file=sys.stderr)
    return False


_STOP = False


def _handle_sigint(_signum, _frame) -> None:
    global _STOP
    _STOP = True
    print("\nПолучен SIGINT, завершаю цикл...")


def run(cfg: AgentConfig) -> None:
    signal.signal(signal.SIGINT, _handle_sigint)

    reader: OBDReader | MockReader
    if cfg.mock:
        print("Режим --mock: реальный OBD не используется.")
        reader = MockReader()
    else:
        reader = OBDReader(cfg.port)

    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {cfg.token}"

    print(f"Поехали: device_id={cfg.device_id}, interval={cfg.interval}s, base_url={cfg.base_url}")
    print("Ctrl+C — остановить.\n")

    sent = 0
    try:
        while not _STOP:
            tick_start = time.monotonic()
            readings = reader.read()
            payload = {"device_id": cfg.device_id, **readings}
            ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
            short = ", ".join(
                f"{k}={v}" for k, v in readings.items() if v is not None
            ) or "(no values)"
            print(f"[{ts}] {short}")
            ok = post_log(session, cfg, payload)
            sent += int(ok)
            elapsed = time.monotonic() - tick_start
            sleep_for = max(cfg.interval - elapsed, 0)
            if _STOP:
                break
            time.sleep(sleep_for)
    finally:
        reader.close()
        print(f"\nОтправлено логов: {sent}")


if __name__ == "__main__":
    run(parse_args())
