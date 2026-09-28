export const MODEL_NAMES = [
  "linear_regression",
  "random_forest",
  "gradient_boosting",
  "xgboost",
  "extra_trees",
] as const;

export type ModelName = (typeof MODEL_NAMES)[number];

export const MODEL_LABELS: Record<ModelName, string> = {
  linear_regression: "Linear Regression (OLS)",
  random_forest: "Random Forest",
  gradient_boosting: "Gradient Boosting",
  xgboost: "XGBoost",
  extra_trees: "Extra Trees",
};

export const MODEL_DESCRIPTIONS: Record<ModelName, string> = {
  linear_regression:
    "Standard Ordinary Least Squares (OLS) linear benchmark. Provides interpretable coefficients without overfitting.",
  random_forest:
    "Ensemble of randomized decision trees. Handles non-linear climate interactions and feature variances robustly.",
  gradient_boosting:
    "Sequential gradient tree boosting. Minimizes residual loss iteratively on tabular panel data.",
  xgboost:
    "Regularized extreme gradient boosting. Highly efficient and regularized against multicollinearity.",
  extra_trees:
    "Extremely randomized trees ensemble. Randomizes cut-points to achieve lower variance on small-to-medium panels.",
};

export const DISCLAIMER =
  "This platform provides analytical estimates based on historical climate and economic data and machine-learning models. Results are not official government forecasts and should not be interpreted as proof that El Niño alone determines agricultural economic performance.";

export const ONI_PRESETS = [
  { label: "La Niña (Cool / Excess)", value: -1.2, desc: "Above-average monsoon rainfall expected" },
  { label: "Neutral ENSO", value: 0.0, desc: "Normal climatic patterns" },
  { label: "Weak El Niño", value: 0.8, desc: "Mild monsoon deficit (-5% to -10%)" },
  { label: "Moderate El Niño", value: 1.5, desc: "Noticeable monsoon deficit (-15% to -20%)" },
  { label: "Strong El Niño", value: 2.2, desc: "Severe monsoon deficit (-25% to -35%)" },
];
