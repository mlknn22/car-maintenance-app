import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { ApiError } from "../api/client";
import { updateCar } from "../api/cars";
import {
  bodyTypeLabel,
  brakeConditionLabel,
  fuelTypeLabel,
  ownerTypeLabel,
  transmissionLabel,
} from "../lib/labels";
import type {
  BodyType,
  BrakeCondition,
  Car,
  CarInput,
  FuelType,
  OwnerType,
  Transmission,
} from "../types";
import { NumberField, SelectField, TextField } from "./FormFields";
import { Modal } from "./Modal";

interface CarEditModalProps {
  car: Car;
  open: boolean;
  onClose: () => void;
}

interface FieldErrors {
  brand?: string;
  model?: string;
  year?: string;
  mileage?: string;
  engine_size?: string;
}

export function CarEditModal({ car, open, onClose }: CarEditModalProps) {
  const queryClient = useQueryClient();

  const [form, setForm] = useState<CarInput>(() => carToInput(car));
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [serverError, setServerError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (data: Partial<CarInput>) => updateCar(car.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["car", car.id] });
      queryClient.invalidateQueries({ queryKey: ["cars"] });
      onClose();
    },
    onError: (err) => {
      setServerError(
        err instanceof ApiError ? err.message : "Не удалось сохранить",
      );
    },
  });

  function update<K extends keyof CarInput>(key: K, value: CarInput[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
    if ((fieldErrors as Record<string, unknown>)[key]) {
      setFieldErrors((prev) => ({ ...prev, [key]: undefined }));
    }
  }

  function validate(): FieldErrors {
    const errs: FieldErrors = {};
    if (!form.brand.trim()) errs.brand = "Укажите марку";
    if (!form.model.trim()) errs.model = "Укажите модель";
    if (form.year < 1900 || form.year > 2100) errs.year = "Год от 1900 до 2100";
    if (form.mileage < 0) errs.mileage = "Пробег не может быть отрицательным";
    if (form.engine_size < 600 || form.engine_size > 8000) {
      errs.engine_size = "Объём от 600 до 8000 см³";
    }
    return errs;
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const errors = validate();
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setServerError(null);
    mutation.mutate(form);
  }

  return (
    <Modal open={open} onClose={onClose} title="Редактировать автомобиль" size="lg">
      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <TextField
            label="Марка"
            value={form.brand}
            onChange={(v) => update("brand", v)}
            error={fieldErrors.brand}
          />
          <TextField
            label="Модель"
            value={form.model}
            onChange={(v) => update("model", v)}
            error={fieldErrors.model}
          />
          <NumberField
            label="Год выпуска"
            value={form.year}
            onChange={(v) => update("year", v)}
            min={1900}
            max={2100}
            error={fieldErrors.year}
          />
          <NumberField
            label="Пробег, км"
            value={form.mileage}
            onChange={(v) => update("mileage", v)}
            min={0}
            error={fieldErrors.mileage}
          />
          <NumberField
            label="Объём двигателя, см³"
            value={form.engine_size}
            onChange={(v) => update("engine_size", v)}
            min={600}
            max={8000}
            error={fieldErrors.engine_size}
          />
          <SelectField
            label="Тип кузова"
            value={form.body_type}
            onChange={(v) => update("body_type", v as BodyType)}
            options={bodyTypeLabel}
          />
          <SelectField
            label="Тип топлива"
            value={form.fuel_type}
            onChange={(v) => update("fuel_type", v as FuelType)}
            options={fuelTypeLabel}
          />
          <SelectField
            label="Коробка передач"
            value={form.transmission}
            onChange={(v) => update("transmission", v as Transmission)}
            options={transmissionLabel}
          />
          <SelectField
            label="Состояние тормозов"
            value={form.brake_condition}
            onChange={(v) => update("brake_condition", v as BrakeCondition)}
            options={brakeConditionLabel}
          />
          <SelectField
            label="По счёту владелец"
            value={form.owner_type}
            onChange={(v) => update("owner_type", v as OwnerType)}
            options={ownerTypeLabel}
          />
        </div>

        {serverError && <p className="text-sm text-red-600">{serverError}</p>}

        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-md border border-slate-300 px-4 py-2 text-sm text-slate-700 transition hover:bg-slate-50"
          >
            Отмена
          </button>
          <button
            type="submit"
            disabled={mutation.isPending}
            className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800 disabled:opacity-50"
          >
            {mutation.isPending ? "Сохраняем..." : "Сохранить"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function carToInput(car: Car): CarInput {
  return {
    brand: car.brand,
    model: car.model,
    year: car.year,
    mileage: car.mileage,
    body_type: car.body_type,
    fuel_type: car.fuel_type,
    transmission: car.transmission,
    engine_size: car.engine_size,
    brake_condition: car.brake_condition,
    owner_type: car.owner_type,
  };
}
