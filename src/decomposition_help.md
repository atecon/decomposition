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



## plot_decompose

```
plot_decompose (series target, bundle Model, bundle opts[null])
```

Plot the components of a decomposition as a grid plot with three rows: (1) the actual series together with the trend-cycle, (2) the seasonal component and (3) the remainder component. Each subplot has its own title. The seasonal and the remainder subplots include a horizontal reference line at zero (additive model) or at one (multiplicative model).

**Arguments:**

- `target`: series, The series that was decomposed.
- `Model`: bundle, Model object returned by the `clc_decompose()` function.
- `opts`: bundle, Optional parameters for controlling the plot. **You can pass the following parameters:**

    * `output`: string, Path and name of the file to save the plot. The file type is determined by the file extension (e.g. `.png` or `.pdf`). If not provided, the plot is shown on the screen (default: show on screen).
    * `title`: string, Overall title of the plot (default: no title).
    * `width`: scalar, Width of the plot in pixels (default: 800).
    * `height`: scalar, Height of the plot in pixels (default: 900).
    * `linewidth`: scalar, Line width (default: 1.0).
    * `monochrome`: bool, If `TRUE`, draw black lines only. The trend-cycle and the reference lines are then distinguished by their dash pattern (default: `FALSE`).
    * `grid`: bool, If `TRUE`, show grid lines (default: `TRUE`).

**Return:** Scalar, `0` if no error occurred, otherwise `1`.



# Interpretation of the components

Let `y` be the series, e.g. units sold per month, and let `trend`, `season` and `remainder` be the components returned by `clc_decompose()`.

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
    * initial release: classical decomposition via `clc_decompose()` (including optional trend extrapolation) and the plot function `plot_decomposition()`
