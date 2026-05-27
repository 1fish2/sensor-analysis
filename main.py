import marimo

__generated_with = "0.23.6"
app = marimo.App(app_title="CO₂ sensor comparison")


@app.cell
def _(mo):
    mo.md(r"""
    # 📊 CO2 Sensor Comparison Dashboard
    This interactive notebook loads CO2 sensor data, filters noise using a moving average, interpolates over dropouts, and compares metrics (DC offset, Tracking Variation STD, Pearson correlation) between different sensors.
    """)
    return


@app.cell
def _():
    from pathlib import Path
    import polars as pl
    import marimo as mo

    return Path, mo, pl


@app.cell
def _(Path):
    SOURCE = Path("data") / "baseline2_CO2_data_2026-05-24_1157.csv"
    TIMESTAMP_COL = "DateTime"
    FAVORITES = ["0A", "10A", "10B", "20B", "SP1", "SP3"]
    return FAVORITES, SOURCE, TIMESTAMP_COL


@app.cell
def _(averaging_slider):
    averaging_window = f"{averaging_slider.value}m"
    return (averaging_window,)


@app.cell
def _(TIMESTAMP_COL, averaging_window, pl):
    def load_data(source) -> pl.DataFrame:
        """Load and smooth the data."""
        df_raw = pl.read_csv(source, try_parse_dates=True)

        # Sort by the timestamp to ensure rolling window calculations work correctly.
        df = df_raw.sort(TIMESTAMP_COL)

        # Cast sensor columns to Float64 so initial nulls don't parse as string columns;
        # interpolate() between non-null values (or forward_fill() to repeat the last
        # non-null value);
        # then apply the rolling mean (moving average) on a 7 minute window to reduce
        # sensor noise.
        sensor_cols = [col for col in df.columns if col != TIMESTAMP_COL]
        df_filtered = df.with_columns(
            [
                pl.col(col)
                .cast(pl.Float64)
                .interpolate()
                .rolling_mean_by(TIMESTAMP_COL, window_size=averaging_window)
                for col in sensor_cols
            ]
        )

        return df_filtered

    def compare_sensors(df: pl.DataFrame, s1_name: str, s2_name: str) -> dict:
        """Align two sensors, filter dropouts, and compute metrics."""

        # Isolate columns and drop rows where either sensor has a null (dropout).
        pair_df = df.select([TIMESTAMP_COL, s1_name, s2_name]).drop_nulls(
            subset=[s1_name, s2_name]
        )

        # Create the difference expression.
        diff_expr = pl.col(s1_name) - pl.col(s2_name)

        # Compute all metrics simultaneously using Polars' fast aggregation engine.
        results = pair_df.select(
            [
                pl.len().alias("Paired Points"),
                diff_expr.mean().round(2).alias("DC Offset"),
                diff_expr.std().round(2).alias("Tracking Variation STD"),
                pl.corr(s1_name, s2_name).round(3).alias("Pearson Correlation"),
            ]
        )

        # Convert the single-row dataframe to a Python dict and add the sensor names.
        return {"Sensor 1": s1_name, "Sensor 2": s2_name} | results.to_dicts()[0]

    def cross_compare(df: pl.DataFrame, favs: list[str]) -> pl.DataFrame:
        """
        Compare each favorite sensor against all the others.
        """
        sensor_cols = [col for col in df.columns if col != TIMESTAMP_COL]

        pairs = []
        for fav in favs:
            if fav not in sensor_cols:
                continue
            pairs.extend([(fav, other) for other in sensor_cols if other != fav])

        metrics = []
        for s1, s2 in pairs:
            m = compare_sensors(df, s1, s2)
            metrics.append(m)
        return pl.DataFrame(metrics)

    def load_and_compare(source, favs: list[str]) -> pl.DataFrame:
        """
        Load the .csv sensor data and return the cross-comparison metrics.
        """
        df = load_data(source)
        return cross_compare(df, favs)

    return compare_sensors, cross_compare, load_data


@app.cell
def _(SOURCE, load_data):
    df = load_data(SOURCE)
    return (df,)


@app.cell
def _(mo):
    averaging_slider = mo.ui.slider(
        1, 15, step=1, value=7, label="Moving average window (minutes)", show_value=True
    )
    averaging_slider
    return (averaging_slider,)


@app.cell
def _(FAVORITES, cross_compare, df, mo):
    metrics_df = cross_compare(df, FAVORITES)

    cross_comparison_widget = mo.md(
        f"""
        ### Favorite Sensors Cross-Comparison Table
        Below are the comparison metrics for all favorites against other active sensors:

        {mo.as_html(metrics_df)}
        """
    )
    cross_comparison_widget
    return


@app.cell
def _(TIMESTAMP_COL, df, mo):
    sensor_names = sorted([col for col in df.columns if col != TIMESTAMP_COL])
    s1_dropdown = mo.ui.dropdown(options=sensor_names, value="0A", label="Sensor 1")
    s2_dropdown = mo.ui.dropdown(options=sensor_names, value="0B", label="Sensor 2")

    # Display the selector widgets in a row
    comparison_widget = mo.md(
        f"""
        ### Select two sensors to compare:
        {mo.hstack([s1_dropdown, s2_dropdown], justify="start", gap=2)}
        """
    )
    comparison_widget
    return comparison_widget, s1_dropdown, s2_dropdown


@app.cell
def _(compare_sensors, df, mo, s1_dropdown, s2_dropdown):
    # This runs reactively whenever s1_dropdown or s2_dropdown changes.
    s1 = s1_dropdown.value
    s2 = s2_dropdown.value

    if s1 and s2 and s1 != s2:
        metrics = compare_sensors(df, s1, s2)
        comparison_display = mo.md(
            f"""
            #### Metrics comparing all data of sensors **{s1}** and **{s2}**
            *   **Paired Points**: {metrics["Paired Points"]:,}
            *   **DC Offset (Average Difference)**: {metrics["DC Offset"]} ppm
            *   **Tracking Variation (STD of Differences)**: {metrics["Tracking Variation STD"]} ppm
            *   **Pearson Correlation**: {metrics["Pearson Correlation"]}
            """
        )
    else:
        comparison_display = mo.md("*Please select two different sensors to compare.*")
    comparison_display
    return comparison_display, s1, s2


@app.cell
def _(
    TIMESTAMP_COL,
    averaging_slider,
    comparison_display,
    comparison_widget,
    df,
    mo,
    s1,
    s2,
):
    import altair as alt

    if s1 and s2 and s1 != s2:
        # Align sensors and calculate difference
        df2 = df.select([TIMESTAMP_COL, s1, s2]).drop_nulls(subset=[s1, s2])
        plot_df = df2.with_columns((df2[s1] - df2[s2]).alias("Difference"))

        # # Filter to the last 24 hours of data
        # max_time = plot_df[TIMESTAMP_COL].max()
        # if isinstance(max_time, datetime.datetime):
        #     cutoff_time = max_time - datetime.timedelta(hours=24)
        #     plot_df = plot_df.filter(pl.col(TIMESTAMP_COL) >= cutoff_time)

        # Dynamically downsample to at most 4000 points to keep notebook outputs small
        # and prevent Altair/Marimo serialization size warnings.
        # TODO: Compare with binned averages
        # plot_df.group_by_dynamic("DateTime", every="1m").agg([plot_df.col(x).mean(), ...])
        num_rows = len(plot_df)
        if num_rows > 4000:
            step = num_rows // 4000
            plot_df = plot_df.gather_every(step)

        # Chart showing the difference
        diff_chart = (
            alt.Chart(plot_df)
            .mark_line(color="#4f46e5", strokeWidth=2)
            .encode(
                x=alt.X(f"{TIMESTAMP_COL}:T", title="Time"),
                y=alt.Y("Difference:Q", title=f"Difference ({s1} - {s2}) [ppm]"),
                tooltip=[
                    alt.Tooltip(f"{TIMESTAMP_COL}:T", title="Time"),
                    alt.Tooltip("Difference:Q", title="Difference (ppm)", format=".2f"),
                ],
            )
        )

        # Chart showing s1 and s2 sensor values sharing the same Y-axis
        sensors_chart = (
            alt.Chart(plot_df)
            .transform_fold([s1, s2], as_=["Sensor", "Value"])
            .mark_line(strokeWidth=2)
            .encode(
                x=alt.X(f"{TIMESTAMP_COL}:T"),
                y=alt.Y("Value:Q", title="Sensor Values [ppm]"),
                color=alt.Color(
                    "Sensor:N",
                    scale=alt.Scale(range=["#f59e0b", "#10b981"]),
                    legend=alt.Legend(title="Sensors"),
                ),
                tooltip=[
                    alt.Tooltip(f"{TIMESTAMP_COL}:T", title="Time"),
                    alt.Tooltip("Sensor:N", title="Sensor"),
                    alt.Tooltip("Value:Q", title="Value (ppm)", format=".2f"),
                ],
            )
        )

        chart = (
            alt.layer(sensors_chart, diff_chart)
            .resolve_scale(y="independent")
            .properties(
                title="Sensor Data and Difference Over Time",
                width="container",
                height=320,
            )
            .interactive()
        )
    else:
        chart = None

    mo.vstack([comparison_widget, averaging_slider, chart, comparison_display])
    return


if __name__ == "__main__":
    app.run()
