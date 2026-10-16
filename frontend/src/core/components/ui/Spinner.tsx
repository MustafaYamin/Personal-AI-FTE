const SIZE_CLASSES = {
  sm: "h-4 w-4 border-2",
  md: "h-6 w-6 border-2",
  lg: "h-10 w-10 border-4",
};

export function Spinner({ size = "md" }: { size?: keyof typeof SIZE_CLASSES }) {
  return (
    <span
      role="status"
      aria-label="Loading"
      className={`inline-block animate-spin rounded-full border-slate-300 border-t-slate-900 ${SIZE_CLASSES[size]}`}
    />
  );
}
