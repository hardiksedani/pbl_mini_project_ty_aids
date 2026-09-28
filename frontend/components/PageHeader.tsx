import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface PageHeaderProps {
  title: string;
  description?: string;
  badge?: string;
  action?: ReactNode;
  className?: string;
}

export default function PageHeader({
  title,
  description,
  badge,
  action,
  className,
}: PageHeaderProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-2xl bg-gradient-to-r from-navy-900 via-indigo-950 to-navy-900 px-6 py-8 text-white shadow-xl sm:px-8",
        className,
      )}
    >
      <div className="hero-glow absolute inset-0" />
      <div className="relative flex flex-wrap items-start justify-between gap-4">
        <div>
          {badge && (
            <span className="mb-2 inline-block rounded-full bg-blue-500/20 px-3 py-1 text-xs font-medium text-blue-200">
              {badge}
            </span>
          )}
          <h1 className="text-2xl font-bold sm:text-3xl">{title}</h1>
          {description && (
            <p className="mt-2 max-w-2xl text-sm text-slate-300 sm:text-base">
              {description}
            </p>
          )}
        </div>
        {action && <div className="shrink-0">{action}</div>}
      </div>
    </div>
  );
}
