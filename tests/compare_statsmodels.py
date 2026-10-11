#!/usr/bin/env python3
"""Reference decompositions via statsmodels, for comparison with
src/decomposition_sample.inp (gretl).

Series: Electricity from aus_production.csv (quarterly, period 4).
  1. Classical additive decomposition (seasonal_decompose)
  2. Classical with trend extrapolation (extrapolate_trend=3)
  3. STL, seasonal window 13, robust

Usage: python3 tests/compare_statsmodels.py [aus_production.csv [gretl_output.csv]]
"""
import sys
import pandas as pd
from statsmodels.tsa.seasonal import STL, seasonal_decompose

CSV = "/home/admin-tarassow/git/forecasting_principles/data/csv/aus_production.csv"
PERIOD = 4
ROBUST = True
S_WINDOW = 13
# gretl's stl_decompose defaults when robust: inner=1, outer=5
# (statsmodels defaults to inner=2, outer=15)
INNER, OUTER = 1, 5


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
    (CSV with columns <prefix>_trend/_season/_rem, prefixes c, e, s)."""
    g = pd.read_csv(gretl_csv)
    g.index = pd.PeriodIndex(g["obs"], freq="Q")
    print("\n=== statsmodels vs gretl (abs diff, NaNs ignored) ===")
    for pre, name in [("c", "classical"), ("e", "classical+extrap"),
                      ("s", "STL")]:
        df = results[pre]
        for col, gcol in [("trend", "trend"), ("season", "season"),
                          ("remainder", "rem")]:
            gc = g[f"{pre}_{gcol}"]
            d = (df[col] - gc).abs()
            nan_mismatch = (df[col].isna() != gc.isna()).sum()
            print(f"{name:18s} {col:10s} max={d.max():12.6f} "
                  f"mean={d.mean():12.6f} NaN-pattern mismatches={nan_mismatch}")


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

    # gretl: stl_decompose(y, 13, 0, 0, 0, 0, ROBUST)
    s = STL(y, period=PERIOD, seasonal=S_WINDOW, robust=ROBUST).fit(
        inner_iter=INNER, outer_iter=OUTER)
    fs = frame(s.trend, s.seasonal, s.resid, y)
    show(f"STL (seasonal={S_WINDOW}, robust={ROBUST})", fs)

    if gretl_csv:
        compare(gretl_csv, {"c": fc, "e": fe, "s": fs})


if __name__ == "__main__":
    main()
