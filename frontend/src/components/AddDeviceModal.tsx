import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { createDevice } from "../api/devices";
import { ApiError } from "../api/client";
import type { DeviceCreated } from "../types";
import { TextField } from "./FormFields";
import { Modal } from "./Modal";

interface AddDeviceModalProps {
  carId: number;
  open: boolean;
  onClose: () => void;
  onCreated: (device: DeviceCreated) => void;
}

export function AddDeviceModal({ carId, open, onClose, onCreated }: AddDeviceModalProps) {
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [nameError, setNameError] = useState<string | null>(null);
  const [serverError, setServerError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () => createDevice({ car_id: carId, device_name: name.trim() }),
    onSuccess: (device) => {
      queryClient.invalidateQueries({ queryKey: ["devices", carId] });
      setName("");
      onCreated(device);
    },
    onError: (err) => {
      setServerError(
        err instanceof ApiError ? err.message : "Не удалось добавить устройство",
      );
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!name.trim()) {
      setNameError("Укажите название устройства");
      return;
    }
    setNameError(null);
    setServerError(null);
    mutation.mutate();
  }

  function handleClose() {
    setName("");
    setNameError(null);
    setServerError(null);
    onClose();
  }

  return (
    <Modal open={open} onClose={handleClose} title="Новое устройство" size="md">
      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        <p className="text-sm text-slate-500">
          Адаптер ELM327, подключаемый к OBD-II разъёму автомобиля. После создания
          вы получите API-токен — его нужно будет передать агенту при запуске.
        </p>
        <TextField
          label="Название устройства"
          value={name}
          onChange={(v) => {
            setName(v);
            if (nameError) setNameError(null);
          }}
          placeholder="Например: ELM327 в Creta"
          error={nameError ?? undefined}
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
            {mutation.isPending ? "Создаём..." : "Создать"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
