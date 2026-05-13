interface TextFieldProps {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  error?: string;
}

export function TextField({
  label,
  value,
  onChange,
  placeholder,
  error,
}: TextFieldProps) {
  return (
    <div>
      <label className="block text-sm text-slate-700">{label}</label>
      <input
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-900 focus:outline-none"
      />
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}

interface NumberFieldProps {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
  step?: number;
  error?: string;
}

export function NumberField({
  label,
  value,
  onChange,
  min,
  max,
  step,
  error,
}: NumberFieldProps) {
  return (
    <div>
      <label className="block text-sm text-slate-700">{label}</label>
      <input
        type="number"
        value={value}
        min={min}
        max={max}
        step={step}
        onFocus={(e) => e.target.select()}
        onChange={(e) => onChange(Number(e.target.value))}
        className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-slate-900 focus:outline-none"
      />
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}

interface SelectFieldProps<T extends string> {
  label: string;
  value: T;
  onChange: (v: string) => void;
  options: Record<T, string>;
}

export function SelectField<T extends string>({
  label,
  value,
  onChange,
  options,
}: SelectFieldProps<T>) {
  return (
    <div>
      <label className="block text-sm text-slate-700">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-slate-900 focus:outline-none"
      >
        {Object.entries(options).map(([apiValue, label]) => (
          <option key={apiValue} value={apiValue}>
            {label as string}
          </option>
        ))}
      </select>
    </div>
  );
}

interface TextareaFieldProps {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  rows?: number;
  error?: string;
}

export function TextareaField({
  label,
  value,
  onChange,
  placeholder,
  rows = 3,
  error,
}: TextareaFieldProps) {
  return (
    <div>
      <label className="block text-sm text-slate-700">{label}</label>
      <textarea
        value={value}
        placeholder={placeholder}
        rows={rows}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-900 focus:outline-none"
      />
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}
