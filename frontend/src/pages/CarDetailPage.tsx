import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { deleteCar, getCar, getRiskScore } from "../api/cars";
import { CarEditModal } from "../components/CarEditModal";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { AlertsSection } from "../components/AlertsSection";
import { DevicesSection } from "../components/DevicesSection";
import { MaintenanceSection } from "../components/MaintenanceSection";
import { TelemetryCharts } from "../components/TelemetryCharts";
import {
  bodyTypeLabel,
  brakeConditionLabel,
  fuelTypeLabel,
  ownerTypeLabel,
  transmissionLabel,
} from "../lib/labels";
import type { Car } from "../types";

export function CarDetailPage() {
  const { id } = useParams();
  const carId = Number(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);

  const { data: car, isLoading, error } = useQuery({
    queryKey: ["car", carId],
    queryFn: () => getCar(carId),
    enabled: !Number.isNaN(carId),
  });

  const riskMutation = useMutation({
    mutationFn: () => getRiskScore(carId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["car", carId] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteCar(carId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cars"] });
      navigate("/cars", { replace: true });
    },
  });

  if (Number.isNaN(carId)) {
    return <NotFound />;
  }

  if (isLoading) {
    return <p className="text-sm text-slate-500">Загружаем автомобиль...</p>;
  }

  if (error || !car) {
    return <NotFound />;
  }

  return (
    <div className="space-y-8">
      <div>
        <Link to="/cars" className="text-sm text-slate-500 hover:text-slate-900">
          ← Все автомобили
        </Link>
        <div className="mt-4 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-medium tracking-tight text-slate-900">
              {car.brand} {car.model}
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              {car.year} год · {car.mileage.toLocaleString("ru-RU")} км
            </p>
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setEditOpen(true)}
              className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 transition hover:bg-slate-50"
            >
              Редактировать
            </button>
            <button
              type="button"
              onClick={() => setDeleteOpen(true)}
              className="rounded-md border border-red-300 px-3 py-1.5 text-sm text-red-600 transition hover:bg-red-50"
            >
              Удалить
            </button>
          </div>
        </div>
      </div>

      <CarSummary car={car} />

      <RiskScoreCard
        car={car}
        onRecalculate={() => riskMutation.mutate()}
        pending={riskMutation.isPending}
        error={
          riskMutation.error instanceof ApiError
            ? riskMutation.error.message
            : null
        }
      />

      <AlertsSection carId={car.id} />
      <DevicesSection carId={car.id} />
      <TelemetryCharts carId={car.id} />
      <MaintenanceSection carId={car.id} defaultMileage={car.mileage} />

      <CarEditModal car={car} open={editOpen} onClose={() => setEditOpen(false)} />
      <ConfirmDialog
        open={deleteOpen}
        onClose={() => setDeleteOpen(false)}
        onConfirm={() => deleteMutation.mutate()}
        title="Удалить автомобиль?"
        message={`Все данные «${car.brand} ${car.model}» — устройства, телеметрия, история ТО, алерты — будут удалены без возможности восстановления.`}
        confirmLabel="Удалить"
        danger
        pending={deleteMutation.isPending}
      />
    </div>
  );
}

function CarSummary({ car }: { car: Car }) {
  return (
    <div className="rounded-md border border-slate-200 bg-white">
      <dl className="grid grid-cols-2 gap-x-6 gap-y-3 p-5 text-sm sm:grid-cols-3">
        <Row label="Тип кузова" value={bodyTypeLabel[car.body_type]} />
        <Row label="Топливо" value={fuelTypeLabel[car.fuel_type]} />
        <Row label="КПП" value={transmissionLabel[car.transmission]} />
        <Row label="Объём двигателя" value={`${car.engine_size} см³`} />
        <Row label="Тормоза" value={brakeConditionLabel[car.brake_condition]} />
        <Row label="Владелец" value={ownerTypeLabel[car.owner_type]} />
      </dl>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-slate-500">{label}</dt>
      <dd className="text-slate-900">{value}</dd>
    </div>
  );
}

interface RiskScoreCardProps {
  car: Car;
  onRecalculate: () => void;
  pending: boolean;
  error: string | null;
}

function RiskScoreCard({ car, onRecalculate, pending, error }: RiskScoreCardProps) {
  const score = car.risk_score;
  const percent = score === null ? null : Math.round(score * 100);
  const tone =
    score === null
      ? "text-slate-400"
      : score >= 0.7
        ? "text-red-600"
        : score >= 0.4
          ? "text-amber-600"
          : "text-emerald-600";

  return (
    <div className="rounded-md border border-slate-200 bg-white p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-sm font-medium text-slate-500">
            ML-оценка необходимости ТО
          </h2>
          <p className={`mt-2 text-3xl font-medium ${tone}`}>
            {percent === null ? "—" : `${percent}%`}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            {score === null
              ? "Нажмите «Рассчитать», чтобы запросить оценку ML-модели"
              : score >= 0.7
                ? "Высокий риск: рекомендуется провести ТО в ближайшее время"
                : score >= 0.4
                  ? "Средний риск: следите за состоянием"
                  : "Низкий риск: автомобиль в хорошем состоянии"}
          </p>
        </div>
        <button
          type="button"
          onClick={onRecalculate}
          disabled={pending}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
        >
          {pending ? "Считаем..." : score === null ? "Рассчитать" : "Пересчитать"}
        </button>
      </div>
      {error && <p className="mt-3 text-xs text-red-600">{error}</p>}
    </div>
  );
}

function NotFound() {
  return (
    <div>
      <Link to="/cars" className="text-sm text-slate-500 hover:text-slate-900">
        ← Все автомобили
      </Link>
      <h1 className="mt-4 text-xl font-medium text-slate-900">Автомобиль не найден</h1>
    </div>
  );
}
