# decomposition Package

This gretl package decomposes a seasonal time series into a trend-cycle, a seasonal and a remainder component. Two methods are available:

1. Classical decomposition (additive or multiplicative), which is based on centered moving averages, via `clc_decompose()`. For more information see https://otexts.com/fpp3/classical-decomposition.html
2. STL (Seasonal-Trend decomposition using Loess), a more flexible and robust method which allows the seasonal pattern to change over time, via `stl_decompose()`. For more information see https://otexts.com/fpp3/stl.html

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

For the additive model: `y = trend + season + remainder`.
For the multiplicative model: `y = trend x season x remainder`.

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



## stl_decompose

```
stl_decompose (series y, bundle opts[null])
```

STL decomposition of a time series into trend-cycle, seasonal and remainder component using loess smoothing (locally weighted regression). The decomposition is additive: `y = trend + season + remainder`. All parameters are optional and are passed via the bundle `opts`.

The reference is: Cleveland, R. B., Cleveland, W. S., McRae, J. E., & Terpenning, I. (1990). STL: A seasonal-trend decomposition procedure based on loess. *Journal of Official Statistics*, 6(1), 3-73.

**How the method works**

Compared to classical decomposition, STL does not assume a fixed seasonal pattern: the seasonal component can change slowly over time, and the trend-cycle is available for all observations (no missing values at the edges). Let `m` denote the seasonal period (e.g. 4 for quarterly and 12 for monthly data). The algorithm iterates the following steps (the "inner loop"), starting with a trend of zero:

1. *Detrending:* subtract the current trend from the series.
2. *Cycle-subseries smoothing:* split the detrended series into `m` cycle-subseries, e.g. all Januaries, all Februaries, and so on for monthly data. Each cycle-subseries is smoothed separately by loess with span `s_window`. This yields a preliminary seasonal component.
3. *Low-pass filtering:* apply two moving averages of length `m`, one of length 3 and finally a loess smoother with span `l_window` to the preliminary seasonal component.
4. *Detrending of the seasonal component:* subtract the low-pass filtered series from the preliminary seasonal component. This removes low-frequency variation (trend) that leaked into the seasonal component. The result is the seasonal component.
5. *Seasonal adjustment:* subtract the seasonal component from the original series.
6. *Trend smoothing:* smooth the seasonally adjusted series by loess with span `t_window`. This is the new trend.

The inner loop is repeated `inner` times. If `robust` is `TRUE` (or `outer > 0`), an additional *outer loop* is run `outer` times: after each inner loop, the remainder is computed and robustness weights are derived from its size. Observations with large remainders, i.e. outliers, receive weights close to zero (bisquare function of the remainder divided by six times its median absolute value). The weights enter the loess smoothers in steps 2 and 6 of the next inner loop, which then starts from the current trend. Hence, outliers hardly affect the trend and the seasonal component and end up in the remainder.

**Arguments:**

- `y`: series, Series to decompose. The series must have a seasonal frequency and contain at least three full seasonal cycles (`3 * m` observations). Many more cycles are needed to estimate a changing seasonal pattern reliably: the seasonal smoother works on cycle-subseries with only one value per cycle. Missing values at the sample edges are ignored with a warning.
- `opts`: bundle, Optional parameters. **You can pass the following parameters:**

    * `s_window`: int, Span of the loess smoother in step 2 (default: `11`, as in R's `STL()`). See the explanations below.
    * `t_window`: int, Span of the loess smoother for the trend in step 6. The default `0` sets the smallest odd integer greater than or equal to `1.5 * m / (1 - 1.5 / s_window)`.
    * `l_window`: int, Span of the loess smoother of the low-pass filter in step 3. The default `0` sets the smallest odd integer greater than or equal to `m`.
    * `inner`: int, Number of inner loop iterations. The default `0` sets `2`.
    * `outer`: int, Number of outer loop (robustness) iterations. The default `0` sets `0` if `robust` is `FALSE` and `15` if `robust` is `TRUE`.
    * `robust`: bool, If `TRUE`, robustness weights are used to reduce the influence of outliers (default: `FALSE`).

**Choosing the parameters**

All spans (`s_window`, `t_window`, `l_window`) should be odd integers and measure a number of observations. A larger span means a smoother estimate, a smaller span means a more flexible estimate that follows the data more closely.

- `s_window` controls how quickly the seasonal pattern may change. In step 2 it counts observations *within a cycle-subseries*, i.e. years for monthly or quarterly data, not months or quarters. A small value (3 or 5) lets the seasonal pattern evolve quickly but may pick up noise. A large value gives a stable seasonal pattern which changes only slowly from year to year. The value must be at least 3; the default of `11` is the one used by R's `STL()`; Cleveland et al. (1990) use 35 for a stable monthly series, and 7 is a common choice if the seasonal pattern changes quickly. Try different values and inspect the seasonal component, e.g. by `plot_decompose()`: it should neither be erratic nor ignore a visible change in the seasonal amplitude.
- `t_window` controls the smoothness of the trend-cycle. A larger value gives a smoother trend, a smaller value lets it follow short-term movements, which then no longer show up in the remainder. The default is the smallest odd integer greater than or equal to `1.5 * m / (1 - 1.5 / s_window)`, the rule suggested by Cleveland et al. (1990) which prevents trend and seasonal component from competing for the same variation (for instance `7` for quarterly and `21` for monthly data if `s_window = 11`). It works well in most cases. Increase it if the trend is too wiggly.
- `l_window` only affects the low-pass filter. The default is almost always appropriate.
- `inner` and `outer`: Two inner iterations are usually sufficient. If the data contain outliers (e.g. due to strikes, one-off events or measurement errors), use `robust = TRUE`; this increases the computation time as the weighted loess has to be recomputed `outer` times. You may also set `outer` directly: a positive value runs the outer loop with that many iterations. Without outliers, the non-robust default is fine.

**Comparison with the defaults of R and Python**

R's `STL()` (package `feasts`, used in the book "Forecasting: Principles and Practice") calls `stats::stl()`; Python's `statsmodels.tsa.seasonal.STL` is another reference.

- `s_window`: 11 in R's `STL()` (it must be odd and at least 7 there), 7 in statsmodels, 11 here.
- `t_window` and `l_window`: the same rule as in R. statsmodels uses the smallest odd integer *greater than* `m` for `l_window`, which differs only for odd `m`.
- `inner`: R uses 2 for non-robust and 1 for robust STL, statsmodels 5 for non-robust and 2 for robust STL. Here, 2 is used in both cases. The non-robust value agrees with R. For robust STL, the value of 2 follows statsmodels: with `inner = 1` our results differed considerably more from statsmodels (mean absolute difference of the trend of about 75 instead of 0.6 for quarterly data with values up to about 59,000). If you need to replicate R's robust results exactly, set `inner = 1`.
- `outer`: 0 for non-robust and 15 for robust STL, as in R and statsmodels.
- Degrees of the local polynomials: the loess smoothers use local linear regression (degree one) throughout. R uses a locally constant fit (degree zero) for the seasonal smoother by default, hence the seasonal component can differ slightly from R's.
- Speed-up by linear interpolation (`jump` in R) is not used: loess is evaluated at every observation.

**Return:** Bundle holding various items.

- `trend`: series, Trend-cycle component.
- `season`: series, Seasonal component.
- `remainder`: series, Remainder component.
- `y`: series, The decomposed series.
- `frequency`: scalar, Seasonal period of the data.
- `nobs`: scalar, Number of observations used.
- `multiplicative`: bool, Always `FALSE`: the decomposition is additive.
- `s_window`, `t_window`, `l_window`, `inner`, `outer`, `robust`: The parameters actually used, after replacing the automatic defaults.

The returned bundle can be passed to `plot_decompose()`.

**Multiplicative decomposition:** STL is additive. If the seasonal swings grow with the level of the series (see below), decompose the logarithm of the series (which requires strictly positive values) and transform the components back (as is also done with Python's `statsmodels.tsa.seasonal.STL`):

```
series ly = log(y)
bundle Model = stl_decompose(ly, _(s_window=13))
series trend = exp(Model.trend)
series season = exp(Model.season)
series remainder = exp(Model.remainder)    # y = trend * season * remainder
```

**Note:** The implementation follows Cleveland et al. (1990) with one simplification: the cycle-subseries are not extended by one value at each end before smoothing. Hence, results can differ slightly from other STL implementations at the edges of the sample. A comparison with Python's `statsmodels.tsa.seasonal.STL` for quarterly data (using the same parameters) gave very similar results.


## plot_decompose

```
plot_decompose (series target, bundle Model, bundle opts[null])
```

Plot the components of a decomposition as a grid plot with three rows: (1) the actual series together with the trend-cycle, (2) the seasonal component and (3) the remainder component. Each subplot has its own title. The seasonal and the remainder subplots include a horizontal reference line at zero (additive model) or at one (multiplicative model).

**Arguments:**

- `target`: series, The series that was decomposed.
- `Model`: bundle, Model object returned by the `*_decompose()` function.
- `opts`: bundle, Optional parameters for controlling the plot. **You can pass the following parameters:**

    * `output`: string, Path and name of the file to save the plot. The file type is determined by the file extension (e.g. `.png` or `.pdf`). If not provided, the plot is shown on the screen (default: show on screen).
    * `layout`: string, Arrangement of the plots (default: `vertical`). `vertical`: one grid plot with the three plots below each other. `horizontal`: one grid plot with the three plots side by side. `separate`: three individual plots (data and trend-cycle, seasonal component, remainder component). When saving separate plots to file, the suffix `_trend`, `_season` or `_remainder` is inserted before the file extension of `output`, e.g. `decomposition.png` is saved as `decomposition_trend.png`, `decomposition_season.png` and `decomposition_remainder.png`. Without `output` the plots are shown on the screen one after another.
    * `title`: string, Overall title of the plot (default: no title). Ignored for `separate` plots, as each plot has its own title.
    * `width`: scalar, Width of the plot in pixels. For `separate` plots, the width of each plot. Default: `800` (`vertical`), `1200` (`horizontal`) and `600` (`separate`).
    * `height`: scalar, Height of the plot in pixels. For `separate` plots, the height of each plot. Default: `900` (`vertical`) and `400` (`horizontal` and `separate`).
    * `linewidth`: scalar, Line width (default: 1.0).
    * `monochrome`: bool, If `TRUE`, draw black lines only. The trend-cycle and the reference lines are then distinguished by their dash pattern (default: `FALSE`).
    * `grid`: bool, If `TRUE`, show grid lines (default: `TRUE`).

**Return:** Scalar, `0` if no error occurred, otherwise `1`.



# Interpretation of the components

Let `y` be the series, e.g. units sold per month, and let `trend`, `season` and `remainder` be the components returned by `clc_decompose()` or `stl_decompose()`. The components of `stl_decompose()` follow the additive interpretation.

## Additive model

```
y = trend + season + remainder
```

- `trend`: the underlying level, in the units of `y` (e.g. units sold per month).
- `season`: the seasonal effect in units of `y`, centered such that the indices sum to zero over one cycle. A value of `+64` for July means that July sales are on average 64 units above the underlying level. The effect is the same number of units in every year, irrespective of the level of the series.
- `remainder`: the deviation from `trend + season` in units of `y`.
- Seasonally adjusted series: `y - season`.

The additive model is appropriate if the size of the seasonal swings stays roughly constant as the level of the series changes.

## Multiplicative model

```
y = trend * season * remainder
```

- `trend`: the underlying level, in the units of `y`. It is of a similar magnitude as in the additive model.
- `season`: a dimensionless seasonal index, centered such that the indices average to one over one cycle. A value of `1.23` for July means that July sales are on average 23% above the underlying level, whatever that level is. A value below one means that the season is weaker than average.
- `remainder`: a dimensionless factor, fluctuating around one. A value of `0.95` means that the observation is 5% below the value expected from trend and season, a value of `1.03` means 3% above.
- Seasonally adjusted series: `y / season`. This series is in the units of `y`.

The multiplicative model is appropriate if the seasonal swings grow (or shrink) in proportion to the level of the series, i.e. if the seasonal effect is a constant percentage rather than a constant number of units. In this case, the remainder of an additive model typically becomes larger when the level of the series rises, whereas the multiplicative remainder stays at a similar relative size.

## Converting the multiplicative components to units

The dimensionless components can be expressed in the units of `y`:

```
seasonal effect in units = trend * (season - 1)
remainder in units       = y - trend * season
```

In contrast to the additive model, the seasonal effect in units varies over time with the level of the trend. For instance, a seasonal index of `1.23` corresponds to `+29` units at a trend of `127` units and to `+110` units at a trend of `475` units.

## Choosing between the two models

Plot the series. If the seasonal swings widen as the level rises, use the multiplicative model (`multiplicative = TRUE`), otherwise use the additive model. Both are linked via logarithms: the multiplicative model for `y` is the additive model for `log(y)`, as `log(y) = log(trend) + log(season) + log(remainder)`. The multiplicative model requires strictly positive values of `y`.


# Changelog

* **v0.1 (October 2026)**
    * initial release: classical decomposition via `clc_decompose()` (including optional trend extrapolation), STL decomposition via `stl_decompose()` and the plot function `plot_decompose()`
