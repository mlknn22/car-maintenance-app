import { useQuery } from "@tanstack/react-query";
import { listAlertsByCar } from "../api/alerts";
import type { Alert, Severity } from "../types";

interface AlertsSectionProps {
  carId: number;
}

const SEVERITY_STYLE: Record<Severity, { container: string; label: string; icon: string }> = {
  critical: {
    container: "border-red-200 bg-red-50",
    label: "text-red-900",
    icon: "text-red-600",
  },
  warning: {
    container: "border-amber-200 bg-amber-50",
    label: "text-amber-900",
    icon: "text-amber-600",
  },
  info: {
    container: "border-slate-200 bg-slate-50",
    label: "text-slate-900",
    icon: "text-slate-500",
  },
};

const SEVERITY_TITLE: Record<Severity, string> = {
  critical: "Критично",
  warning: "Предупреждение",
  info: "Информация",
};

export function AlertsSection({ carId }: AlertsSectionProps) {
  const { data: alerts, isLoading } = useQuery({
    queryKey: ["alerts", carId, "active"],
    queryFn: () => listAlertsByCar(carId, "active"),
    refetchInterval: 5000,
    refetchIntervalInBackground: false,
  });

  if (isLoading) return null;
  if (!alerts || alerts.length === 0) return null;

  const sorted = [...alerts].sort(severityCompare);

  return (
    <section className="space-y-2">
      {sorted.map((alert) => (
        <AlertBanner key={alert.id} alert={alert} />
      ))}
    </section>
  );
}

function AlertBanner({ alert }: { alert: Alert }) {
  const style = SEVERITY_STYLE[alert.severity];
  return (
    <div className={`rounded-md border px-4 py-3 ${style.container}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className={`text-xs font-medium uppercase tracking-wide ${style.icon}`}>
            {SEVERITY_TITLE[alert.severity]}
          </div>
          <div className={`mt-1 text-sm ${style.label}`}>{alert.message}</div>
        </div>
        <div className="shrink-0 text-xs text-slate-500">
          {formatTime(alert.timestamp)}
        </div>
      </div>
    </div>
  );
}

const SEVERITY_RANK: Record<Severity, number> = { critical: 0, warning: 1, info: 2 };

function severityCompare(a: Alert, b: Alert): number {
  return SEVERITY_RANK[a.severity] - SEVERITY_RANK[b.severity];
}

function formatTime(value: string): string {
  const date = new Date(value);
  const diffSec = Math.floor((Date.now() - date.getTime()) / 1000);
  if (diffSec < 60) return "только что";
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)} мин назад`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} ч назад`;
  return date.toLocaleString("ru-RU", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}
