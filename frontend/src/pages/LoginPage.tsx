import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { login } from "../api/auth";
import { ApiError } from "../api/client";
import { setToken } from "../lib/auth";
import { validateEmail, validatePassword } from "../lib/validators";

interface LocationState {
  from?: string;
}

interface FieldErrors {
  email?: string;
  password?: string;
}

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = (location.state as LocationState)?.from ?? "/cars";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const errors: FieldErrors = {};
    const emailError = validateEmail(email);
    if (emailError) errors.email = emailError;
    const passwordError = validatePassword(password);
    if (passwordError) errors.password = passwordError;
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setServerError(null);
    setSubmitting(true);
    try {
      const token = await login(email, password);
      setToken(token.access_token);
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setServerError(translateLoginError(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6 py-12">
        <h1 className="text-2xl font-medium tracking-tight text-slate-900">
          Вход
        </h1>
        <p className="mt-2 text-sm text-slate-500">
          Войдите, чтобы продолжить отслеживание состояния автомобиля
        </p>

        <form onSubmit={handleSubmit} noValidate className="mt-8 space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm text-slate-700">
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (fieldErrors.email) {
                  setFieldErrors((prev) => ({ ...prev, email: undefined }));
                }
              }}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-900 focus:outline-none"
            />
            {fieldErrors.email && (
              <p className="mt-1 text-xs text-red-600">{fieldErrors.email}</p>
            )}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm text-slate-700">
              Пароль
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (fieldErrors.password) {
                  setFieldErrors((prev) => ({ ...prev, password: undefined }));
                }
              }}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-slate-900 focus:outline-none"
            />
            {fieldErrors.password && (
              <p className="mt-1 text-xs text-red-600">{fieldErrors.password}</p>
            )}
          </div>

          {serverError && <p className="text-sm text-red-600">{serverError}</p>}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800 disabled:opacity-50"
          >
            {submitting ? "Входим..." : "Войти"}
          </button>
        </form>

        <p className="mt-6 text-sm text-slate-500">
          Нет аккаунта?{" "}
          <Link to="/register" className="text-slate-900 underline underline-offset-2">
            Зарегистрироваться
          </Link>
        </p>
      </div>
    </div>
  );
}

function translateLoginError(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.status === 401) return "Неверный email или пароль";
    if (err.status === 422) return "Проверьте корректность полей";
    return err.message;
  }
  return "Не удалось войти, повторите попытку";
}
