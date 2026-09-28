import PipelineRunner from "@/components/PipelineRunner";
import PageHeader from "@/components/PageHeader";
import { Card, CardContent } from "@/components/ui/Card";

export default function PipelinePage() {
  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-8 sm:px-6">
      <PageHeader
        badge="Automated ETL + ML"
        title="Data Pipeline"
        description="One click downloads data from all sources, cleans the panel, stores it in Firestore, and trains Random Forest, Gradient Boosting, and XGBoost."
      />

      <PipelineRunner />

      <Card>
        <CardContent className="p-6">
          <h3 className="font-semibold text-navy-900">Data Sources</h3>
          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            <SourceCard
              name="NOAA ONI Index"
              provider="NOAA Physical Sciences Laboratory"
              desc="Oceanic Niño Index — monthly sea surface temperature anomaly, aggregated to annual values for El Niño strength."
            />
            <SourceCard
              name="Rainfall & Temperature"
              provider="Open-Meteo Archive API"
              desc="Historical daily precipitation and temperature for Indian state centroids (2009–2023), aggregated annually."
            />
            <SourceCard
              name="Agricultural GDP"
              provider="MOSPI State Accounts"
              desc="State-wise agricultural GDP reference panel (₹ Crore) joined with climate data for panel ML."
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function SourceCard({
  name,
  provider,
  desc,
}: {
  name: string;
  provider: string;
  desc: string;
}) {
  return (
    <div className="rounded-xl border border-slate-100 bg-gradient-to-br from-slate-50 to-white p-4 transition hover:shadow-md">
      <p className="font-bold text-navy-900">{name}</p>
      <p className="mt-1 text-xs font-medium text-indigo-600">{provider}</p>
      <p className="mt-2 text-sm text-slate-600 leading-relaxed">{desc}</p>
    </div>
  );
}
