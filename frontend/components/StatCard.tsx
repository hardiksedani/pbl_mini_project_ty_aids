interface StatCardProps {
  label: string;
  value: string | number;
  unit?: string;
  accent?: boolean;
}

export default function StatCard({
  label,
  value,
  unit,
  accent = false,
}: StatCardProps) {
  return (
    <div
      className={`rounded-lg border p-5 shadow-sm ${
        accent
          ? "border-risk-500/30 bg-risk-50"
          : "border-slate-200 bg-white"
      }`}
    >
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p
        className={`mt-2 text-2xl font-bold ${
          accent ? "text-risk-700" : "text-navy-900"
        }`}
      >
        {value}
        {unit && (
          <span className="ml-1 text-base font-normal text-slate-500">
            {unit}
          </span>
        )}
      </p>
    </div>
  );
}
