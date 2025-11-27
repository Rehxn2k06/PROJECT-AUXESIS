# run_compile.py
import subprocess
import sys
import re
from statistics import median
import json
from pathlib import Path
from datetime import datetime
from config import DATA_DIR, MODEL_DIR, TEST_DIR


TIME_RE = re.compile(r"took\s+([0-9.]+)")

def compile_program(src_file, flags, exe_file="a.out"):
    cmd_compile = ["g++", src_file, "-o", exe_file] + flags.split()
    proc = subprocess.run(cmd_compile, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Compile failed:\n{proc.stderr}")
    return cmd_compile

def run_and_parse_time(exe_file="a.out"):
    """Run the executable and parse the program's printed time (expects a 'took X' float)."""
    proc = subprocess.run([f"./{exe_file}"], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Program crashed:\n{proc.stderr}")
    out = proc.stdout.strip()
    # look for "took 0.01234" or similar
    m = TIME_RE.search(out)
    if not m:
        # fallback: return None and also print full output for debugging
        print("Warning: couldn't parse time from program output. Full output:\n", out)
        return None, out
    return float(m.group(1)), out

def collect_runs(src_file, flags, runs=7, exe="a.out", save_result=False):
    # 1) compile once
    compile_cmd = compile_program(src_file, flags, exe)
    # 2) run N times and collect program-reported times
    times = []
    outputs = []
    for i in range(runs):
        t, out = run_and_parse_time(exe)
        outputs.append(out)
        if t is not None:
            times.append(t)
    if not times:
        raise RuntimeError("No valid timing parsed from any runs.")
    med = median(times)
    result = {
        "src": src_file,
        "flags": flags,
        "runs": runs,
        "times": times,
        "median_time": med,
        "compile_cmd": " ".join(compile_cmd),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    print(f"Results for {src_file} {flags}")
    print("times:", times)
    print(f"median: {med:.6f} s")
    if save_result:
        p = Path(DATA_DIR / "results.json")
        arr = []
        if p.exists():
            arr = json.loads(p.read_text())
        arr.append(result)
        p.write_text(json.dumps(arr, indent=2))
        print("Appended record to results.json")
    return result

if __name__ == "__main__":
    # usage: python3 run_compile.py <source.cpp> <flags...>
    if len(sys.argv) < 2:
        print("Usage: python3 run_compile.py <source.cpp> [flags...]")
        sys.exit(1)
    src = sys.argv[1]
    flags = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "-O2"
    # runs can be adjusted here
    res = collect_runs(src, flags, runs=7, save_result=True)
