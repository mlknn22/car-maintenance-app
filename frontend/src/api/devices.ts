import type {
  Device,
  DeviceCreated,
  DeviceInput,
  DeviceTokenResponse,
} from "../types";
import { apiRequest } from "./client";

export function listDevicesByCar(carId: number): Promise<Device[]> {
  return apiRequest<Device[]>(`/devices/car/${carId}`);
}

export function createDevice(payload: DeviceInput): Promise<DeviceCreated> {
  return apiRequest<DeviceCreated>("/devices/", { method: "POST", body: payload });
}

export function regenerateDeviceToken(id: number): Promise<DeviceTokenResponse> {
  return apiRequest<DeviceTokenResponse>(`/devices/${id}/regenerate-token`, {
    method: "POST",
  });
}

export function deleteDevice(id: number): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/devices/${id}`, { method: "DELETE" });
}
