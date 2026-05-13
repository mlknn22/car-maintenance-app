import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { deleteDevice, listDevicesByCar, regenerateDeviceToken } from "../api/devices";
import { ApiError } from "../api/client";
import type { Device } from "../types";
import { AddDeviceModal } from "./AddDeviceModal";
import { ConfirmDialog } from "./ConfirmDialog";
import { DeviceTokenModal } from "./DeviceTokenModal";

interface DevicesSectionProps {
  carId: number;
}

interface ShownToken {
  deviceId: number;
  token: string;
  isNew: boolean;
}

export function DevicesSection({ carId }: DevicesSectionProps) {
  const queryClient = useQueryClient();

  const [addOpen, setAddOpen] = useState(false);
  const [shownToken, setShownToken] = useState<ShownToken | null>(null);
  const [confirmRegen, setConfirmRegen] = useState<Device | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<Device | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const { data: devices, isLoading } = useQuery({
    queryKey: ["devices", carId],
    queryFn: () => listDevicesByCar(carId),
  });

  const regenerateMutation = useMutation({
    mutationFn: (id: number) => regenerateDeviceToken(id),
    onSuccess: (response, id) => {
      setShownToken({ deviceId: id, token: response.api_token, isNew: false });
      setConfirmRegen(null);
    },
    onError: (err) => {
      setActionError(
        err instanceof ApiError ? err.message : "Не удалось выпустить токен",
      );
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteDevice(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["devices", carId] });
      setConfirmDelete(null);
    },
    onError: (err) => {
      setActionError(
        err instanceof ApiError ? err.message : "Не удалось удалить устройство",
      );
    },
  });

  return (
    <section>
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-medium text-slate-500">Устройства</h2>
        <button
          type="button"
          onClick={() => setAddOpen(true)}
          className="text-sm text-slate-900 underline underline-offset-2"
        >
          + Добавить устройство
        </button>
      </div>

      <div className="mt-2">
        {isLoading && <p className="text-xs text-slate-500">Загружаем устройства...</p>}

        {actionError && (
          <p className="mb-3 text-xs text-red-600">{actionError}</p>
        )}

        {devices && devices.length === 0 && (
          <div className="rounded-md border border-dashed border-slate-300 px-5 py-6 text-xs text-slate-400">
            К автомобилю не подключено ни одного OBD-устройства
          </div>
        )}

        {devices && devices.length > 0 && (
          <ul className="space-y-2">
            {devices.map((device) => (
              <li
                key={device.id}
                className="flex items-center justify-between rounded-md border border-slate-200 bg-white px-4 py-3"
              >
                <div className="min-w-0">
                  <div className="text-sm font-medium text-slate-900">
                    {device.device_name}
                  </div>
                  <div className="mt-1 text-xs text-slate-500">
                    {formatLastSeen(device.last_seen)}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setConfirmRegen(device)}
                    className="rounded-md border border-slate-300 px-3 py-1 text-xs text-slate-700 transition hover:bg-slate-50"
                  >
                    Новый токен
                  </button>
                  <button
                    type="button"
                    onClick={() => setConfirmDelete(device)}
                    className="rounded-md border border-red-300 px-3 py-1 text-xs text-red-600 transition hover:bg-red-50"
                  >
                    Удалить
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <AddDeviceModal
        carId={carId}
        open={addOpen}
        onClose={() => setAddOpen(false)}
        onCreated={(device) => {
          queryClient.invalidateQueries({ queryKey: ["devices", carId] });
          setAddOpen(false);
          setShownToken({
            deviceId: device.id,
            token: device.api_token,
            isNew: true,
          });
        }}
      />

      {shownToken && (
        <DeviceTokenModal
          open
          onClose={() => setShownToken(null)}
          deviceId={shownToken.deviceId}
          token={shownToken.token}
          isNew={shownToken.isNew}
        />
      )}

      <ConfirmDialog
        open={confirmRegen !== null}
        onClose={() => setConfirmRegen(null)}
        onConfirm={() => confirmRegen && regenerateMutation.mutate(confirmRegen.id)}
        title="Выпустить новый токен?"
        message="Старый токен перестанет работать. Запущенный с ним агент получит 401 и остановится."
        confirmLabel="Выпустить"
        pending={regenerateMutation.isPending}
      />

      <ConfirmDialog
        open={confirmDelete !== null}
        onClose={() => setConfirmDelete(null)}
        onConfirm={() => confirmDelete && deleteMutation.mutate(confirmDelete.id)}
        title="Удалить устройство?"
        message={
          confirmDelete
            ? `«${confirmDelete.device_name}» и все его записи телеметрии будут удалены.`
            : ""
        }
        confirmLabel="Удалить"
        danger
        pending={deleteMutation.isPending}
      />
    </section>
  );
}

function formatLastSeen(value: string | null): string {
  if (!value) return "Ни разу не выходило на связь";
  const date = new Date(value);
  const diffMs = Date.now() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  if (diffSec < 60) return "Активно сейчас";
  if (diffSec < 3600) return `Последний сигнал ${Math.floor(diffSec / 60)} мин назад`;
  if (diffSec < 86400) return `Последний сигнал ${Math.floor(diffSec / 3600)} ч назад`;
  return `Последний сигнал ${date.toLocaleDateString("ru-RU")}`;
}
