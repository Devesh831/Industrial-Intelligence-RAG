"""Recompute consistency checks from the generated, private output files."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent


def main():
    results = json.loads((ROOT / "results.json").read_text(encoding="utf-8"))
    metrics = json.loads((ROOT / "forecast_metrics.json").read_text(encoding="utf-8"))
    shutdown = pd.read_csv(ROOT / "shutdown_periods.csv", parse_dates=["start", "end"])
    anomalies = pd.read_csv(ROOT / "anomalous_periods.csv", parse_dates=["start", "end"])
    clusters = pd.read_csv(ROOT / "clusters_summary.csv")
    forecasts = pd.read_csv(ROOT / "forecasts.csv", parse_dates=["origin", "target_time"])
    for frame in (shutdown, anomalies):
        hours = (frame.end-frame.start).dt.total_seconds()/3600
        assert (hours > 0).all() and np.allclose(hours, frame.duration_hours), "Invalid event durations"
        assert frame.start.is_monotonic_increasing, "Events must be ordered"
        assert (frame.start.iloc[1:].reset_index(drop=True) >= frame.end.iloc[:-1].reset_index(drop=True)).all(), "Events overlap"
    assert len(shutdown) == results["shutdown_events"]
    assert np.isclose(shutdown.duration_hours.sum(), results["shutdown_hours"])
    assert len(anomalies) == results["anomaly_events"]
    assert int(clusters.sample_count.sum()) == results["active_clustered_bins"]
    assert len(forecasts) == results["test_origins"] * 12
    assert set(forecasts.horizon_steps) == set(range(1, 13))
    assert not forecasts.duplicated(["origin", "horizon_steps"]).any()
    assert (forecasts.target_time - forecasts.origin == pd.to_timedelta(forecasts.horizon_steps*5, unit="min")).all()
    for name in ("persistence", "random_forest"):
        err = forecasts[name] - forecasts.actual
        assert np.isclose(np.abs(err).mean(), metrics[name]["mae"])
        assert np.isclose(np.sqrt(np.square(err).mean()), metrics[name]["rmse"])
    print("Output event, cluster and forecast consistency checks passed.")


if __name__ == "__main__": main()
