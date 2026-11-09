"""Reproducible cyclone time-series analysis. See README for assumptions."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
PLOTS = ROOT / "plots"
TARGET = "Cyclone_Inlet_Gas_Temp"
OUTLET = "Cyclone_Gas_Outlet_Temp"
DRAFT = "Cyclone_Inlet_Draft"
SEED = 42


def events(mask, label="event"):
    """Consecutive true 5-minute bins; end is exclusive."""
    mask = mask.fillna(False).astype(bool)
    groups = mask.ne(mask.shift(fill_value=False)).cumsum()
    idx = mask[mask].index
    if len(idx) == 0:
        return pd.DataFrame(columns=["start", "end", "duration_hours"])
    grouped = pd.Series(idx, index=idx).groupby(groups.loc[idx])
    result = grouped.agg(start="first", last="last")
    result["end"] = result.pop("last") + pd.Timedelta(minutes=5)
    result["duration_hours"] = (result.end - result.start).dt.total_seconds() / 3600
    return result.reset_index(drop=True)


def prepare(path):
    raw = pd.read_excel(path, sheet_name="internship-data-1")
    raw["time"] = pd.to_datetime(raw.time, errors="coerce")
    raw = raw.dropna(subset=["time"]).sort_values("time")
    if raw.time.duplicated().any() or (raw.time.dt.floor("5min") != raw.time).any():
        raise ValueError("Duplicate or off-grid timestamps require explicit review")
    raw = raw.set_index("time").apply(pd.to_numeric, errors="coerce")
    grid = pd.date_range(raw.index.min(), raw.index.max(), freq="5min", name="time")
    data = raw.reindex(grid)
    # Fill only internally bounded gaps of at most 3 bins, never long outages.
    for c in data:
        s = data[c]
        run = s.isna().ne(s.isna().shift()).cumsum()
        size = s.isna().groupby(run).transform("sum")
        candidate = s.interpolate(limit_area="inside")
        data[c] = s.where(~(s.isna() & (size <= 3)), candidate)
    return raw, data


def chart(data, output, title, cols=None):
    cols = cols or [TARGET, OUTLET]
    ax = data[cols].plot(figsize=(12, 4), lw=.65, title=title)
    ax.set_ylabel("Sensor reading (units not supplied)")
    ax.figure.tight_layout(); ax.figure.savefig(PLOTS / output, dpi=150); plt.close(ax.figure)


def main(path):
    PLOTS.mkdir(exist_ok=True)
    raw, data = prepare(path)
    sensors = list(data.columns)
    raw.describe(percentiles=[.05, .5, .95]).T.to_csv(ROOT / "summary_statistics.csv")
    raw.corr().to_csv(ROOT / "correlation_matrix.csv")
    chart(data.loc["2017-01-01":"2017-01-07"], "one_week.png", "First week: temperatures")
    chart(data.loc["2017"].resample("1h").mean(), "one_year.png", "2017: hourly mean temperatures")
    # Conservative heuristic, not a verified operational label. Missing observations are unknown.
    known = data[[TARGET, OUTLET, DRAFT]].notna().all(axis=1)
    low = (data[TARGET] < 200) & (data[OUTLET] < 200) & (data[DRAFT] > -50) & known
    shutdowns = events(low)
    shutdowns.to_csv(ROOT / "shutdown_periods.csv", index=False)
    year = data.loc["2017"]
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(year.index, year[TARGET], lw=.35, label="Inlet temperature")
    for row in shutdowns.itertuples():
        if row.start.year <= 2017 and row.end.year >= 2017:
            ax.axvspan(row.start, row.end, color="red", alpha=.3)
    ax.set_title("2017: detected low-temperature / low-draft periods (red)"); ax.legend(); fig.tight_layout(); fig.savefig(PLOTS / "shutdowns_2017.png", dpi=150); plt.close(fig)
    # Winsorisation is used only for model input; raw data and event evidence remain unchanged.
    active = data.notna().all(axis=1) & ~low
    X = data.loc[active, sensors]
    limits = X.quantile([.005, .995]); X = X.clip(limits.loc[.005], limits.loc[.995], axis=1)
    sample = X.sample(min(len(X), 40000), random_state=SEED)
    scaler = StandardScaler().fit(sample)
    km = KMeans(n_clusters=4, random_state=SEED, n_init=10).fit(scaler.transform(sample))
    states = pd.Series(pd.NA, index=data.index, dtype="Int64", name="state")
    states.loc[X.index] = km.predict(scaler.transform(X))
    state_stats = data.loc[X.index].groupby(states.loc[X.index]).agg(["mean", "std", "median", lambda x: x.quantile(.05), lambda x: x.quantile(.95)])
    state_stats.columns = [f"{a}__{b.replace('<lambda_0>', 'p05').replace('<lambda_1>', 'p95')}" for a,b in state_stats.columns]
    for state in range(4):
        runs = events(states.eq(state))
        state_stats.loc[state, "sample_count"] = int(states.eq(state).sum())
        state_stats.loc[state, "run_count"] = len(runs)
        state_stats.loc[state, "median_run_minutes"] = runs.duration_hours.median()*60
    state_stats.to_csv(ROOT / "clusters_summary.csv")
    anomaly = pd.Series(False, index=data.index)
    for state in range(4):
        idx = states.index[states.eq(state).fillna(False)]
        values = X.loc[idx]
        train = values.sample(min(len(values), 30000), random_state=SEED)
        forest = IsolationForest(n_estimators=100, contamination=.01, random_state=SEED, n_jobs=-1).fit(scaler.transform(train))
        anomaly.loc[idx] = forest.predict(scaler.transform(values)) == -1
    periods = events(anomaly)
    details = []
    reference_stats = {state: (data.loc[states.eq(state).fillna(False)].mean(), data.loc[states.eq(state).fillna(False)].std().replace(0, np.nan)) for state in range(4)}
    for row in periods.itertuples():
        subset = data.loc[row.start:row.end-pd.Timedelta(minutes=5)]
        st = int(states.loc[row.start])
        mean, scale = reference_stats[st]
        scores = ((subset.mean()-mean).abs()/scale).sort_values(ascending=False)
        details.append({"start":row.start,"end":row.end,"duration_hours":row.duration_hours,"state":st,"most_implicated_variables":", ".join(scores.index[:3])})
    pd.DataFrame(details, columns=["start","end","duration_hours","state","most_implicated_variables"]).to_csv(ROOT / "anomalous_periods.csv", index=False)
    evidence = []
    for i, row in enumerate(periods.nlargest(4, "duration_hours").itertuples(), 1):
        window = data.loc[row.start-pd.Timedelta(hours=2):row.end+pd.Timedelta(hours=2)]
        before = data.loc[row.start-pd.Timedelta(hours=1):row.start-pd.Timedelta(minutes=5)]
        during = data.loc[row.start:row.end-pd.Timedelta(minutes=5)]
        after = data.loc[row.end:row.end+pd.Timedelta(minutes=55)]
        record = {"event":i,"start":row.start,"end":row.end,"state_before":str(states.loc[row.start-pd.Timedelta(minutes=5)]) if row.start-pd.Timedelta(minutes=5) in states.index else "unknown", "state_during":str(states.loc[row.start]), "state_after":str(states.loc[row.end]) if row.end in states.index else "unknown"}
        for col in [TARGET, OUTLET, DRAFT]:
            for label, frame in [("before", before), ("during", during), ("after", after)]: record[f"{col}_{label}_median"] = frame[col].median()
        evidence.append(record)
        fig, axes = plt.subplots(3, 1, figsize=(12, 7), sharex=True)
        window[[TARGET, OUTLET]].plot(ax=axes[0], lw=.8); window[[DRAFT]].plot(ax=axes[1], lw=.8)
        states.loc[window.index].astype(float).plot(ax=axes[2], drawstyle="steps-post", lw=.8); axes[2].set_ylabel("State")
        for ax in axes: ax.axvspan(row.start, row.end, color="red", alpha=.2)
        axes[0].set_title(f"Anomaly {i}: state at start {states.loc[row.start]}; red = flagged")
        fig.tight_layout(); fig.savefig(PLOTS / f"anomaly_{i}.png", dpi=150); plt.close(fig)
    pd.DataFrame(evidence).to_csv(ROOT / "selected_anomaly_evidence.csv", index=False)
    # 12-output direct forecasting using past 12 observations. Time split precedes test targets.
    # Forecast only fully observed windows; interpolation could leak future values.
    temp = raw[TARGET].reindex(data.index).to_numpy(); n = len(temp); split = int(n*.8)
    offsets = np.arange(12); starts = np.arange(11, n-12)
    past = np.column_stack([temp[starts-i] for i in offsets])
    future = np.column_stack([temp[starts+i] for i in range(1,13)])
    valid = np.isfinite(past).all(axis=1) & np.isfinite(future).all(axis=1)
    train_mask = valid & (starts+12 < split)
    test_mask = valid & (starts >= split) & ((starts-split)%12 == 0)
    train_ids = np.flatnonzero(train_mask)
    rng = np.random.default_rng(SEED)
    if len(train_ids)>30000: train_ids = np.sort(rng.choice(train_ids, 30000, replace=False))
    model = RandomForestRegressor(n_estimators=60, min_samples_leaf=4, n_jobs=-1, random_state=SEED).fit(past[train_ids], future[train_ids])
    ids = np.flatnonzero(test_mask); actual = future[ids]; pred = model.predict(past[ids]); base = np.repeat(past[ids,:1], 12, axis=1)
    rows = []
    for j, idx in enumerate(ids):
        for h in range(12): rows.append((data.index[starts[idx]],data.index[starts[idx]+h+1],h+1,actual[j,h],base[j,h],pred[j,h]))
    forecasts = pd.DataFrame(rows, columns=["origin","target_time","horizon_steps","actual","persistence","random_forest"])
    forecasts.to_csv(ROOT / "forecasts.csv", index=False)
    metrics = {name:{"mae":float(mean_absolute_error(actual.ravel(), p.ravel())), "rmse":float(np.sqrt(mean_squared_error(actual.ravel(), p.ravel())))} for name,p in [("persistence",base),("random_forest",pred)]}
    (ROOT / "forecast_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    fig, ax=plt.subplots(figsize=(10,4)); ax.plot(range(1,13),np.mean(abs(actual-base),axis=0),label="Persistence"); ax.plot(range(1,13),np.mean(abs(actual-pred),axis=0),label="Random forest"); ax.set(xlabel="Horizon (5-minute steps)",ylabel="MAE",title="Held-out forecast error by horizon"); ax.legend(); fig.tight_layout(); fig.savefig(PLOTS / "forecast_errors.png",dpi=150); plt.close(fig)
    results={"rows":len(raw),"grid_rows":len(data),"unknown_shutdown_bins":int((~known).sum()),"shutdown_events":len(shutdowns),"shutdown_hours":float(shutdowns.duration_hours.sum()),"active_clustered_bins":int(active.sum()),"anomalous_bins":int(anomaly.sum()),"anomaly_events":len(periods),"test_origins":len(ids),"forecast_metrics":metrics}
    (ROOT / "results.json").write_text(json.dumps(results,indent=2), encoding="utf-8")
    print(json.dumps(results,indent=2))


if __name__ == "__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("workbook", type=Path); args=parser.parse_args(); main(args.workbook)
