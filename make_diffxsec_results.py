#!/usr/bin/env python3
import argparse
import glob
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import uproot


# ============================================================
# Truth pT(H) bins (must match POI naming and sigma-sm JSON)
# ============================================================
PT_BINS: Dict[str, Tuple[float, Optional[float]]] = {
    "0_60":    (0.0, 60.0),
    "60_120":  (60.0, 120.0),
    "120_200": (120.0, 200.0),
    "200_300": (200.0, 300.0),
    "300_450": (300.0, 450.0),
    "450_inf": (450.0, None),
}
ORDER = list(PT_BINS.keys())


# ============================================================
# Container for one POI interval
# ============================================================
@dataclass
class IntervalResult:
    rhat: float
    err_down: float
    err_up: float
    truncated_low: bool
    truncated_high: bool
    reached_left: bool
    reached_right: bool


# ============================================================
# Read Combine 1D scan
# ============================================================
def read_scan(rootfile: str, poi: str):
    try:
        with uproot.open(rootfile) as f:
            if "limit" not in f:
                return None, None
            arr = f["limit"].arrays([poi, "deltaNLL"], library="np")
    except Exception as e:
        print(f"[WARN] Cannot read {rootfile}: {e}")
        return None, None

    x = np.asarray(arr[poi], dtype=float)
    d = np.asarray(arr["deltaNLL"], dtype=float)

    mask = np.isfinite(x) & np.isfinite(d)
    x, d = x[mask], d[mask]
    if len(x) < 5:
        return None, None

    idx = np.argsort(x)
    x, d = x[idx], d[idx]
    d -= np.min(d)  # normalize

    return x, d


# ============================================================
# Extract 68% CL interval (ΔNLL = 0.5)
# ============================================================
def interval_68(x: np.ndarray, d: np.ndarray, target: float = 0.5) -> IntervalResult:
    i0 = int(np.argmin(d))
    x0 = float(x[i0])

    xmin, xmax = float(np.min(x)), float(np.max(x))

    lo = hi = None
    reached_left = reached_right = False

    # left
    for i in range(i0 - 1, -1, -1):
        if (d[i] - target) * (d[i + 1] - target) <= 0:
            lo = float(np.interp(target, [d[i], d[i + 1]], [x[i], x[i + 1]]))
            reached_left = True
            break

    # right
    for i in range(i0 + 1, len(x)):
        if (d[i - 1] - target) * (d[i] - target) <= 0:
            hi = float(np.interp(target, [d[i - 1], d[i]], [x[i - 1], x[i]]))
            reached_right = True
            break

    truncated_low = lo is None
    truncated_high = hi is None

    if lo is None:
        lo = xmin
    if hi is None:
        hi = xmax

    return IntervalResult(
        rhat=x0,
        err_down=max(0.0, x0 - lo),
        err_up=max(0.0, hi - x0),
        truncated_low=truncated_low,
        truncated_high=truncated_high,
        reached_left=reached_left,
        reached_right=reached_right,
    )


# ============================================================
# Load SM cross sections
# ============================================================
def load_sigma_sm(path: str) -> Dict[str, float]:
    with open(path) as f:
        data = json.load(f)

    out = {}
    for b in data.get("bins", []):
        out[str(b["pt_bin"])] = float(b["sigma_SM_pb"])
    #    out[str(b["pt_bin"])] = float(b["sigma_SM_pb"])
    return out


# ============================================================
# Main
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scandir", required=True)
    ap.add_argument("--sigma-sm", required=True)
    ap.add_argument("--mass", type=int, default=125)
    ap.add_argument("--ptmax-overflow", type=float, default=1000.0)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--pois", nargs="+", required=True)
    ap.add_argument("--target", type=float, default=0.5)
    args = ap.parse_args()

    sigma_sm = load_sigma_sm(args.sigma_sm)
    rows: List[dict] = []

    for poi in args.pois:
        if not poi.startswith("r_pTH_"):
            continue

        ptbin = poi.replace("r_pTH_", "")
        if ptbin not in PT_BINS or ptbin not in sigma_sm:
            continue

        lo_pt, hi_pt = PT_BINS[ptbin]
        width = (hi_pt - lo_pt) if hi_pt else (args.ptmax_overflow - lo_pt)

        scan = f"{args.scandir}/higgsCombine_scan_{poi}.MultiDimFit.mH{args.mass}.root"
        files = glob.glob(scan)
        if not files:
            print(f"[WARN] Missing scan for {poi}")
            continue

        x, d = read_scan(files[0], poi)
        if x is None:
            continue

        if np.nanmax(d) < args.target:
            print(f"[WARN] {poi}: ΔNLL never reaches {args.target} (TRUNCATED)")

        res = interval_68(x, d, args.target)

        sig_sm = sigma_sm[ptbin]

        sigma_hat = res.rhat * sig_sm
        sigma_dn = res.err_down * sig_sm
        sigma_up = res.err_up * sig_sm

        rows.append({
            "pt_bin": ptbin,
            "pt_low": lo_pt,
            "pt_high": hi_pt if hi_pt else args.ptmax_overflow,
            "width_GeV": width,

            "r_hat": res.rhat,
            "r_err_down": res.err_down,
            "r_err_up": res.err_up,

            "sigma_SM_pb": sig_sm,
            "sigma_hat_pb": sigma_hat,
            "sigma_err_down_pb": sigma_dn,
            "sigma_err_up_pb": sigma_up,

            "dsigma_dpT_hat_pb_per_GeV": sigma_hat / width,
            "dsigma_dpT_err_down_pb_per_GeV": sigma_dn / width,
            "dsigma_dpT_err_up_pb_per_GeV": sigma_up / width,

            "truncated_low": res.truncated_low,
            "truncated_high": res.truncated_high,
            "scan_file": files[0],
        })

    rows.sort(key=lambda r: ORDER.index(r["pt_bin"]))
    df = pd.DataFrame(rows)
    df.to_csv(args.out_csv, index=False)

    with open(args.out_json, "w") as f:
        json.dump(rows, f, indent=2)

    print(f"[OK] wrote {args.out_csv}")
    print(f"[OK] wrote {args.out_json}")

    n_trunc = sum(r["truncated_low"] or r["truncated_high"] for r in rows)
    if n_trunc:
        print(f"[WARN] {n_trunc}/{len(rows)} bins are truncated → interpret as limits")


if __name__ == "__main__":
    main()
