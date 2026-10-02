"""Verify submission file hashes and recompute metrics from all saved predictions.

This check does not fit new models or regenerate the original source data.
"""
import csv
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

root = Path(__file__).resolve().parent
with (root / "manifest_sha256.csv").open(encoding="utf-8-sig", newline="") as handle:
    entries = list(csv.DictReader(handle))
for entry in entries:
    path = root / Path(entry["file"].replace("\\", "/"))
    assert path.stat().st_size == int(entry["bytes"]), entry["file"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], entry["file"]

scores = pd.read_csv(root / "results" / "comparison_results.csv")
assert len(scores) == 280
assert not scores.duplicated(["Representation", "Model", "Split"]).any()
assert scores["Converged"].all()
for row in scores.itertuples(index=False):
    name = f"{row.Representation}_{row.Model}_{row.Split}.csv"
    predictions = pd.read_csv(root / "results" / "predictions" / name)
    assert len(predictions) == int(row.N) and predictions.token_id.is_unique, name
    observed = predictions.log_apr.to_numpy(dtype=np.float64)
    predicted = predictions.prediction.to_numpy(dtype=np.float64)
    assert np.isfinite(observed).all() and np.isfinite(predicted).all(), name
    r2 = r2_score(observed, predicted)
    adjusted = 1 - (1 - r2) * (row.N - 1) / (row.N - row.P - 1)
    actual = [r2, adjusted, np.sqrt(mean_squared_error(observed, predicted)),
              mean_absolute_error(observed, predicted)]
    expected = [row.R2, row.Adj_R2, row.RMSE, row.MAE]
    assert np.allclose(actual, expected, rtol=1e-12, atol=1e-12), name

print(f"Verified {len(entries)} file hashes and all {len(scores)} prediction/score records.")
