import PageHeader from "@/components/PageHeader";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import {
  BarChart,
  Brain,
  CheckCircle2,
  Database,
  GraduationCap,
  Scale,
  ShieldCheck,
} from "lucide-react";

export default function MethodologyPage() {
  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-8 sm:px-6">
      <PageHeader
        badge="Academic Specification"
        title="Research Methodology & Data Dictionary"
        description="Detailed formulation of panel data construction, multi-model evaluation criteria, and economic target definitions."
      />

      {/* College PBL Identification Card */}
      <Card className="border-indigo-100 bg-gradient-to-r from-blue-50 to-indigo-50">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="rounded-2xl bg-indigo-600 p-3 text-white shadow-md">
              <GraduationCap className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-indigo-700">
                PBL Academic Project
              </p>
              <h2 className="mt-1 text-xl font-bold text-navy-900">
                Predicting the Impact of El Niño on Agricultural GDP using Panel Data Machine Learning
              </h2>
              <p className="mt-1 text-sm text-slate-700">
                <strong>Institution:</strong> K. J. Somaiya Institute of Technology · Department of Artificial Intelligence and Data Science
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Methodology Pipeline Visual */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-bold text-navy-900">Analytical Pipeline Architecture</h3>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-6 text-center">
            {[
              { step: "1. Data Acquisition", desc: "NOAA ONI, Open-Meteo, RBI GSVA", icon: Database },
              { step: "2. Data Preprocessing", desc: "Range checks, state normalization", icon: CheckCircle2 },
              { step: "3. Panel Engineering", desc: "Anomalies, climate lags (t-1)", icon: Scale },
              { step: "4. Multi-Model ML", desc: "Train 5 regression models", icon: Brain },
              { step: "5. Empirical Selection", desc: "Lowest RMSE on held-out test years", icon: BarChart },
              { step: "6. Scenario Engine", desc: "Hypothetical policy simulation", icon: ShieldCheck },
            ].map((item, idx) => {
              const Icon = item.icon;
              return (
                <div key={idx} className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                  <Icon className="mx-auto h-6 w-6 text-indigo-600 mb-2" />
                  <p className="text-xs font-bold text-navy-900">{item.step}</p>
                  <p className="mt-1 text-[11px] text-slate-500">{item.desc}</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Target Variable Transparency */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-bold text-navy-900">Target Variable: Clarification &amp; Data Dictionary</h3>
        </CardHeader>
        <CardContent className="space-y-4 text-sm text-slate-700 leading-relaxed">
          <p>
            While the project title reflects the academic curriculum formulation (<em>Agricultural GDP</em>),
            official Indian economic statistical accounts publish state-level production as <strong>Gross State Value Added (GSVA) from Agriculture, Forestry, and Fishing</strong>.
          </p>
          <div className="overflow-x-auto rounded-xl border border-slate-100">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500">
                <tr>
                  <th className="px-4 py-3">Variable Name</th>
                  <th className="px-4 py-3">Official Series Description</th>
                  <th className="px-4 py-3">Units</th>
                  <th className="px-4 py-3">Source</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                <tr>
                  <td className="px-4 py-3 font-semibold text-navy-900">agricultural_gdp_cr</td>
                  <td className="px-4 py-3">Gross State Value Added from Agriculture at Constant Prices (Base 2011-12)</td>
                  <td className="px-4 py-3">₹ Crore</td>
                  <td className="px-4 py-3">Reserve Bank of India (RBI) / MoSPI</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-semibold text-navy-900">rainfall_mm</td>
                  <td className="px-4 py-3">Annual Cumulative Precipitation at State Geographic Centroid</td>
                  <td className="px-4 py-3">millimeters (mm)</td>
                  <td className="px-4 py-3">Open-Meteo Historical Archive / ECMWF ERA5</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-semibold text-navy-900">avg_temperature_c</td>
                  <td className="px-4 py-3">Annual Mean 2m Surface Air Temperature</td>
                  <td className="px-4 py-3">°Celsius</td>
                  <td className="px-4 py-3">Open-Meteo Historical Archive</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-semibold text-navy-900">oni_index</td>
                  <td className="px-4 py-3">Oceanic Niño Index (3-month SST Anomaly in Niño 3.4 Region)</td>
                  <td className="px-4 py-3">°Celsius</td>
                  <td className="px-4 py-3">NOAA Physical Sciences Laboratory</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="text-xs text-slate-500">
            * Measuring at Constant Prices (2011-12 Base) is critical because it captures real volume changes rather than inflationary price increases.
          </p>
        </CardContent>
      </Card>

      {/* Multi-Model ML Philosophy */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-bold text-navy-900">Multi-Model Selection Philosophy</h3>
        </CardHeader>
        <CardContent className="space-y-4 text-sm text-slate-700 leading-relaxed">
          <p>
            Rather than presuming that one specific algorithm (such as XGBoost or Random Forest) is uniformly optimal,
            this platform implements a competitive multi-model benchmark across 5 architectures:
          </p>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-xl border border-slate-100 p-4 bg-slate-50">
              <p className="font-bold text-navy-900 text-sm">1. Linear Regression (OLS)</p>
              <p className="mt-1 text-xs text-slate-600">Serves as the classical econometric baseline and benchmark for explainability.</p>
            </div>
            <div className="rounded-xl border border-slate-100 p-4 bg-slate-50">
              <p className="font-bold text-navy-900 text-sm">2. Random Forest Regressor</p>
              <p className="mt-1 text-xs text-slate-600">Non-linear bagging ensemble that reduces variance across noisy panel features.</p>
            </div>
            <div className="rounded-xl border border-slate-100 p-4 bg-slate-50">
              <p className="font-bold text-navy-900 text-sm">3. Gradient Boosting Regressor</p>
              <p className="mt-1 text-xs text-slate-600">Sequential boosting algorithm that iteratively fits models to pseudo-residuals.</p>
            </div>
            <div className="rounded-xl border border-slate-100 p-4 bg-slate-50">
              <p className="font-bold text-navy-900 text-sm">4. XGBoost Regressor</p>
              <p className="mt-1 text-xs text-slate-600">Extreme gradient boosting with L1/L2 regularization to prevent overfitting on collinear climate signals.</p>
            </div>
            <div className="rounded-xl border border-slate-100 p-4 bg-slate-50 md:col-span-2">
              <p className="font-bold text-navy-900 text-sm">5. Extra Trees Regressor</p>
              <p className="mt-1 text-xs text-slate-600">Extremely randomized decision trees that optimize split thresholds across candidate features for lower bias.</p>
            </div>
          </div>
          <div className="rounded-xl bg-blue-50 p-4 border border-blue-100 text-xs text-blue-900">
            <strong>Chronological Evaluation Principle:</strong> Because panel data is time-dependent, random k-fold cross validation introduces temporal leakage.
            Models are trained on earlier historical years and evaluated strictly on held-out latest test years (e.g. 2021–2023).
            The model exhibiting the minimum Root Mean Squared Error (RMSE) is automatically selected as the operational estimator.
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
