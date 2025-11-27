# data_load.py
import json
import pandas as pd
from pathlib import Path
from config import DATA_DIR, MODEL_DIR, TEST_DIR


def load_results(json_path=DATA_DIR / "results.json", out_csv=DATA_DIR / "results_clean.csv"):
    with open(json_path, "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df['program'] = df['src'].str.replace('.cpp', '', regex=False)
    # ensure runtime column exists and uses median_time
    df['runtime'] = df['median_time']
    df.to_csv(out_csv, index=False)
    print(f"Saved cleaned results to {out_csv} ({len(df)} rows)")
    return df

if __name__ == "__main__":
    load_results()
