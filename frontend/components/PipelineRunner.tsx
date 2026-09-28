"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight,
  CheckCircle2,
  CloudDownload,
  Database,
  Loader2,
  Sparkles,
  Trash2,
  XCircle,
} from "lucide-react";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { api, ApiError, PipelineStatus } from "@/lib/api";
import { MODEL_LABELS } from "@/lib/constants";

const STEPS = [
  { key: "downloading", label: "Download Sources", icon: CloudDownload },
  { key: "cleaning", label: "Data Cleaning", icon: Trash2 },
  { key: "storing", label: "Store to Database", icon: Database },
  { key: "training", label: "Train ML Models", icon: Sparkles },
  { key: "done", label: "Complete", icon: CheckCircle2 },
];

export default function PipelineRunner() {
  const [status, setStatus] = useState<PipelineStatus | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadStatus = useCallback(async () => {
    try {
      const s = await api.getPipelineStatus();
      setStatus(s);
      if (s.status === "running") {
        setRunning(true);
      } else if (s.status === "completed" || s.status === "failed") {
        setRunning(false);
      }
      return s;
    } catch {
      return null;
    }
  }, []);

  useEffect(() => {
    loadStatus();
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [loadStatus]);

  function startPolling() {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      const s = await loadStatus();
      if (s && (s.status === "completed" || s.status === "failed")) {
        if (pollRef.current) clearInterval(pollRef.current);
        pollRef.current = null;
        setRunning(false);
        if (s.status === "failed" && s.error) {
          setError(s.error);
        }
      }
    }, 2500);
  }

  async function runPipeline() {
    setRunning(true);
    setError(null);
    try {
      const res = await api.runPipeline();
      setStatus(res);
      startPolling();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Pipeline failed to start");
      setRunning(false);
    }
  }

  const currentStep =
    status?.status === "completed"
      ? "done"
      : running
        ? status?.current_step ?? "downloading"
        : status?.current_step ?? "idle";
  const stepIndex = STEPS.findIndex((s) => s.key === currentStep);
  const isComplete = status?.status === "completed";

  return (
    <div className="space-y-6">
      <Card className="overflow-hidden border-0 bg-gradient-to-br from-navy-900 via-indigo-950 to-navy-900 text-white shadow-2xl shadow-indigo-900/30">
        <CardContent className="relative p-8">
          <div className="hero-glow absolute inset-0" />
          <div className="relative">
            <Badge variant="info" className="mb-4 bg-blue-500/20 text-blue-200">
              Automated Pipeline
            </Badge>
            <h2 className="text-2xl font-bold sm:text-3xl">
              Download → Clean → Train
            </h2>
            <p className="mt-2 max-w-xl text-slate-300">
              Fetches live data from NOAA (ONI), Open-Meteo (rainfall &amp;
              temperature), and MOSPI reference GDP — cleans the panel, stores it,
              and trains Random Forest, Gradient Boosting, and XGBoost automatically.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Button
                onClick={runPipeline}
                disabled={running}
                size="lg"
                className="shadow-blue-500/40"
              >
                {running ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Pipeline running…
                  </>
                ) : (
                  <>
                    <CloudDownload className="h-4 w-4" />
                    Run Full Pipeline
                  </>
                )}
              </Button>
              {isComplete && (
                <Link href="/predict">
                  <Button variant="secondary" size="lg">
                    Go to Predictions
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              )}
            </div>
            {error && (
              <div className="mt-4 flex items-start gap-2 rounded-xl bg-red-500/20 px-4 py-3 text-sm text-red-200">
                <XCircle className="mt-0.5 h-4 w-4 shrink-0" />
                {error}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-navy-900">Pipeline Progress</h3>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            {STEPS.map((step, i) => {
              const Icon = step.icon;
              const done = stepIndex > i || isComplete;
              const active = stepIndex === i && running;
              return (
                <div
                  key={step.key}
                  className="flex flex-1 flex-col items-center text-center"
                >
                  <div
                    className={`flex h-12 w-12 items-center justify-center rounded-2xl transition-all ${
                      done
                        ? "bg-emerald-100 text-emerald-600 shadow-sm"
                        : active
                          ? "bg-blue-100 text-blue-600 ring-2 ring-blue-400 ring-offset-2"
                          : "bg-slate-100 text-slate-400"
                    }`}
                  >
                    {active ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : done ? (
                      <CheckCircle2 className="h-5 w-5" />
                    ) : (
                      <Icon className="h-5 w-5" />
                    )}
                  </div>
                  <span
                    className={`mt-2 text-xs font-semibold ${done || active ? "text-navy-900" : "text-slate-400"}`}
                  >
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <AnimatePresence>
        {status?.sources && status.sources.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-navy-900">Data Sources</h3>
              </CardHeader>
              <CardContent>
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {status.sources.map((src) => (
                    <div
                      key={src.source}
                      className="rounded-xl border border-slate-100 bg-gradient-to-br from-slate-50 to-white p-4 transition hover:shadow-md"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <p className="font-semibold text-navy-900">{src.source}</p>
                        <Badge variant={src.status === "success" ? "success" : "danger"}>
                          {src.status}
                        </Badge>
                      </div>
                      <p className="mt-1 text-xs text-slate-500">{src.provider}</p>
                      {src.records != null && (
                        <p className="mt-2 text-sm font-medium text-indigo-700">
                          {src.records} records
                        </p>
                      )}
                      {src.detail && (
                        <p className="mt-1 text-xs text-slate-500">{src.detail}</p>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {status?.cleaning && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-navy-900">Cleaning Report</h3>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-4">
              <Stat label="Rows in" value={status.cleaning.rows_in} />
              <Stat label="Rows out" value={status.cleaning.rows_out} />
              <Stat label="Dropped" value={status.cleaning.rows_dropped} />
              <Stat label="Imputed cells" value={status.cleaning.imputed_cells} />
            </div>
            {status.cleaning.steps && (
              <ul className="mt-4 space-y-1">
                {status.cleaning.steps.map((s) => (
                  <li key={s} className="flex items-center gap-2 text-sm text-slate-600">
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                    {s}
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      )}

      {status?.training && (
        <Card className="border-emerald-200 bg-gradient-to-br from-emerald-50 to-white">
          <CardHeader>
            <h3 className="text-lg font-semibold text-emerald-900">
              All Models Trained Successfully
            </h3>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-emerald-800">
              Best model:{" "}
              <strong>{MODEL_LABELS[status.training.best_model]}</strong> · RMSE{" "}
              {status.training.models[status.training.best_model].rmse.toFixed(2)} ₹ Cr
            </p>
            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              {Object.entries(status.training.models).map(([name, m]) => (
                <div
                  key={name}
                  className="rounded-xl border border-emerald-100 bg-white p-4 shadow-sm"
                >
                  <p className="text-xs font-medium text-slate-500">
                    {MODEL_LABELS[name as keyof typeof MODEL_LABELS]}
                  </p>
                  <p className="mt-1 text-2xl font-bold text-navy-900">
                    R² {m.r2.toFixed(3)}
                  </p>
                  <p className="text-xs text-slate-500">
                    RMSE {m.rmse.toFixed(2)} · MAE {m.mae.toFixed(2)}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl bg-slate-50 p-4 text-center">
      <p className="text-2xl font-bold text-navy-900">{value}</p>
      <p className="text-xs text-slate-500">{label}</p>
    </div>
  );
}
