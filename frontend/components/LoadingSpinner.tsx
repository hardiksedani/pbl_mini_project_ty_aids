export default function LoadingSpinner({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 py-8 text-slate-600">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-navy-700 border-t-transparent" />
      <span>{label}</span>
    </div>
  );
}
