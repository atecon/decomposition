# decomposition Package

This package decomposes a seasonal time series into a trend-cycle, a seasonal and a remainder component using classical decomposition (additive or multiplicative), which is based on centered moving averages. For more information see:

https://otexts.com/fpp3/classical-decomposition.html

The series must have a seasonal (periodic) frequency, e.g. quarterly or monthly data. The seasonal period is taken from the dataset frequency.

Please ask questions and report bugs on the Gretl mailing list if possible. Alternatively, create an issue ticket on the github repo (see below).
Source code and test script(s) can be found here: https://github.com/atecon/decomposition


# Public Functions

## clc_decompose

```
clc_decompose (series y, bundle opts[null])
```

Classical decomposition of a time series into trend-cycle, seasonal and remainder component.

The trend-cycle is estimated by a centered moving average (an m-MA if the seasonal period m is odd, a 2xm-MA if m is even). The seasonal component is the average of the detrended series for each season, centered such that the seasonal indices sum to zero (additive) or average to one (multiplicative). The remainder is what is left over. Missing values at the sample edges are ignored with a warning. The series must contain at least two full seasonal cycles.

For the additive model: `y = trend + season + remainder`. For the multiplicative model: `y = trend * season * remainder`.

**Arguments:**

- `y`: series, Series to decompose.
- `opts`: bundle, Optional parameters. **You can pass the following parameters:**

    * `multiplicative`: bool, If `TRUE` use the multiplicative model, otherwise the additive model (default: `FALSE`).
    * `extrapolate_trend`: int, If greater than zero, the trend-cycle is linearly extrapolated into the missing values which the moving average leaves at both ends of the series. A line is fitted by OLS to the nearest `extrapolate_trend + 1` valid trend points at each end. As the seasonal and remainder components are computed from the trend, they are then also available at the edges. A larger value gives a smoother, less noise-sensitive extrapolation. The default `0` leaves the missing values in place (default: `0`).

**Return:** Bundle holding various items.

- `trend`: series, Trend-cycle component.
- `season`: series, Seasonal component.
- `remainder`: series, Remainder component.
- `y`: series, The decomposed series.
- `frequency`: scalar, Seasonal period of the data.
- `nobs`: scalar, Number of observations used.
- `multiplicative`: bool, Model type used.
- `extrapolate_trend`: int, Number of extra points used for extrapolating the trend.

**Note:** Without trend extrapolation the first and last `m/2` observations of `trend` and `remainder` are missing (`m` is the seasonal period).


# Changelog

* **v0.1 (October 2026)**
    * initial release: classical decomposition via `clc_decompose()` (including optional trend extrapolation)
