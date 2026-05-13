import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { listCars } from "../api/cars";
import { bodyTypeLabel, fuelTypeLabel } from "../lib/labels";
import type { Car } from "../types";

export function CarsListPage() {
  const { data: cars, isLoading, error } = useQuery({
    queryKey: ["cars"],
    queryFn: listCars,
  });

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-medium tracking-tight text-slate-900">
            Мои автомобили
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Список зарегистрированных автомобилей с оценкой риска
          </p>
        </div>
        <Link
          to="/cars/new"
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
        >
          + Добавить автомобиль
        </Link>
      </div>

      <div className="mt-8">
        {isLoading && (
          <p className="text-sm text-slate-500">Загружаем список...</p>
        )}

        {error && (
          <p className="text-sm text-red-600">
            Не удалось загрузить список автомобилей
          </p>
        )}

        {cars && cars.length === 0 && (
          <div className="rounded-md border border-dashed border-slate-300 px-6 py-12 text-center">
            <p className="text-sm text-slate-500">
              Пока ни одного автомобиля не добавлено
            </p>
            <Link
              to="/cars/new"
              className="mt-4 inline-block rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
            >
              Добавить первый
            </Link>
          </div>
        )}

        {cars && cars.length > 0 && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {cars.map((car) => (
              <CarCard key={car.id} car={car} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function CarCard({ car }: { car: Car }) {
  return (
    <Link
      to={`/cars/${car.id}`}
      className="block rounded-md border border-slate-200 bg-white p-4 transition hover:border-slate-400"
    >
      <div className="flex items-baseline justify-between gap-2">
        <h2 className="text-base font-medium text-slate-900">
          {car.brand} {car.model}
        </h2>
        <span className="text-sm text-slate-500">{car.year}</span>
      </div>
      <div className="mt-3 flex items-center justify-between text-sm">
        <span className="text-slate-500">
          {car.mileage.toLocaleString("ru-RU")} км
        </span>
        <RiskBadge value={car.risk_score} />
      </div>
      <div className="mt-2 text-xs text-slate-400">
        {bodyTypeLabel[car.body_type]} · {fuelTypeLabel[car.fuel_type]}
      </div>
    </Link>
  );
}

function RiskBadge({ value }: { value: number | null }) {
  if (value === null) {
    return <span className="text-xs text-slate-400">Риск не рассчитан</span>;
  }

  const percent = Math.round(value * 100);
  const tone =
    value >= 0.7
      ? "text-red-600"
      : value >= 0.4
        ? "text-amber-600"
        : "text-emerald-600";

  return (
    <span className={`text-sm font-medium ${tone}`}>
      Риск {percent}%
    </span>
  );
}
