import marimo

__generated_with = "0.23.6"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    # 📊 CO2 Sensor Comparison Dashboard

    This interactive notebook loads CO2 sensor data, filters noise using a rolling mean, interpolates dropouts, and compares metrics (DC offset, Tracking Variation STD, Pearson correlation) between different sensors.
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
def _(TIMESTAMP_COL, pl):
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
                .rolling_mean_by(TIMESTAMP_COL, window_size="7m")
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
def _(TIMESTAMP_COL, df, mo):
    sensor_names = sorted([col for col in df.columns if col != TIMESTAMP_COL])
    s1_dropdown = mo.ui.dropdown(options=sensor_names, value="0A", label="Sensor 1")
    s2_dropdown = mo.ui.dropdown(options=sensor_names, value="0B", label="Sensor 2")

    # We display them nicely in a row
    comparison_widget = mo.md(
        f"""
        ### Interactive Sensor Comparison
        Select two sensors to compare in real time:

        {mo.hstack([s1_dropdown, s2_dropdown])}
        """
    )
    comparison_widget
    return s1_dropdown, s2_dropdown


@app.cell
def _(compare_sensors, df, mo, s1_dropdown, s2_dropdown):
    # This runs reactively whenever s1_dropdown or s2_dropdown changes.
    s1 = s1_dropdown.value
    s2 = s2_dropdown.value

    if s1 and s2:
        metrics = compare_sensors(df, s1, s2)
        comparison_display = mo.md(
            f"""
            #### Metrics between **{s1}** and **{s2}**
            *   **Paired Points**: {metrics["Paired Points"]}
            *   **DC Offset (Average Difference)**: {metrics["DC Offset"]} ppm
            *   **Tracking Variation (STD of Differences)**: {metrics["Tracking Variation STD"]} ppm
            *   **Pearson Correlation**: {metrics["Pearson Correlation"]}
            """
        )
    else:
        comparison_display = mo.md("*Please select two sensors to compare.*")
    comparison_display
    return


@app.cell
def _(FAVORITES, cross_compare, df, mo):
    metrics_df = cross_compare(df, FAVORITES)

    cross_comparison_widget = mo.md(
        f"""
        ### Favorites Cross-Comparison Table
        Below are the comparison metrics for all favorites against other active sensors:

        {mo.as_html(metrics_df)}
        """
    )
    cross_comparison_widget
    return


if __name__ == "__main__":
    app.run()
