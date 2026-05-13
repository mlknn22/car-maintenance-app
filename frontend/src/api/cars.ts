import type { Car, CarInput, RiskScoreResponse } from "../types";
import { apiRequest } from "./client";

export function listCars(): Promise<Car[]> {
  return apiRequest<Car[]>("/cars/");
}

export function getCar(id: number): Promise<Car> {
  return apiRequest<Car>(`/cars/${id}`);
}

export function createCar(payload: CarInput): Promise<Car> {
  return apiRequest<Car>("/cars/", { method: "POST", body: payload });
}

export function updateCar(id: number, payload: Partial<CarInput>): Promise<Car> {
  return apiRequest<Car>(`/cars/${id}`, { method: "PATCH", body: payload });
}

export function deleteCar(id: number): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/cars/${id}`, { method: "DELETE" });
}

export function getRiskScore(id: number): Promise<RiskScoreResponse> {
  return apiRequest<RiskScoreResponse>(`/cars/${id}/risk-score`);
}
