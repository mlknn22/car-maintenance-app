import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login, register } from "../api/auth";
import { ApiError } from "../api/client";
import { setToken } from "../lib/auth";
import { validateEmail, validatePassword } from "../lib/validators";

interface FieldErrors {
  email?: string;
  password?: string;
  full_name?: string;
}

export function RegisterPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function clearFieldError(name: keyof FieldErrors) {
    setFieldErrors((prev) =>
      prev[name] ? { ...prev, [name]: undefined } : prev,
    );
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const errors: FieldErrors = {};
    const emailError = validateEmail(email);
    if (emailError) errors.email = emailError;
    const passwordError = validatePassword(password);
    if (passwordError) errors.password = passwordError;
    if (fullName.length > 100) errors.full_name = "Имя слишком длинное";
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setServerError(null);
    setSubmitting(true);
    try {
      await register({
        email,
        password,
        full_name: fullName.trim() || null,
      });
      const token = await login(email, password);
      setToken(token.access_token);
      navigate("/cars", { replace: true });
    } catch (err) {
      setServerError(translateRegisterError(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6 py-12">
        <h1 className="text-2xl font-medium tracking-tight text-slate-900">
          Регистрация
        </h1>
        <p className="mt-2 text-sm text-slate-500">
          Создайте аккаунт, чтобы привязать свой автомобиль и устройство
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
                clearFieldError("email");
              }}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-slate-900 focus:outline-none"
            />
            {fieldErrors.email && (
              <p className="mt-1 text-xs text-red-600">{fieldErrors.email}</p>
            )}
          </div>

          <div>
            <label htmlFor="full_name" className="block text-sm text-slate-700">
              Имя <span className="text-slate-400">(необязательно)</span>
            </label>
            <input
              id="full_name"
              type="text"
              autoComplete="name"
              value={fullName}
              onChange={(e) => {
                setFullName(e.target.value);
                clearFieldError("full_name");
              }}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-slate-900 focus:outline-none"
            />
            {fieldErrors.full_name && (
              <p className="mt-1 text-xs text-red-600">{fieldErrors.full_name}</p>
            )}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm text-slate-700">
              Пароль <span className="text-slate-400">(не менее 8 символов)</span>
            </label>
            <input
              id="password"
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                clearFieldError("password");
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
            {submitting ? "Создаём аккаунт..." : "Зарегистрироваться"}
          </button>
        </form>

        <p className="mt-6 text-sm text-slate-500">
          Уже есть аккаунт?{" "}
          <Link to="/login" className="text-slate-900 underline underline-offset-2">
            Войти
          </Link>
        </p>
      </div>
    </div>
  );
}

function translateRegisterError(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.status === 400 && /already registered/i.test(err.message)) {
      return "Этот email уже зарегистрирован";
    }
    if (err.status === 422) return "Проверьте корректность полей";
    return err.message;
  }
  return "Не удалось зарегистрироваться";
}
