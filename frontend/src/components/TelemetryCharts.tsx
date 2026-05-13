import { useQuery } from "@tanstack/react-query";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { listTelemetryByCar } from "../api/telemetry";
import type { TelemetryLog } from "../types";

interface TelemetryChartsProps {
  carId: number;
}

interface ChartPoint {
  ts: number;
  label: string;
  coolant_temp: number | null;
  rpm: number | null;
  battery_voltage: number | null;
}

export function TelemetryCharts({ carId }: TelemetryChartsProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["telemetry", carId],
    queryFn: () => listTelemetryByCar(carId, 200),
    refetchInterval: 5000,
    refetchIntervalInBackground: false,
  });

  const points = transform(data ?? []);

  return (
    <section>
      <h2 className="text-sm font-medium text-slate-500">Телеметрия</h2>

      {isLoading && !data && (
        <p className="mt-2 text-xs text-slate-500">Загружаем телеметрию...</p>
      )}

      {data && data.length === 0 && (
        <div className="mt-2 rounded-md border border-dashed border-slate-300 px-5 py-6 text-xs text-slate-400">
          Данных пока нет. Подключите устройство к автомобилю и запустите OBD-агента.
        </div>
      )}

      {points.length > 0 && (
        <div className="mt-3 space-y-4">
          <ChartCard
            title="Температура охлаждающей жидкости"
            unit="°C"
            data={points}
            dataKey="coolant_temp"
            domain={[40, 130]}
            warningBand={{ min: 95, max: 105 }}
            criticalAbove={105}
          />
          <ChartCard
            title="Обороты двигателя"
            unit="об/мин"
            data={points}
            dataKey="rpm"
            domain={[0, 6500]}
          />
          <ChartCard
            title="Напряжение аккумулятора"
            unit="В"
            data={points}
            dataKey="battery_voltage"
            domain={[10, 16]}
            criticalBelow={11.5}
            warningBand={{ min: 11.5, max: 12.5 }}
          />
        </div>
      )}
    </section>
  );
}

interface ChartCardProps {
  title: string;
  unit: string;
  data: ChartPoint[];
  dataKey: "coolant_temp" | "rpm" | "battery_voltage";
  domain: [number, number];
  warningBand?: { min: number; max: number };
  criticalAbove?: number;
  criticalBelow?: number;
}

function ChartCard({
  title,
  unit,
  data,
  dataKey,
  domain,
  warningBand,
  criticalAbove,
  criticalBelow,
}: ChartCardProps) {
  const latest = [...data].reverse().find((p) => p[dataKey] !== null)?.[dataKey] ?? null;

  const tone =
    latest === null
      ? "text-slate-400"
      : criticalAbove !== undefined && latest >= criticalAbove
        ? "text-red-600"
        : criticalBelow !== undefined && latest <= criticalBelow
          ? "text-red-600"
          : warningBand && latest >= warningBand.min && latest <= warningBand.max
            ? "text-amber-600"
            : "text-emerald-600";

  return (
    <div className="rounded-md border border-slate-200 bg-white p-4">
      <div className="flex items-baseline justify-between">
        <h3 className="text-xs font-medium text-slate-500">{title}</h3>
        <span className={`text-lg font-medium ${tone}`}>
          {latest === null ? "—" : `${formatValue(latest, dataKey)} ${unit}`}
        </span>
      </div>
      <div className="mt-2 h-32 w-full">
        <ResponsiveContainer>
          <LineChart
            data={data}
            margin={{ top: 5, right: 8, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis
              dataKey="label"
              tick={{ fontSize: 10, fill: "#94a3b8" }}
              interval="preserveStartEnd"
              minTickGap={40}
            />
            <YAxis
              domain={domain}
              tick={{ fontSize: 10, fill: "#94a3b8" }}
              width={40}
            />
            <Tooltip
              labelStyle={{ fontSize: 11, color: "#64748b" }}
              contentStyle={{
                fontSize: 11,
                borderColor: "#e2e8f0",
                borderRadius: 6,
              }}
              formatter={(v) => {
                if (typeof v !== "number") return "—";
                return `${formatValue(v, dataKey)} ${unit}`;
              }}
            />
            <Line
              type="monotone"
              dataKey={dataKey}
              stroke="#0f172a"
              strokeWidth={1.5}
              dot={false}
              isAnimationActive={false}
              connectNulls
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function transform(logs: TelemetryLog[]): ChartPoint[] {
  return logs
    .map<ChartPoint>((log) => {
      const date = new Date(log.timestamp);
      return {
        ts: date.getTime(),
        label: date.toLocaleTimeString("ru-RU", {
          hour: "2-digit",
          minute: "2-digit",
        }),
        coolant_temp: log.coolant_temp,
        rpm: log.rpm,
        battery_voltage: log.battery_voltage,
      };
    })
    .sort((a, b) => a.ts - b.ts);
}

function formatValue(value: number, dataKey: string): string {
  if (dataKey === "rpm") return Math.round(value).toLocaleString("ru-RU");
  return value.toFixed(1);
}
