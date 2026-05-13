export type BodyType = "Truck" | "Van" | "Bus" | "Car" | "Motorcycle" | "SUV";
export type FuelType = "Electric" | "Petrol" | "Diesel";
export type Transmission = "Automatic" | "Manual";
export type BrakeCondition = "New" | "Good" | "Worn Out";
export type OwnerType = "First" | "Second" | "Third";
export type Severity = "info" | "warning" | "critical";

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  created_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  full_name?: string | null;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface CarInput {
  brand: string;
  model: string;
  year: number;
  mileage: number;
  body_type: BodyType;
  fuel_type: FuelType;
  transmission: Transmission;
  engine_size: number;
  brake_condition: BrakeCondition;
  owner_type: OwnerType;
}

export interface Car extends CarInput {
  id: number;
  user_id: number;
  risk_score: number | null;
}

export interface RiskScoreResponse {
  car_id: number;
  risk_score: number;
  model_name: string;
  computed_at: string;
}

export interface DeviceInput {
  car_id: number;
  device_name: string;
}

export interface Device extends DeviceInput {
  id: number;
  connected: boolean;
  last_seen: string | null;
  created_at: string;
}

export interface DeviceCreated extends Device {
  api_token: string;
}

export interface DeviceTokenResponse {
  api_token: string;
}

export interface MaintenanceRecordInput {
  car_id: number;
  service_date: string;
  work_type: string;
  cost: number;
  mileage_at_service: number;
  notes?: string | null;
}

export interface MaintenanceRecord extends MaintenanceRecordInput {
  id: number;
  created_at: string;
}

export interface Alert {
  id: number;
  car_id: number;
  type: string;
  message: string;
  severity: Severity;
  is_read: boolean;
  timestamp: string;
  resolved_at: string | null;
}

export interface TelemetryLog {
  id: number;
  device_id: number;
  timestamp: string;
  coolant_temp: number | null;
  rpm: number | null;
  battery_voltage: number | null;
  speed: number | null;
  engine_load: number | null;
}
