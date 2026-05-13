import type {
  BodyType,
  BrakeCondition,
  FuelType,
  OwnerType,
  Severity,
  Transmission,
} from "../types";

export const bodyTypeLabel: Record<BodyType, string> = {
  Car: "Легковой",
  SUV: "Кроссовер / внедорожник",
  Truck: "Грузовой",
  Van: "Микроавтобус",
  Bus: "Автобус",
  Motorcycle: "Мотоцикл",
};

export const fuelTypeLabel: Record<FuelType, string> = {
  Petrol: "Бензин",
  Diesel: "Дизель",
  Electric: "Электро",
};

export const transmissionLabel: Record<Transmission, string> = {
  Automatic: "Автомат",
  Manual: "Механика",
};

export const brakeConditionLabel: Record<BrakeCondition, string> = {
  New: "Новые",
  Good: "В норме",
  "Worn Out": "Изношены",
};

export const ownerTypeLabel: Record<OwnerType, string> = {
  First: "Первый владелец",
  Second: "Второй владелец",
  Third: "Третий и более",
};

export const severityLabel: Record<Severity, string> = {
  info: "Информация",
  warning: "Предупреждение",
  critical: "Критично",
};
