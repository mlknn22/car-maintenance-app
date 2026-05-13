import { useState } from "react";
import { Modal } from "./Modal";

interface DeviceTokenModalProps {
  open: boolean;
  onClose: () => void;
  deviceId: number;
  token: string;
  isNew: boolean;
}

export function DeviceTokenModal({
  open,
  onClose,
  deviceId,
  token,
  isNew,
}: DeviceTokenModalProps) {
  const [copied, setCopied] = useState<string | null>(null);

  const baseUrl = window.location.origin.replace("5173", "8000");
  const command = `uv run python agent/obd_agent.py --device-id ${deviceId} --token ${token} --base-url ${baseUrl} --interval 5`;
  const mockCommand = `uv run python agent/obd_agent.py --device-id ${deviceId} --token ${token} --base-url ${baseUrl} --mock`;

  function copy(text: string, label: string) {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(label);
      setTimeout(() => setCopied(null), 2000);
    });
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isNew ? "Устройство добавлено" : "Новый токен выпущен"}
      size="lg"
    >
      <div className="space-y-4">
        <div className="rounded-md bg-amber-50 border border-amber-200 px-4 py-3 text-xs text-amber-900">
          <strong className="font-medium">Сохраните токен сейчас.</strong> После
          закрытия окна он больше не будет показан. Если потеряете —
          сгенерируйте новый (старый перестанет работать).
        </div>

        <div>
          <label className="block text-xs text-slate-500">API-токен устройства</label>
          <div className="mt-1 flex gap-2">
            <code className="flex-1 break-all rounded-md bg-slate-100 px-3 py-2 font-mono text-xs text-slate-900">
              {token}
            </code>
            <button
              type="button"
              onClick={() => copy(token, "token")}
              className="rounded-md border border-slate-300 px-3 py-1 text-xs text-slate-700 transition hover:bg-slate-50"
            >
              {copied === "token" ? "Скопировано" : "Копировать"}
            </button>
          </div>
        </div>

        <div>
          <label className="block text-xs text-slate-500">
            Команда запуска агента (реальный OBD-адаптер)
          </label>
          <div className="mt-1 flex gap-2">
            <code className="flex-1 break-all rounded-md bg-slate-100 px-3 py-2 font-mono text-xs text-slate-900">
              {command}
            </code>
            <button
              type="button"
              onClick={() => copy(command, "real")}
              className="rounded-md border border-slate-300 px-3 py-1 text-xs text-slate-700 transition hover:bg-slate-50"
            >
              {copied === "real" ? "Скопировано" : "Копировать"}
            </button>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            Запустите в терминале на ноутбуке с подключённым адаптером.
          </p>
        </div>

        <div>
          <label className="block text-xs text-slate-500">
            Mock-режим (без железа, для проверки)
          </label>
          <div className="mt-1 flex gap-2">
            <code className="flex-1 break-all rounded-md bg-slate-100 px-3 py-2 font-mono text-xs text-slate-900">
              {mockCommand}
            </code>
            <button
              type="button"
              onClick={() => copy(mockCommand, "mock")}
              className="rounded-md border border-slate-300 px-3 py-1 text-xs text-slate-700 transition hover:bg-slate-50"
            >
              {copied === "mock" ? "Скопировано" : "Копировать"}
            </button>
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
          >
            Готово
          </button>
        </div>
      </div>
    </Modal>
  );
}
