"""
Analyze CO2 sensor data from multiple sensors and compare the sensors.
"""

from pathlib import Path

import polars as pl

SOURCE = Path("data") / "baseline_CO2_data_2026-05-22_2259.csv"
TIMESTAMP_COL = "DateTime"

# The most responsive and consistent group of sensors, by eyeball.
FAVORITES = ["0A", "10A", "10B", "20B", "SP1", "SP3"]


def load_data(source: str | Path) -> pl.DataFrame:
    """Load and smooth the data."""
    df_raw = pl.read_csv(source, try_parse_dates=True)

    # Sort by the timestamp to ensure rolling window calculations work correctly.
    df = df_raw.sort(TIMESTAMP_COL)

    # Cast sensor columns to Float64 so initial nulls don't parse as string columns;
    # interpolate() between non-null values (or forward_fill() to repeat the last
    # non-null value);
    # then apply the rolling mean (moving average) on a 15 minute window to reduce
    # sensor noise.
    sensor_cols = [col for col in df.columns if col != TIMESTAMP_COL]
    df_filtered = df.with_columns(
        [
            pl.col(col)
            .cast(pl.Float64)
            .interpolate()
            .rolling_mean_by(TIMESTAMP_COL, window_size="15m")
            for col in sensor_cols
        ]
    )

    return df_filtered


def compare_sensors(df: pl.DataFrame, s1_name: str, s2_name: str) -> dict:
    """Align two sensors, filter dropouts, and compute metrics."""

    # Isolate columns and drop rows where either sensor has a null (dropout).
    # The only nulls after load_data's interpolate() or forward_fill() should
    # be at the beginning.
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

    Returns a Polars DataFrame with columns: Sensor 1, Sensor 2, Paired Points,
    DC Offset, Tracking Variation STD, and Pearson Correlation.
    """
    sensor_cols = [col for col in df.columns if col != TIMESTAMP_COL]
    pairs = []
    for fav in favs:
        if fav not in sensor_cols:
            print(f"Warning: Favorite sensor '{fav}' isn't in the data.")
            continue
        pairs.extend([(fav, other) for other in sensor_cols if other != fav])

    metrics = []
    for s1, s2 in pairs:
        m = compare_sensors(df, s1, s2)
        metrics.append(m)
    return pl.DataFrame(metrics)


def load_and_compare(source: str | Path, favs: list[str]) -> pl.DataFrame:
    """
    Load the .csv sensor data and return the cross-comparison metrics.
    """
    df = load_data(source)
    return cross_compare(df, favs)


def example():
    # Example use with column names from the CSV:
    df = load_data(SOURCE)
    metrics = compare_sensors(df, "0A", "0B")
    print(metrics)


if __name__ == "__main__":
    metrics_df = load_and_compare(SOURCE, FAVORITES)
    metrics_df.show(1000)
