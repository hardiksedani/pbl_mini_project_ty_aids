"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { CloudRain, Droplets, Thermometer, Waves } from "lucide-react";
import Disclaimer from "@/components/Disclaimer";
import ErrorMessage from "@/components/ErrorMessage";
import LoadingSpinner from "@/components/LoadingSpinner";
import PageHeader from "@/components/PageHeader";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { api, ApiError, ModelComparison, PredictResponse, StateSummary } from "@/lib/api";
import { MODEL_LABELS, MODEL_NAMES, ONI_PRESETS } from "@/lib/constants";

function impactLabel(pct: number): string {
  if (pct <= -20) return "severe negative";
  if (pct <= -10) return "moderate negative";
  if (pct < 0) return "mild negative";
  if (pct <= 5) return "stable";
  return "positive";
}

function buildInterpretation(
  result: PredictResponse,
  metrics: ModelComparison | null,
  rainfall: number,
  temperature: number,
  oni: number,
): string {
  const avgImpact =
    result.predictions.reduce((s, p) => s + p.predicted_impact_pct, 0) /
    result.predictions.length;

  let driver = "climate inputs";
  if (metrics?.best_model) {
    const fi = metrics.models[metrics.best_model].feature_importance;
    const entries = [
      { key: "rainfall", imp: fi.rainfall_mm, dev: rainfall },
      { key: "temperature", imp: fi.avg_temperature_c, dev: temperature },
      { key: "ONI index", imp: fi.oni_index, dev: oni },
    ];
    entries.sort((a, b) => b.imp * Math.abs(b.dev) - a.imp * Math.abs(a.dev));
    driver = entries[0].key;
  }

  return `This represents a ${impactLabel(avgImpact)} impact on Agricultural GDP, driven primarily by ${driver} under the scenario you entered.`;
}

export default function PredictPage() {
  const [states, setStates] = useState<StateSummary[]>([]);
  const [metrics, setMetrics] = useState<ModelComparison | null>(null);
  const [state, setState] = useState("");
  const [rainfall, setRainfall] = useState(700);
  const [temperature, setTemperature] = useState(30);
  const [oniIndex, setOniIndex] = useState(1.5);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [pageLoading, setPageLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.getStates(),
      api.getModelComparison().catch(() => null),
    ])
      .then(([statesRes, metricsRes]) => {
        setStates(statesRes.states);
        if (statesRes.states.length) setState(statesRes.states[0].state);
        setMetrics(metricsRes);
      })
      .catch((e) =>
        setError(e instanceof ApiError ? e.message : "Failed to load form data"),
      )
      .finally(() => setPageLoading(false));
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.predict({
        state,
        rainfall,
        temperature,
        oni_index: oniIndex,
      });
      setResult(res);
    } catch (e) {
      setError(
        e instanceof ApiError
          ? e.message
          : "Prediction failed. Run the Data Pipeline first to train models.",
      );
    } finally {
      setLoading(false);
    }
  }

  if (pageLoading) return <LoadingSpinner label="Loading prediction tool…" />;

  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-8 sm:px-6">
      <PageHeader
        badge="Scenario Analysis"
        title="Predict Agricultural GDP Impact"
        description="Enter rainfall, temperature, and El Niño (ONI) conditions — compare predictions from all three ML models side by side."
      />

      {states.length === 0 && (
        <Card className="border-amber-200 bg-amber-50">
          <CardContent className="py-8 text-center">
            <p className="font-medium text-amber-900">No data available yet</p>
            <p className="mt-1 text-sm text-amber-800">
              Run the automated pipeline to download data and train models.
            </p>
            <Link href="/pipeline" className="mt-4 inline-block">
              <Button>Go to Data Pipeline</Button>
            </Link>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <h3 className="flex items-center gap-2 text-lg font-semibold text-navy-900">
            <CloudRain className="h-5 w-5 text-indigo-500" />
            Climate Scenario
          </h3>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-6">
            <div className="grid gap-5 sm:grid-cols-2">
              <label className="block">
                <span className="text-sm font-medium text-slate-700">State</span>
                <select
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                  className="mt-1.5 w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm shadow-sm focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                  required
                >
                  {states.map((s) => (
                    <option key={s.state} value={s.state}>
                      {s.state}
                    </option>
                  ))}
                </select>
              </label>

              <label className="block">
                <span className="flex items-center gap-1.5 text-sm font-medium text-slate-700">
                  <Droplets className="h-4 w-4 text-blue-500" />
                  Rainfall (mm)
                </span>
                <input
                  type="number"
                  value={rainfall}
                  onChange={(e) => setRainfall(Number(e.target.value))}
                  className="mt-1.5 w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm shadow-sm focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                  min={0}
                  step={0.1}
                  required
                />
              </label>

              <label className="block">
                <span className="flex items-center gap-1.5 text-sm font-medium text-slate-700">
                  <Thermometer className="h-4 w-4 text-orange-500" />
                  Temperature (°C)
                </span>
                <input
                  type="number"
                  value={temperature}
                  onChange={(e) => setTemperature(Number(e.target.value))}
                  className="mt-1.5 w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm shadow-sm focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                  step={0.1}
                  required
                />
              </label>

              <div className="block sm:col-span-2">
                <span className="flex items-center gap-1.5 text-sm font-medium text-slate-700">
                  <Waves className="h-4 w-4 text-cyan-500" />
                  ONI Index — El Niño strength
                </span>
                <input
                  type="range"
                  min={-2}
                  max={3}
                  step={0.1}
                  value={oniIndex}
                  onChange={(e) => setOniIndex(Number(e.target.value))}
                  className="mt-3 w-full accent-indigo-600"
                />
                <div className="mt-2 flex justify-between text-xs text-slate-500">
                  <span>La Niña (−2)</span>
                  <span className="rounded-full bg-indigo-100 px-3 py-1 font-bold text-indigo-700">
                    {oniIndex.toFixed(1)}
                  </span>
                  <span>Strong El Niño (+3)</span>
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {ONI_PRESETS.map((p) => (
                    <button
                      key={p.label}
                      type="button"
                      onClick={() => setOniIndex(p.value)}
                      className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:border-indigo-300 hover:bg-indigo-50"
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <Button type="submit" disabled={loading || !state} size="lg">
              {loading ? "Predicting…" : "Predict Agricultural GDP"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {error && <ErrorMessage message={error} />}

      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-navy-900">
                Results for {result.state}
              </h3>
              <p className="text-sm text-slate-600">
                Historical average:{" "}
                <strong>{result.historical_avg_gdp_cr.toFixed(1)} ₹ Cr</strong>
              </p>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {MODEL_NAMES.map((name) => {
                  const pred = result.predictions.find((p) => p.model === name);
                  if (!pred) return null;
                  const isNegative = pred.predicted_impact_pct < -10;
                  return (
                    <div
                      key={name}
                      className={`rounded-2xl border p-5 transition hover:shadow-lg ${
                        isNegative
                          ? "border-red-200 bg-gradient-to-br from-red-50 to-white"
                          : "border-slate-200 bg-gradient-to-br from-slate-50 to-white"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-slate-500">
                          {MODEL_LABELS[name]}
                        </p>
                        {metrics?.best_model === name && (
                          <Badge variant="success">Best</Badge>
                        )}
                      </div>
                      <p className="mt-3 text-3xl font-bold text-navy-900">
                        {pred.predicted_gdp_cr.toFixed(1)}
                        <span className="ml-1 text-base font-normal text-slate-500">
                          ₹ Cr
                        </span>
                      </p>
                      <p
                        className={`mt-2 text-sm font-semibold ${
                          pred.predicted_impact_pct < 0
                            ? "text-red-700"
                            : "text-emerald-700"
                        }`}
                      >
                        {pred.predicted_impact_pct > 0 ? "+" : ""}
                        {pred.predicted_impact_pct.toFixed(1)}% vs. avg
                      </p>
                    </div>
                  );
                })}
              </div>

              {result.ensemble_gdp_cr != null && (
                <p className="mt-6 rounded-xl bg-indigo-50 px-4 py-3 text-sm text-indigo-900">
                  Ensemble average across all models:{" "}
                  <strong>{result.ensemble_gdp_cr.toFixed(1)} ₹ Cr</strong>
                </p>
              )}

              <p className="mt-4 rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
                {buildInterpretation(result, metrics, rainfall, temperature, oniIndex)}
              </p>

              <Disclaimer />
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
