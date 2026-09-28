"use client";

import { useEffect, useMemo, useState } from "react";
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
} from "react-simple-maps";
import { scaleLinear } from "d3-scale";

const GEO_URL =
  "https://raw.githubusercontent.com/udit-001/india-maps-data/main/geojson/india_states.geojson";

/** Map GeoJSON state names to our dataset names where they differ. */
const STATE_NAME_MAP: Record<string, string> = {
  "NCT of Delhi": "Delhi",
  "Andaman and Nicobar": "Andaman and Nicobar Islands",
  "Andaman and Nicobar Islands": "Andaman and Nicobar Islands",
  "Jammu and Kashmir": "Jammu & Kashmir",
  "Dadra and Nagar Haveli and Daman and Diu": "Dadra and Nagar Haveli",
  Telangana: "Telangana",
};

interface Props {
  /** state name → impact % (negative = risk) */
  impactByState: Record<string, number>;
  onStateClick?: (state: string) => void;
  selectedState?: string;
}

export default function IndiaChoropleth({
  impactByState,
  onStateClick,
  selectedState,
}: Props) {
  const [geoData, setGeoData] = useState<object | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(GEO_URL)
      .then((r) => {
        if (!r.ok) throw new Error("Could not load map data");
        return r.json();
      })
      .then(setGeoData)
      .catch(() => setError("Map data unavailable. Check network connection."));
  }, []);

  const values = Object.values(impactByState);
  const colorScale = useMemo(() => {
    const min = values.length ? Math.min(...values, -30) : -30;
    const max = values.length ? Math.max(...values, 10) : 10;
    return scaleLinear<string>()
      .domain([min, 0, max])
      .range(["#b91c1c", "#22c55e", "#15803d"]);
  }, [values]);

  if (error) {
    return (
      <div className="flex h-96 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-sm text-slate-600">
        {error}
      </div>
    );
  }

  if (!geoData) {
    return (
      <div className="flex h-96 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-sm text-slate-600">
        Loading map…
      </div>
    );
  }

  return (
    <div>
      <ComposableMap
        projection="geoMercator"
        projectionConfig={{ scale: 900, center: [82, 23] }}
        width={700}
        height={600}
        className="mx-auto w-full max-w-3xl"
      >
        <ZoomableGroup center={[82, 23]} zoom={1}>
          <Geographies geography={geoData}>
            {({ geographies }) =>
              geographies.map((geo) => {
                const rawName =
                  geo.properties.ST_NM ??
                  geo.properties.NAME_1 ??
                  geo.properties.name ??
                  "";
                const mappedName = STATE_NAME_MAP[rawName] ?? rawName;
                const impact = impactByState[mappedName];
                const fill =
                  impact !== undefined ? colorScale(impact) : "#e2e8f0";
                const isSelected = selectedState === mappedName;

                return (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    fill={fill}
                    stroke={isSelected ? "#1e3a5f" : "#fff"}
                    strokeWidth={isSelected ? 1.5 : 0.5}
                    style={{
                      default: { outline: "none" },
                      hover: { outline: "none", opacity: 0.85, cursor: "pointer" },
                      pressed: { outline: "none" },
                    }}
                    onClick={() => {
                      if (impact !== undefined && onStateClick) {
                        onStateClick(mappedName);
                      }
                    }}
                  />
                );
              })
            }
          </Geographies>
        </ZoomableGroup>
      </ComposableMap>
      <div className="mt-3 flex flex-wrap items-center justify-center gap-4 text-xs text-slate-600">
        <span className="flex items-center gap-1">
          <span className="inline-block h-3 w-6 rounded bg-[#b91c1c]" />
          High negative impact
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-3 w-6 rounded bg-[#22c55e]" />
          Stable / positive
        </span>
        <span className="text-slate-400">Click a highlighted state to select</span>
      </div>
    </div>
  );
}
