import type { MaintenanceRecord, MaintenanceRecordInput } from "../types";
import { apiRequest } from "./client";

export function listRecordsByCar(carId: number): Promise<MaintenanceRecord[]> {
  return apiRequest<MaintenanceRecord[]>(`/maintenance-records/?car_id=${carId}`);
}

export function createRecord(payload: MaintenanceRecordInput): Promise<MaintenanceRecord> {
  return apiRequest<MaintenanceRecord>("/maintenance-records/", {
    method: "POST",
    body: payload,
  });
}

export function deleteRecord(id: number): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/maintenance-records/${id}`, {
    method: "DELETE",
  });
}
