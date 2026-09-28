"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Droplets, Thermometer } from "lucide-react";
import Disclaimer from "@/components/Disclaimer";
import ErrorMessage from "@/components/ErrorMessage";
import GdpTrendChart from "@/components/GdpTrendChart";
import LoadingSpinner from "@/components/LoadingSpinner";
import PageHeader from "@/components/PageHeader";
import Button from "@/components/ui/Button";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { api, HistoryRow } from "@/lib/api";

export default function StateDetailPage() {
  const params = useParams();
  const rawState = params?.state as string;
  const stateName = decodeURIComponent(rawState || "");

  const [history, setHistory] = useState<HistoryRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!stateName) return;
    setLoading(true);
    api
      .getStateHistory(stateName)
      .then((res) => setHistory(res.history))
      .catch(() => setError(`Could not load historical records for ${stateName}`))
      .finally(() => setLoading(false));
  }, [stateName]);

  if (loading) return <LoadingSpinner label={`Loading analytics for ${stateName}…`} />;
  if (error || !history.length) {
    return (
      <div className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6">
        <Link href="/dashboard" className="inline-flex items-center gap-1.5 text-sm text-indigo-600 hover:underline">
          <ArrowLeft className="h-4 w-4" /> Back to Dashboard
        </Link>
        <ErrorMessage message={error ?? `No records found for ${stateName}`} />
      </div>
    );
  }

  const values = history.map((h) => h.agricultural_gdp_cr);
  const avgGdp = values.reduce((a, b) => a + b, 0) / values.length;
  const latestGdp = history[history.length - 1].agricultural_gdp_cr;
  const avgRain = history.reduce((a, b) => a + b.rainfall_mm, 0) / history.length;
  const avgTemp = history.reduce((a, b) => a + b.avg_temperature_c, 0) / history.length;

  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-8 sm:px-6">
      <div className="flex items-center justify-between">
        <Link href="/dashboard" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-navy-900 transition">
          <ArrowLeft className="h-4 w-4" /> Back to State Overview
        </Link>
        <Link href={`/scenario`}>
          <Button size="sm">Simulate Scenario for {stateName}</Button>
        </Link>
      </div>

      <PageHeader
        badge="State Analysis"
        title={`${stateName} — Agricultural & Climate Profile`}
        description={`Longitudinal panel analysis of agricultural output, monsoon precipitation, and ENSO correlation from ${history[0].year} to ${history[history.length - 1].year}.`}
      />

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-5">
            <p className="text-xs font-semibold uppercase text-slate-500">Historical Avg GSVA</p>
            <p className="mt-2 text-2xl font-bold text-navy-900">
              ₹{avgGdp.toLocaleString(undefined, { maximumFractionDigits: 1 })} <span className="text-xs font-normal text-slate-500">Cr</span>
            </p>
            <p className="mt-1 text-xs text-slate-500">Annual mean at constant prices</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <p className="text-xs font-semibold uppercase text-slate-500">Latest Year ({history[history.length - 1].year})</p>
            <p className="mt-2 text-2xl font-bold text-navy-900">
              ₹{latestGdp.toLocaleString(undefined, { maximumFractionDigits: 1 })} <span className="text-xs font-normal text-slate-500">Cr</span>
            </p>
            <p className={`mt-1 text-xs font-semibold ${latestGdp >= avgGdp ? "text-emerald-600" : "text-red-600"}`}>
              {latestGdp >= avgGdp ? "+" : ""}{(((latestGdp - avgGdp) / avgGdp) * 100).toFixed(1)}% vs baseline
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <p className="text-xs font-semibold uppercase text-slate-500 flex items-center gap-1">
              <Droplets className="h-3.5 w-3.5 text-blue-500" /> Avg Rainfall
            </p>
            <p className="mt-2 text-2xl font-bold text-navy-900">
              {avgRain.toFixed(1)} <span className="text-xs font-normal text-slate-500">mm/yr</span>
            </p>
            <p className="mt-1 text-xs text-slate-500">Centroid annual accumulation</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <p className="text-xs font-semibold uppercase text-slate-500 flex items-center gap-1">
              <Thermometer className="h-3.5 w-3.5 text-orange-500" /> Avg Temperature
            </p>
            <p className="mt-2 text-2xl font-bold text-navy-900">
              {avgTemp.toFixed(1)} <span className="text-xs font-normal text-slate-500">°C</span>
            </p>
            <p className="mt-1 text-xs text-slate-500">2-meter surface mean</p>
          </CardContent>
        </Card>
      </div>

      {/* Historical GDP & ONI Chart */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-bold text-navy-900">Longitudinal Output &amp; ONI Overlay</h3>
          <p className="text-xs text-slate-500">Dashed line represents the Oceanic Niño Index; solid line tracks Agricultural GSVA/GDP in ₹ Crore.</p>
        </CardHeader>
        <CardContent>
          <GdpTrendChart history={history} />
        </CardContent>
      </Card>

      {/* Historical Observations Table */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-bold text-navy-900">Historical Annual Panel Observations</h3>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto rounded-xl border border-slate-100">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500">
                <tr>
                  <th className="px-4 py-3">Year</th>
                  <th className="px-4 py-3">Rainfall (mm)</th>
                  <th className="px-4 py-3">Temperature (°C)</th>
                  <th className="px-4 py-3">ONI Index</th>
                  <th className="px-4 py-3">Agricultural Output (₹ Cr)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {history.map((row) => (
                  <tr key={row.year} className="hover:bg-slate-50">
                    <td className="px-4 py-2.5 font-bold text-navy-900">{row.year}</td>
                    <td className="px-4 py-2.5">{row.rainfall_mm.toFixed(1)}</td>
                    <td className="px-4 py-2.5">{row.avg_temperature_c.toFixed(1)}</td>
                    <td className="px-4 py-2.5">{row.oni_index.toFixed(2)}</td>
                    <td className="px-4 py-2.5 font-semibold text-navy-900">{row.agricultural_gdp_cr.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4">
            <Disclaimer />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
