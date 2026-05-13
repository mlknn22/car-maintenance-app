import type { Alert } from "../types";
import { apiRequest } from "./client";

type AlertStatusFilter = "active" | "resolved" | "all";

export function listAlertsByCar(
  carId: number,
  status: AlertStatusFilter = "active",
): Promise<Alert[]> {
  return apiRequest<Alert[]>(
    `/alerts/?car_id=${carId}&status=${status}`,
  );
}

export function markAlertRead(id: number): Promise<Alert> {
  return apiRequest<Alert>(`/alerts/${id}/read`, { method: "PATCH" });
}

export function deleteAlert(id: number): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/alerts/${id}`, { method: "DELETE" });
}
