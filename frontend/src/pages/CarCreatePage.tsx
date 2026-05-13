import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createCar } from "../api/cars";
import { ApiError } from "../api/client";
import { NumberField, SelectField, TextField } from "../components/FormFields";
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
  CarInput,
  FuelType,
  OwnerType,
  Transmission,
} from "../types";

interface FieldErrors {
  brand?: string;
  model?: string;
  year?: string;
  mileage?: string;
  engine_size?: string;
}

const CURRENT_YEAR = new Date().getFullYear();

const INITIAL: CarInput = {
  brand: "",
  model: "",
  year: CURRENT_YEAR,
  mileage: 0,
  body_type: "Car",
  fuel_type: "Petrol",
  transmission: "Automatic",
  engine_size: 1600,
  brake_condition: "Good",
  owner_type: "First",
};

export function CarCreatePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [form, setForm] = useState<CarInput>(INITIAL);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [serverError, setServerError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: createCar,
    onSuccess: (car) => {
      queryClient.invalidateQueries({ queryKey: ["cars"] });
      navigate(`/cars/${car.id}`, { replace: true });
    },
    onError: (err) => {
      setServerError(
        err instanceof ApiError ? err.message : "Не удалось создать автомобиль",
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
    <div>
      <Link to="/cars" className="text-sm text-slate-500 hover:text-slate-900">
        ← Все автомобили
      </Link>
      <h1 className="mt-4 text-2xl font-medium tracking-tight text-slate-900">
        Новый автомобиль
      </h1>
      <p className="mt-1 text-sm text-slate-500">
        Эти данные используются ML-моделью для оценки риска необходимости ТО
      </p>

      <form onSubmit={handleSubmit} noValidate className="mt-8 max-w-2xl space-y-5">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <TextField
            label="Марка"
            value={form.brand}
            onChange={(v) => update("brand", v)}
            placeholder="Hyundai"
            error={fieldErrors.brand}
          />
          <TextField
            label="Модель"
            value={form.model}
            onChange={(v) => update("model", v)}
            placeholder="Creta"
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

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={mutation.isPending}
            className="rounded-md bg-slate-900 px-5 py-2 text-sm font-medium text-white transition hover:bg-slate-800 disabled:opacity-50"
          >
            {mutation.isPending ? "Сохраняем..." : "Сохранить"}
          </button>
          <Link
            to="/cars"
            className="rounded-md border border-slate-300 px-5 py-2 text-sm text-slate-700 transition hover:bg-slate-50"
          >
            Отмена
          </Link>
        </div>
      </form>
    </div>
  );
}

