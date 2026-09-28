"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { MODEL_LABELS, ModelName } from "@/lib/constants";

const FEATURE_LABELS: Record<string, string> = {
  rainfall_mm: "Rainfall (mm)",
  avg_temperature_c: "Temperature (°C)",
  oni_index: "ONI Index",
  rainfall_anomaly: "Rainfall Anomaly (mm)",
  temp_anomaly: "Temp Anomaly (°C)",
  lagged_rainfall_mm: "Lagged Rainfall (t-1)",
  lagged_temperature_c: "Lagged Temp (t-1)",
  lagged_oni: "Lagged ONI (t-1)",
};

interface Props {
  model: ModelName;
  importance: Record<string, number>;
}

export default function FeatureImportanceChart({ model, importance }: Props) {
  if (!importance || Object.keys(importance).length === 0) {
    return <p className="text-xs text-slate-400 py-4 text-center">Feature importance not available</p>;
  }

  const chartData = Object.keys(importance).map((key) => ({
    feature: FEATURE_LABELS[key] || key.replace(/_/g, " "),
    importance: Number(importance[key]) || 0,
  }));

  return (
    <div>
      <h3 className="mb-3 text-sm font-semibold text-navy-900">
        {MODEL_LABELS[model]} — Feature Importance
      </h3>
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis type="number" domain={[0, 1]} tick={{ fontSize: 11 }} />
            <YAxis type="category" dataKey="feature" width={120} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v) => (typeof v === "number" ? v.toFixed(3) : String(v))} />
            <Bar dataKey="importance" fill="#1e3a5f" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
