# eval_checks.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from scipy.stats import spearmanr
from collections import defaultdict
import joblib, math
from xgboost import XGBRegressor
from config import DATA_DIR, MODEL_DIR, TEST_DIR


df = pd.read_csv(DATA_DIR / "dataset.csv")

# feature columns used in training (adjust if different)
ALL_FLAGS = ['-O1','-O2','-O3','-Ofast','-Os','-funroll-loops','-ftree-vectorize','-ffast-math','-march','-flto']
X_cols = ['num_for','num_while','num_if','num_funcs','num_brackets','loc','baseline_O3_time','baseline_log'] + [f'has_{f}' for f in ALL_FLAGS]
X_cols = [c for c in X_cols if c in df.columns]

# quick train/test split metric
X = df[X_cols].fillna(0)
y = np.log(df['runtime'].values) - np.log(df['baseline_O3_time'].values)  # log-rel target
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42)
m = XGBRegressor(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.7,
    objective='reg:squarederror',
    tree_method="hist",
    n_jobs=4)
m.fit(Xtr, ytr)
ypred = m.predict(Xte)
# convert back to seconds for reporting
baseline_te = np.exp(np.log(df.loc[Xte.index, 'baseline_O3_time'].values))
yte_runtime = baseline_te * np.exp(yte)
ypred_runtime = baseline_te * np.exp(ypred)
print("Train R2 (log-rel):", m.score(Xtr, ytr))
print("Test R2 (runtime scale):", r2_score(yte_runtime, ypred_runtime))
print("Test RMSE (seconds):", np.sqrt(mean_squared_error(yte_runtime, ypred_runtime)))

# Leave-One-Program-Out evaluation: measure Spearman + top-k hit rate
programs = df['src'].unique()
spearman_scores = []
top1 = top3 = 0
for prog in programs:
    train_df = df[df['src'] != prog]
    test_df  = df[df['src'] == prog]
    if len(test_df) < 2 or len(train_df) < 10:
        continue
    Xtr = train_df[X_cols].fillna(0)
    ytr = np.log(train_df['runtime'].values) - np.log(train_df['baseline_O3_time'].values)
    Xtest = test_df[X_cols].fillna(0)
    ytest_rel = np.log(test_df['runtime'].values) - np.log(test_df['baseline_O3_time'].values)
    model = XGBRegressor(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.7,
    objective='reg:squarederror',
    tree_method="hist",
    n_jobs=4)
    model.fit(Xtr, ytr)
    ypred_rel = model.predict(Xtest)
    # compare ordering
    ytest_runtime = test_df['baseline_O3_time'].values * np.exp(ytest_rel)
    ypred_runtime = test_df['baseline_O3_time'].values * np.exp(ypred_rel)
    # Spearman
    rho, _ = spearmanr(ypred_runtime, ytest_runtime)
    if np.isfinite(rho):
        spearman_scores.append(rho)
    # top-k hit (k=3)
    idx_best_true = np.argmin(ytest_runtime)
    topk_idx = np.argsort(ypred_runtime)[:3]
    if idx_best_true == np.argmin(ypred_runtime):
        top1 += 1
    if idx_best_true in topk_idx:
        top3 += 1

n = len(spearman_scores)
print("LOO Spearman mean:", np.mean(spearman_scores) if n else None, "count:", n)
print("LOO top-1 hits:", top1, "top-3 hits:", top3, "out of", n)

# Save quick model
joblib.dump(m,MODEL_DIR / "debug_last_model_xgb.joblib")
print("Saved debug_last_model_xgb.joblib")
