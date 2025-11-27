# recommend_flags.py
"""
Recommend compiler flag combos for a given C++ source using a saved surrogate model.
- Assumes model predicts log(runtime / baseline_O3_time) (i.e., relative log).
- By default loads XGB model from Model/xgb_model.joblib (can override with --model).
"""

import argparse
import itertools
import math
import re
import subprocess
from pathlib import Path
from statistics import median
import joblib
import numpy as np
import pandas as pd
from config import DATA_DIR, MODEL_DIR, TEST_DIR


# Candidate flags (tweak as you like)
FLAG_CANDIDATES = [
    "-O1", "-O2", "-O3", "-Ofast", "-Os",
    "-funroll-loops", "-ftree-vectorize", "-ffast-math",
    "-march=native", "-flto"
]

# ---- Helpers: compile & run, parse program-reported time ----
TIME_RE = re.compile(r"took\s+([0-9.]+)")

def compile_program(src: Path, flags, exe="a.out"):
    cmd = ["g++", str(src), "-o", exe] + flags
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode == 0, proc.stderr

def run_program_capture(src_exe="./a.out"):
    """Run the program and return stdout text and wall time fallback."""
    import time
    t0 = time.time()
    proc = subprocess.run([str(src_exe)], capture_output=True, text=True)
    t1 = time.time()
    return proc.returncode == 0, proc.stdout, proc.stderr, (t1 - t0)

def parse_reported_time(stdout: str):
    m = TIME_RE.search(stdout)
    if m:
        try:
            return float(m.group(1))
        except:
            return None
    return None

# ---- Measure baseline using -O3: compile + run multiple times, return median ----
def measure_baseline_O3(src: Path, runs=5, exe="baseline.out"):
    ok, err = compile_program(src, ["-O3"], exe=exe)
    if not ok:
        raise RuntimeError(f"Failed to compile baseline -O3: {err}")
    times = []
    for i in range(runs):
        ok, out, err, wall = run_program_capture("./"+exe)
        if not ok:
            raise RuntimeError(f"Program crashed on baseline run: {err}")
        t = parse_reported_time(out)
        if t is None:
            # fallback to wall time if program didn't print microbenchmark
            t = wall
        times.append(t)
    return median(times)

# ---- Static feature extraction (must match training) ----
import re as _re
FUNC_RE = _re.compile(r'\b[a-zA-Z0-9_]+\s*\(')

def extract_static_for_file(src: Path):
    text = src.read_text()
    num_for = len(_re.findall(r'\bfor\b', text))
    num_while = len(_re.findall(r'\bwhile\b', text))
    num_if = len(_re.findall(r'\bif\b', text))
    num_funcs = len(FUNC_RE.findall(text))
    num_brackets = text.count('[')
    loc = len(text.splitlines())
    name = src.name.lower()
    if 'matmul' in name:
        ptype = 'compute'
    elif 'convolution' in name:
        ptype = 'stencil'
    elif 'pointer' in name:
        ptype = 'memory'
    elif 'sort' in name:
        ptype = 'sort'
    elif 'string' in name:
        ptype = 'text'
    else:
        ptype = 'unknown'
    return {
        'src': src.name,
        'num_for': num_for,
        'num_while': num_while,
        'num_if': num_if,
        'num_funcs': num_funcs,
        'num_brackets': num_brackets,
        'loc': loc,
        'ptype': ptype
    }

# ---- Build model input row (must match training X_cols) ----
ALL_FLAGS_FOR_MODEL = ['-O1','-O2','-O3','-Ofast','-Os','-funroll-loops',
                       '-ftree-vectorize','-ffast-math','-march','-flto']

def build_feature_row(static_feats, flags_list, baseline):
    # base numeric features
    row = {
        'num_for': static_feats['num_for'],
        'num_while': static_feats['num_while'],
        'num_if': static_feats['num_if'],
        'num_funcs': static_feats['num_funcs'],
        'num_brackets': static_feats['num_brackets'],
        'loc': static_feats['loc'],
        'baseline_O3_time': baseline,
        'baseline_log': math.log(baseline) if baseline>0 else 0.0
    }
    # flag binary indicators as used in training
    for fl in ALL_FLAGS_FOR_MODEL:
        row[f'has_{fl}'] = (fl in flags_list)
    return row

# ---- Enumerate combos ----
def enumerate_flag_combos(max_size=2):
    combos = []
    for r in range(1, max_size+1):
        for c in itertools.combinations(FLAG_CANDIDATES, r):
            combos.append(list(c))
    return combos

# ---- Main CLI ----
def main():
    p = argparse.ArgumentParser()
    p.add_argument("src", help="Path to C++ source file")
    p.add_argument("--max-size", type=int, default=2, help="max combo size")
    p.add_argument("--topk", type=int, default=5, help="how many top combos to show")
    p.add_argument("--verify", action="store_true", help="compile & run top combos to verify")
    p.add_argument("--model", default=str(MODEL_DIR / "xgb_model_main.joblib"), help="path to saved surrogate model (default: XGB model in Model/)")
    args = p.parse_args()

    src = Path(args.src)
    if not src.exists():
        print("Source not found:", src)
        return

    # load model
    model = joblib.load(args.model)
    FEATURE_COLUMNS = model.feature_names_in_

    # 1) measure baseline (cheap single-run calibration)
    print("Measuring baseline with -O3 (5 runs, median)...")
    baseline = measure_baseline_O3(src, runs=5, exe="baseline.out")
    print(f"Baseline (-O3) median runtime: {baseline:.6f} s")

    # 2) extract static features
    static_feats = extract_static_for_file(src)

    # 3) enumerate combos and predict
    combos = enumerate_flag_combos(max_size=args.max_size)
    rows = []
    for flags in combos:
        feat = build_feature_row(static_feats, flags, baseline)
        Xrow = pd.DataFrame([feat])[FEATURE_COLUMNS]  # single-row DF to match training input columns
        # ensure columns order / presence: model expects the same training columns.
        # If your model expects fewer columns, sklearn will still accept columns subset
        # but order should match training columns; using DataFrame is convenient.
        pred_log_rel = float(model.predict(Xrow)[0])  # predicted log(runtime/baseline)
        pred_runtime = float(math.exp(pred_log_rel) * baseline)
        rows.append({"flags": " ".join(flags), "pred_runtime": pred_runtime, "pred_log_rel": pred_log_rel})

    rows = sorted(rows, key=lambda x: x["pred_runtime"])
    print(f"\nTop {args.topk} predicted combos for {src.name}:")
    for r in rows[:args.topk]:
        print(f"  {r['flags']:<40} --> predicted runtime {r['pred_runtime']:.6f} s (log_rel {r['pred_log_rel']:.4f})")

    # 4) Optional verification
    if args.verify:
        print("\nVerifying by compiling & running the top combos (this will run them):")
        for r in rows[:args.topk]:
            flags = r['flags'].split()
            print("Compiling with:", flags)
            ok, err = compile_program(src, flags, exe="a.out")
            if not ok:
                print(" Compile error:", err)
                continue
            ok, out, err, wall = run_program_capture("./a.out")
            if not ok:
                print(" Program crashed:", err)
                continue
            measured = parse_reported_time(out) or wall
            print(" Program output (first line):")
            print(out.splitlines()[:3])
            print(f" Measured time: {measured:.6f} s")
            print("-"*40)

if __name__ == "__main__":
    main()
