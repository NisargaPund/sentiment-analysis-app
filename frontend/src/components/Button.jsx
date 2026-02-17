export default function Button({ children, onClick, type = "button", disabled }) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-xs sm:text-sm font-semibold text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50 w-full sm:w-auto"
    >
      {children}
    </button>
  );
}

