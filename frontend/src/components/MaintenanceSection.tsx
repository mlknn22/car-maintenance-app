import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { ApiError } from "../api/client";
import { deleteRecord, listRecordsByCar } from "../api/maintenance";
import type { MaintenanceRecord } from "../types";
import { AddMaintenanceModal } from "./AddMaintenanceModal";
import { ConfirmDialog } from "./ConfirmDialog";

interface MaintenanceSectionProps {
  carId: number;
  defaultMileage: number;
}

export function MaintenanceSection({ carId, defaultMileage }: MaintenanceSectionProps) {
  const queryClient = useQueryClient();
  const [addOpen, setAddOpen] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState<MaintenanceRecord | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const { data: records, isLoading } = useQuery({
    queryKey: ["maintenance", carId],
    queryFn: () => listRecordsByCar(carId),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteRecord(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["maintenance", carId] });
      setConfirmDelete(null);
    },
    onError: (err) => {
      setActionError(
        err instanceof ApiError ? err.message : "Не удалось удалить запись",
      );
    },
  });

  const sorted = (records ?? [])
    .slice()
    .sort((a, b) => (a.service_date < b.service_date ? 1 : -1));

  return (
    <section>
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-medium text-slate-500">История ТО</h2>
        <button
          type="button"
          onClick={() => setAddOpen(true)}
          className="text-sm text-slate-900 underline underline-offset-2"
        >
          + Добавить запись
        </button>
      </div>

      <div className="mt-2">
        {isLoading && (
          <p className="text-xs text-slate-500">Загружаем историю...</p>
        )}

        {actionError && <p className="mb-3 text-xs text-red-600">{actionError}</p>}

        {records && records.length === 0 && (
          <div className="rounded-md border border-dashed border-slate-300 px-5 py-6 text-xs text-slate-400">
            Записей о ТО пока нет
          </div>
        )}

        {sorted.length > 0 && (
          <div className="overflow-hidden rounded-md border border-slate-200 bg-white">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-xs text-slate-500">
                <tr>
                  <th className="px-4 py-2 text-left font-normal">Дата</th>
                  <th className="px-4 py-2 text-left font-normal">Вид работ</th>
                  <th className="px-4 py-2 text-right font-normal">Стоимость</th>
                  <th className="px-4 py-2 text-right font-normal">Пробег</th>
                  <th className="px-4 py-2 w-12" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {sorted.map((record) => (
                  <tr key={record.id}>
                    <td className="px-4 py-2 text-slate-700 whitespace-nowrap">
                      {formatDate(record.service_date)}
                    </td>
                    <td className="px-4 py-2 text-slate-900">
                      {record.work_type}
                      {record.notes && (
                        <div className="text-xs text-slate-500">{record.notes}</div>
                      )}
                    </td>
                    <td className="px-4 py-2 text-right text-slate-700">
                      {formatRub(record.cost)}
                    </td>
                    <td className="px-4 py-2 text-right text-slate-700">
                      {record.mileage_at_service.toLocaleString("ru-RU")} км
                    </td>
                    <td className="px-4 py-2 text-right">
                      <button
                        type="button"
                        onClick={() => setConfirmDelete(record)}
                        className="text-xs text-slate-400 transition hover:text-red-600"
                        aria-label="Удалить запись"
                      >
                        ×
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <AddMaintenanceModal
        carId={carId}
        defaultMileage={defaultMileage}
        open={addOpen}
        onClose={() => setAddOpen(false)}
      />

      <ConfirmDialog
        open={confirmDelete !== null}
        onClose={() => setConfirmDelete(null)}
        onConfirm={() => confirmDelete && deleteMutation.mutate(confirmDelete.id)}
        title="Удалить запись?"
        message={
          confirmDelete
            ? `Запись «${confirmDelete.work_type}» от ${formatDate(confirmDelete.service_date)} будет удалена.`
            : ""
        }
        confirmLabel="Удалить"
        danger
        pending={deleteMutation.isPending}
      />
    </section>
  );
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

function formatRub(value: number): string {
  return value.toLocaleString("ru-RU", { maximumFractionDigits: 0 }) + " ₽";
}
