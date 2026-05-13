import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { createRecord } from "../api/maintenance";
import { ApiError } from "../api/client";
import type { MaintenanceRecordInput } from "../types";
import { NumberField, TextField, TextareaField } from "./FormFields";
import { Modal } from "./Modal";

interface AddMaintenanceModalProps {
  carId: number;
  defaultMileage: number;
  open: boolean;
  onClose: () => void;
}

interface FieldErrors {
  service_date?: string;
  work_type?: string;
  cost?: string;
  mileage_at_service?: string;
}

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

export function AddMaintenanceModal({
  carId,
  defaultMileage,
  open,
  onClose,
}: AddMaintenanceModalProps) {
  const queryClient = useQueryClient();

  const [serviceDate, setServiceDate] = useState(todayIso());
  const [workType, setWorkType] = useState("");
  const [cost, setCost] = useState(0);
  const [mileage, setMileage] = useState(defaultMileage);
  const [notes, setNotes] = useState("");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [serverError, setServerError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (payload: MaintenanceRecordInput) => createRecord(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["maintenance", carId] });
      reset();
      onClose();
    },
    onError: (err) => {
      setServerError(
        err instanceof ApiError ? err.message : "Не удалось сохранить запись",
      );
    },
  });

  function reset() {
    setServiceDate(todayIso());
    setWorkType("");
    setCost(0);
    setMileage(defaultMileage);
    setNotes("");
    setFieldErrors({});
    setServerError(null);
  }

  function handleClose() {
    reset();
    onClose();
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const errs: FieldErrors = {};
    if (!serviceDate) errs.service_date = "Укажите дату";
    if (workType.trim().length < 2) errs.work_type = "Опишите выполненную работу";
    if (cost < 0) errs.cost = "Стоимость не может быть отрицательной";
    if (mileage < 0) errs.mileage_at_service = "Пробег не может быть отрицательным";
    setFieldErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setServerError(null);
    mutation.mutate({
      car_id: carId,
      service_date: serviceDate,
      work_type: workType.trim(),
      cost,
      mileage_at_service: mileage,
      notes: notes.trim() || null,
    });
  }

  return (
    <Modal open={open} onClose={handleClose} title="Запись о ТО" size="md">
      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        <div>
          <label className="block text-sm text-slate-700">Дата работ</label>
          <input
            type="date"
            value={serviceDate}
            onChange={(e) => {
              setServiceDate(e.target.value);
              if (fieldErrors.service_date) {
                setFieldErrors((prev) => ({ ...prev, service_date: undefined }));
              }
            }}
            className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-slate-900 focus:outline-none"
          />
          {fieldErrors.service_date && (
            <p className="mt-1 text-xs text-red-600">{fieldErrors.service_date}</p>
          )}
        </div>

        <TextField
          label="Вид работ"
          value={workType}
          onChange={(v) => {
            setWorkType(v);
            if (fieldErrors.work_type) {
              setFieldErrors((prev) => ({ ...prev, work_type: undefined }));
            }
          }}
          placeholder="Замена масла"
          error={fieldErrors.work_type}
        />

        <div className="grid grid-cols-2 gap-4">
          <NumberField
            label="Стоимость, ₽"
            value={cost}
            onChange={(v) => {
              setCost(v);
              if (fieldErrors.cost) {
                setFieldErrors((prev) => ({ ...prev, cost: undefined }));
              }
            }}
            min={0}
            step={100}
            error={fieldErrors.cost}
          />
          <NumberField
            label="Пробег на момент ТО, км"
            value={mileage}
            onChange={(v) => {
              setMileage(v);
              if (fieldErrors.mileage_at_service) {
                setFieldErrors((prev) => ({
                  ...prev,
                  mileage_at_service: undefined,
                }));
              }
            }}
            min={0}
            error={fieldErrors.mileage_at_service}
          />
        </div>

        <TextareaField
          label="Заметки (необязательно)"
          value={notes}
          onChange={setNotes}
          placeholder="Поставщик, артикулы запчастей, другие детали"
        />

        {serverError && <p className="text-sm text-red-600">{serverError}</p>}

        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={handleClose}
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
