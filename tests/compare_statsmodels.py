#!/usr/bin/env python3
"""Reference decompositions via statsmodels, for comparison with
src/tsdecomp_sample.inp (gretl).

Series: Electricity from aus_production.csv (quarterly, period 4).
  1. Classical additive decomposition (seasonal_decompose)
  2. Classical with trend extrapolation (extrapolate_trend=3)
  3. STL, seasonal window 13
  4. STL, seasonal window 13, robust

Two figures are written next to this script when the gretl CSV is given:
classical_comparison.png and stl_comparison.png.

Usage: python3 tests/compare_statsmodels.py [aus_production.csv [gretl_output.csv]]

Example:
```
python3 -W ignore tests/compare_statsmodels.py \
  /home/admin-tarassow/git/forecasting_principles/data/csv/aus_production.csv \
  tests/gretl_output.csv
```
"""
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.seasonal import STL, seasonal_decompose

CSV = "/home/admin-tarassow/git/forecasting_principles/data/csv/aus_production.csv"
PERIOD = 4
S_WINDOW = 13
# stl_decompose() uses inner=2 (R's value for non-robust STL) in both the
# robust and the non-robust case, and outer=0 / 15. statsmodels' default
# for non-robust STL is inner=5, so inner is set explicitly here.
INNER = 2
OUTER_NONROBUST, OUTER_ROBUST = 0, 15
HERE = os.path.dirname(os.path.abspath(__file__))
PNG_CLASSICAL = os.path.join(HERE, "classical_comparison.png")
PNG_STL = os.path.join(HERE, "stl_comparison.png")
BLUE, ORANGE = "#2a78d6", "#eb6834"  # categorical slots 1 and 2


def frame(trend, season, resid, y):
    return pd.DataFrame({"trend": trend, "season": season,
                         "remainder": resid, "y": y})


def show(title, df):
    print(f"\n=== {title} ===")
    pd.set_option("display.float_format", lambda v: f"{v:12.4f}")
    print(df.head(10).to_string())
    print("...")
    print(df.tail(10).to_string())


def compare(gretl_csv, results):
    """Max abs / mean abs difference per component against gretl output
    (CSV with columns <prefix>_trend/_season/_rem, prefixes c, e, s, r)."""
    g = pd.read_csv(gretl_csv)
    g.index = pd.PeriodIndex(g["obs"], freq="Q")
    print("\n=== statsmodels vs gretl (abs diff, NaNs ignored) ===")
    for pre, name in [("c", "classical"), ("e", "classical+extrap"),
                      ("s", "STL"), ("r", "STL robust")]:
        df = results[pre]
        for col, gcol in [("trend", "trend"), ("season", "season"),
                          ("remainder", "rem")]:
            gc = g[f"{pre}_{gcol}"]
            d = (df[col] - gc).abs()
            nan_mismatch = (df[col].isna() != gc.isna()).sum()
            print(f"{name:18s} {col:10s} max={d.max():12.6f} "
                  f"mean={d.mean():12.6f} NaN-pattern mismatches={nan_mismatch}")


def plot_comparison(gretl_csv, results, cols, title, out):
    """3xN grid: rows = trend/season/remainder, one column per entry of
    `cols` (list of (prefix, column title)). Each subplot overlays
    statsmodels (solid) and gretl (dashed)."""
    g = pd.read_csv(gretl_csv)
    g.index = pd.PeriodIndex(g["obs"], freq="Q")
    x = g.index.to_timestamp()
    comps = [("trend", "trend"), ("season", "season"),
             ("remainder", "rem")]
    fig, axes = plt.subplots(3, len(cols), figsize=(6.5 * len(cols), 9),
                             sharex=True, squeeze=False)
    for j, (pre, col_title) in enumerate(cols):
        for i, (comp, gcol) in enumerate(comps):
            ax = axes[i, j]
            ax.plot(x, results[pre][comp].values, color=BLUE, lw=2.5,
                    label="statsmodels")
            ax.plot(x, g[f"{pre}_{gcol}"].values, color=ORANGE, lw=1.2,
                    ls="--", label="gretl")
            if i == 0:
                ax.set_title(col_title)
            if j == 0:
                ax.set_ylabel(comp)
            ax.grid(alpha=0.25)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
    axes[0, 0].legend(frameon=False, loc="upper left")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"\nPlot saved to {out}")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else CSV
    gretl_csv = sys.argv[2] if len(sys.argv) > 2 else None
    data = pd.read_csv(path, sep=";")
    idx = pd.PeriodIndex(data["Quarter"].str.replace(" ", ""), freq="Q")
    y = pd.Series(data["Electricity"].astype(float).values, index=idx,
                  name="Electricity")

    # gretl: scalar MULTIPLICATIVE = FALSE -> additive
    c = seasonal_decompose(y, model="additive", period=PERIOD)
    fc = frame(c.trend, c.seasonal, c.resid, y)
    show("Classical (additive)", fc)

    # gretl: extrapolate_trend = 3 (statsmodels: same parameter)
    ce = seasonal_decompose(y, model="additive", period=PERIOD,
                            extrapolate_trend=3)
    fe = frame(ce.trend, ce.seasonal, ce.resid, y)
    show("Classical (additive), extrapolate_trend=3", fe)

    # gretl: stl_decompose(y, defbundle("s_window", 13))
    s = STL(y, period=PERIOD, seasonal=S_WINDOW, robust=False).fit(
        inner_iter=INNER, outer_iter=OUTER_NONROBUST)
    fs = frame(s.trend, s.seasonal, s.resid, y)
    show(f"STL (seasonal={S_WINDOW})", fs)

    # gretl: stl_decompose(y, defbundle("s_window", 13, "robust", 1))
    r = STL(y, period=PERIOD, seasonal=S_WINDOW, robust=True).fit(
        inner_iter=INNER, outer_iter=OUTER_ROBUST)
    fr = frame(r.trend, r.seasonal, r.resid, y)
    show(f"STL (seasonal={S_WINDOW}, robust)", fr)

    if gretl_csv:
        res = {"c": fc, "e": fe, "s": fs, "r": fr}
        compare(gretl_csv, res)
        title = "aus_production: Electricity -- statsmodels vs gretl"
        plot_comparison(gretl_csv, res,
                        [("c", "Classical"),
                         ("e", "Classical, extrapolate_trend=3")],
                        title, PNG_CLASSICAL)
        plot_comparison(gretl_csv, res,
                        [("s", f"STL (seasonal={S_WINDOW})"),
                         ("r", f"STL (seasonal={S_WINDOW}), robust")],
                        title, PNG_STL)


if __name__ == "__main__":
    main()
