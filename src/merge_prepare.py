import pandas as pd
import numpy as np
from config import DATA_DIR, MODEL_DIR, TEST_DIR


def merge_prepare_with_baseline(results_csv=DATA_DIR / "results_clean.csv", features_csv=DATA_DIR / "features.csv", out_csv=DATA_DIR / "dataset.csv"):
    df = pd.read_csv(results_csv)
    fdf = pd.read_csv(features_csv)
    df = df.merge(fdf, on='src', how='left')

    # encode flags as before
    all_flags = ['-O1','-O2','-O3','-Ofast','-Os','-funroll-loops','-ftree-vectorize','-ffast-math','-march','-flto']
    for fl in all_flags:
        df[f'has_{fl}'] = df['flags'].astype(str).str.contains(fl, na=False)

    df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')
    df = df.dropna(subset=['runtime'])

    # --- compute baseline_O3_time per program ---
    # prefer rows where flags contains -O3; if none, fallback to min runtime for that program
    baseline_map = {}
    for prog, group in df.groupby('src'):
        o3_rows = group[group['flags'].str.contains(r'\\b-O3\\b', na=False)]
        if len(o3_rows) > 0:
            baseline_map[prog] = o3_rows['runtime'].median()   # median of O3 runs
        else:
            baseline_map[prog] = group['runtime'].min()       # fallback

    # add baseline column replicating per row
    df['baseline_O3_time'] = df['src'].map(baseline_map)

    # optional: add baseline_log for convenience
    df['baseline_log'] = np.log(df['baseline_O3_time'])

    df.to_csv(out_csv, index=False)
    print(f"Prepared dataset with baseline saved to {out_csv}, shape={df.shape}")
    return df

if __name__ == "__main__":
    merge_prepare_with_baseline()
