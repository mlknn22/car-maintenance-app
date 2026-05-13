const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateEmail(value: string): string | null {
  if (!value.trim()) return "Введите email";
  if (!EMAIL_RE.test(value.trim())) return "Некорректный email";
  return null;
}

export function validatePassword(value: string): string | null {
  if (!value) return "Введите пароль";
  if (value.length < 8) return "Пароль должен быть не короче 8 символов";
  if (value.length > 128) return "Пароль слишком длинный";
  return null;
}
