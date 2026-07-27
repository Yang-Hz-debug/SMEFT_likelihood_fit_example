#!/usr/bin/env python3
"""
Extract SMEFT results (CHB, CHW) from MultiDimFit scan output.

Usage:
  python3 make_smeft_results.py \\
    --scandir smeft_outputs/Run3_full/scans \\
    --mass 125 \\
    --out-json smeft_results.json

Parses higgsCombine_scan_CHB.MultiDimFit.mH125.root (1D CHB scan)
and higgsCombine_scan_CHW.MultiDimFit.mH125.root (1D CHW scan)
to extract 68% and 95% CL intervals.
Also plots 1D scans and 2D contours if data available.
"""
import argparse
import json
import glob
import numpy as np
import uproot
import os


def read_scan(rootfile: str, poi: str):
    """Read a 1D scan from a Combine MultiDimFit output (profiled likelihood)."""
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
    d -= np.min(d)

    return x, d


def read_scan_2d(rootfile: str):
    """Read a 2D scan from a Combine MultiDimFit output."""
    try:
        with uproot.open(rootfile) as f:
            if "limit" not in f:
                return None, None, None
            arr = f["limit"].arrays(["CHB", "CHW", "deltaNLL"], library="np")
    except Exception as e:
        print(f"[WARN] Cannot read 2D scan {rootfile}: {e}")
        return None, None, None

    x = np.asarray(arr["CHB"], dtype=float)
    y = np.asarray(arr["CHW"], dtype=float)
    d = np.asarray(arr["deltaNLL"], dtype=float)

    mask = np.isfinite(x) & np.isfinite(y) & np.isfinite(d)
    x, y, d = x[mask], y[mask], d[mask]
    if len(x) < 4:
        return None, None, None

    d -= np.min(d)
    return x, y, d


def interval_cl(x: np.ndarray, d: np.ndarray, target: float):
    """Extract CL interval (ΔNLL = target) from profiled likelihood scan."""
    i0 = int(np.argmin(d))
    x0 = float(x[i0])
    xmin, xmax = float(np.min(x)), float(np.max(x))

    lo = hi = None
    for i in range(i0 - 1, -1, -1):
        if (d[i] - target) * (d[i + 1] - target) <= 0:
            lo = float(np.interp(target, [d[i], d[i + 1]], [x[i], x[i + 1]]))
            break
    for i in range(i0 + 1, len(x)):
        if (d[i - 1] - target) * (d[i] - target) <= 0:
            hi = float(np.interp(target, [d[i - 1], d[i]], [x[i - 1], x[i]]))
            break

    if lo is None: lo = xmin
    if hi is None: hi = xmax

    return {
        "best_fit": x0,
        "err_down": max(0.0, x0 - lo),
        "err_up": max(0.0, hi - x0),
        "low": lo,
        "high": hi,
        "truncated_low": lo <= xmin + 1e-6 * (xmax - xmin),
        "truncated_high": hi >= xmax - 1e-6 * (xmax - xmin),
    }


def plot_1d_scan(x, d, poi_name, label, outpath):
    """Plot 1D scan using matplotlib."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print(f"[WARN] matplotlib not available, skip 1D plot for {poi_name}")
        return

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(x, d, 'b-', linewidth=2)
    ax.axhline(0.5, color='gray', linestyle='--', alpha=0.5, label=r'68% CL ($\Delta$NLL=0.5)')
    ax.axhline(1.92, color='gray', linestyle=':', alpha=0.5, label=r'95% CL ($\Delta$NLL=1.92)')
    ax.axvline(0, color='red', linestyle='-', alpha=0.3, label='SM (0)')
    ax.set_ylim(-0.001, 7)  # 根据你的数据调整上限
    i0 = np.argmin(d)
    ax.plot(x[i0], d[i0], 'k*', markersize=10, label=f'best fit ({x[i0]:.2f})')

    ax.set_xlabel(f"${poi_name}$")
    ax.set_ylabel(r"$\Delta$NLL")
    ax.set_title(f"SMEFT 1D scan — {poi_name} ({label})")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(f"{outpath}.pdf", bbox_inches="tight")
    fig.savefig(f"{outpath}.png", bbox_inches="tight", dpi=150)
    print(f"[OK] Wrote {outpath}.pdf / .png")
    plt.close(fig)


def plot_2d_contours(scandir: str, mass: int = 125, outname: str = "smeft_2d_contour"):
    """Generate 2D contour plot from scan ROOT file."""
    scan_2d = f"{scandir}/higgsCombine_scan_2D.MultiDimFit.mH{mass}.root"
    files_2d = glob.glob(scan_2d)
    if not files_2d:
        print("[INFO] No 2D scan file found for plotting")
        return

    x, y, d = read_scan_2d(files_2d[0])
    if x is None:
        print("[WARN] Cannot read 2D scan")
        return

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[WARN] matplotlib not available, skipping 2D plot")
        return

    try:
        unique_x = np.sort(np.unique(x))
        unique_y = np.sort(np.unique(y))
        nx, ny = len(unique_x), len(unique_y)

        fig, ax = plt.subplots(figsize=(8, 7))

        if nx * ny == len(x):
            Z = d.reshape(ny, nx)
            cf = ax.contourf(unique_x, unique_y, Z,
                             levels=np.arange(0, min(Z.max() + 0.5, 10), 0.5),
                             cmap="YlOrRd", extend="max")
            cbar = fig.colorbar(cf, ax=ax, label=r"$\Delta$NLL")

            if Z.max() > 2.3:
                cs68 = ax.contour(unique_x, unique_y, Z, levels=[2.30],
                                  colors="blue", linewidths=2, linestyles="--")
                ax.clabel(cs68, fmt={2.30: r"68% CL"})
            if Z.max() > 5.99:
                cs95 = ax.contour(unique_x, unique_y, Z, levels=[5.99],
                                  colors="red", linewidths=2, linestyles="--")
                ax.clabel(cs95, fmt={5.99: r"95% CL"})
        else:
            sc = ax.scatter(x, y, c=d, cmap="YlOrRd", s=30, edgecolors="none")
            cbar = fig.colorbar(sc, ax=ax, label=r"$\Delta$NLL")

        i0 = np.argmin(d)
        ax.plot(x[i0], y[i0], "k*", markersize=12, label=f"best fit ({x[i0]:.2f}, {y[i0]:.2f})")
        ax.plot(0, 0, "ko", markersize=8, label="SM (0, 0)")

        ax.set_xlabel(r"$C_{HB}$")
        ax.set_ylabel(r"$C_{HW}$")
        ax.set_title("SMEFT 2D scan — " + os.path.basename(scandir))
        ax.legend(loc="upper right")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(f"{outname}.pdf", bbox_inches="tight")
        fig.savefig(f"{outname}.png", bbox_inches="tight", dpi=150)
        print(f"[OK] Wrote {outname}.pdf / {outname}.png")
        plt.close(fig)
    except Exception as e:
        print(f"[WARN] 2D plotting failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    ap = argparse.ArgumentParser(description="Extract SMEFT scan results")
    ap.add_argument("--scandir", required=True, help="Directory with scan ROOT files")
    ap.add_argument("--mass", type=int, default=125)
    ap.add_argument("--out-json", default="smeft_results.json")
    ap.add_argument("--plot-dir", default=None, help="Directory for output plots (default: same as scandir)")
    ap.add_argument("--target-68", type=float, default=0.5, help="ΔNLL for 68% CL")
    ap.add_argument("--target-95", type=float, default=1.92, help="ΔNLL for 95% CL")
    args = ap.parse_args()

    plot_dir = args.plot_dir if args.plot_dir else args.scandir
    os.makedirs(plot_dir, exist_ok=True)

    results = {}

    for poi in ["CHB", "CHW"]:
        scan = f"{args.scandir}/higgsCombine_scan_{poi}.MultiDimFit.mH{args.mass}.root"
        files = glob.glob(scan)
        if not files:
            print(f"[WARN] Missing scan for {poi}: {scan}")
            results[poi] = {"error": "scan file not found"}
            continue

        x, d = read_scan(files[0], poi)
        if x is None:
            print(f"[WARN] Cannot read scan for {poi}")
            results[poi] = {"error": "cannot read scan"}
            continue

        r_68 = interval_cl(x, d, args.target_68)
        r_95 = interval_cl(x, d, args.target_95)

        results[poi] = {
            "best_fit": r_68["best_fit"],
            "err68_down": r_68["err_down"],
            "err68_up": r_68["err_up"],
            "cl68_low": r_68["low"],
            "cl68_high": r_68["high"],
            "cl95_low": r_95["low"],
            "cl95_high": r_95["high"],
            "truncated_low": r_68["truncated_low"],
            "truncated_high": r_68["truncated_high"],
        }

        print(f"[OK] {poi}: best_fit={r_68['best_fit']:.4f}, "
              f"68% = [{r_68['low']:.4f}, {r_68['high']:.4f}], "
              f"95% = [{r_95['low']:.4f}, {r_95['high']:.4f}]")

        # Save scan data for external use
        results[f"{poi}_scan_x"] = x.tolist()
        results[f"{poi}_scan_y"] = d.tolist()
        results[f"{poi}_scan_file"] = files[0]

        # Plot 1D scan
        label = os.path.basename(args.scandir.rstrip('/'))
        plot_1d_scan(x, d, poi, label, os.path.join(plot_dir, f"smeft_scan_{label}_{poi}"))

    # 2D scan
    scan_2d = f"{args.scandir}/higgsCombine_scan_2D.MultiDimFit.mH{args.mass}.root"
    files_2d = glob.glob(scan_2d)
    if files_2d:
        print(f"[OK] 2D scan file found: {files_2d[0]}")
        results["2D_scan_file"] = files_2d[0]

        x2, y2, d2 = read_scan_2d(files_2d[0])
        if x2 is not None:
            results["2D_CHB"] = x2.tolist()
            results["2D_CHW"] = y2.tolist()
            results["2D_deltaNLL"] = d2.tolist()

            i0 = np.argmin(d2)
            print(f"[OK] 2D best fit: CHB={x2[i0]:.4f}, CHW={y2[i0]:.4f}, ΔNLL={d2[i0]:.4f}")
            results["2D_contour_68"] = 2.30
            results["2D_contour_95"] = 5.99

        # Plot 2D contours
        label = os.path.basename(args.scandir.rstrip('/'))
        plot_2d_contours(args.scandir, args.mass, os.path.join(plot_dir, f"smeft_2d_contour_{label}"))
    else:
        print("[INFO] No 2D scan file found")

    with open(args.out_json, "w") as f:
        json.dump(results, f, indent=2)

    print(f"[OK] wrote {args.out_json}")


if __name__ == "__main__":
    main()