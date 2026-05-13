import { Modal } from "./Modal";

interface ConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  danger?: boolean;
  pending?: boolean;
}

export function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = "Подтвердить",
  danger = false,
  pending = false,
}: ConfirmDialogProps) {
  const confirmClass = danger
    ? "bg-red-600 hover:bg-red-700"
    : "bg-slate-900 hover:bg-slate-800";

  return (
    <Modal open={open} onClose={onClose} title={title} size="sm">
      <p className="text-sm text-slate-600">{message}</p>
      <div className="mt-5 flex justify-end gap-2">
        <button
          type="button"
          onClick={onClose}
          className="rounded-md border border-slate-300 px-4 py-2 text-sm text-slate-700 transition hover:bg-slate-50"
        >
          Отмена
        </button>
        <button
          type="button"
          onClick={onConfirm}
          disabled={pending}
          className={`rounded-md px-4 py-2 text-sm font-medium text-white transition disabled:opacity-50 ${confirmClass}`}
        >
          {pending ? "..." : confirmLabel}
        </button>
      </div>
    </Modal>
  );
}
