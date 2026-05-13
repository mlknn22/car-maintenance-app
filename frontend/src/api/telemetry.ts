import type { TelemetryLog } from "../types";
import { apiRequest } from "./client";

export function listTelemetryByCar(
  carId: number,
  limit = 100,
): Promise<TelemetryLog[]> {
  return apiRequest<TelemetryLog[]>(
    `/telemetry-logs/car/${carId}?limit=${limit}`,
  );
}

export function getLatestTelemetry(carId: number): Promise<TelemetryLog> {
  return apiRequest<TelemetryLog>(`/telemetry-logs/car/${carId}/latest`);
}
