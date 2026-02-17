export default function Input({ label, value, onChange, type = "text", placeholder }) {
  return (
    <label className="block">
      <div className="mb-2 text-xs sm:text-sm font-medium text-slate-200">{label}</div>
      <input
        className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs sm:text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        type={type}
        placeholder={placeholder}
        autoComplete="off"
      />
    </label>
  );
}

