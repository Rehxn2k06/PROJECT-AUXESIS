# feature_extract.py
import re
import json
import pandas as pd
from pathlib import Path
from config import DATA_DIR, MODEL_DIR, TEST_DIR


# Try common directories where your .cpp files might live.
# Add or change entries if you keep source files in other folders.
SEARCH_DIRS = [TEST_DIR]

def find_source_path(prog_name):
    """
    Try to locate the source file for prog_name by checking SEARCH_DIRS.
    Returns Path if found, else None.
    """
    for d in SEARCH_DIRS:
        p = d / prog_name
        if p.exists():
            return p
    return None

def extract_static_features(src_list, out_csv="features.csv"):
    rows = []
    for prog in src_list:
        # prog might be just a filename (e.g. "matmul.cpp") or a path
        prog_path = Path(prog)
        if prog_path.exists():
            src_path = prog_path
        else:
            src_path = find_source_path(prog_path.name)

        if not src_path or not src_path.exists():
            print("Missing:", prog)
            continue

        text = src_path.read_text()

        num_for = len(re.findall(r'\bfor\b', text))
        num_while = len(re.findall(r'\bwhile\b', text))
        num_if = len(re.findall(r'\bif\b', text))
        # heuristic for function-like patterns (will overcount sometimes)
        num_funcs = len(re.findall(r'\b[a-zA-Z0-9_]+\s*\(', text))
        num_brackets = text.count('[')
        loc = len(text.splitlines())

        # simple type tags (manual mapping for these benchmarks)
        name = src_path.name.lower()
        if 'matmul' in name:
            ptype = 'compute'
        elif 'convolution' in name:
            ptype = 'stencil'
        elif 'pointer' in name:
            ptype = 'memory'
        elif 'sort_big' in name or 'sort' in name:
            ptype = 'sort'
        elif 'string_parse' in name or 'string' in name or 'token' in name:
            ptype = 'text'
        else:
            ptype = 'unknown'

        rows.append({
            'src': src_path.name,
            'num_for': num_for,
            'num_while': num_while,
            'num_if': num_if,
            'num_funcs': num_funcs,
            'num_brackets': num_brackets,
            'loc': loc,
            'ptype': ptype,
            'resolved_path': str(src_path)
        })

    fdf = pd.DataFrame(rows)
    fdf.to_csv(out_csv, index=False)
    print(f"Saved features to {out_csv} ({len(fdf)} programs)")
    return fdf

if __name__ == "__main__":
    # Read sources referenced in results.json (safe and deterministic)
    if not Path(DATA_DIR / "results.json").exists():
        print("results.json not found — please ensure you ran experiments and results.json exists.")
        raise SystemExit(1)

    with open(DATA_DIR / "results.json") as f:
        data = json.load(f)
    srcs = sorted({r['src'] for r in data})
    print("Found programs in results.json:", srcs)

    extract_static_features(srcs)
