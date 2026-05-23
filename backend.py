"""
backend.py — all model & data logic for Find Your Cluster.

No Streamlit / UI code lives here (NFR-4). The frontend calls only the public
functions below; it never touches the model, scaler, or a DataFrame directly.
Single source of truth for preprocessing (NFR-3): the same recipe used in training.
"""

import functools
import numpy as np
import pandas as pd
import joblib

BUNDLE_PATH = "models/cluster_model.joblib"
DATA_PATH = "data/Credit_Card_Applications.csv"

ALL_FEATURES = [f"A{i}" for i in range(1, 15)]

# If the CSV was saved with our inferred friendly headers, normalize back to A-codes.
_FRIENDLY_TO_A = {
    "Gender": "A1", "Age": "A2", "Years_Employed": "A3", "Marital_Status": "A4",
    "Creditworthiness_Tier": "A5", "Occupation": "A6", "Years_at_Address": "A7",
    "Currently_Employed": "A8", "Prior_Default": "A9", "Debt_Thousands": "A10",
    "Drivers_License": "A11", "Citizenship_Status": "A12", "Credit Balance": "A13",
    "Annual_Income": "A14",
}


# ---------------------------------------------------------------------------
# Loading (cached so it happens once per process — NFR-1)
# ---------------------------------------------------------------------------
@functools.lru_cache(maxsize=1)
def load_bundle(path=BUNDLE_PATH):
    return joblib.load(path)


@functools.lru_cache(maxsize=1)
def _load_data(path=DATA_PATH):
    df = pd.read_csv(path)
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    df = df.rename(columns=_FRIENDLY_TO_A)
    return df


def _b():
    return load_bundle()


# ---------------------------------------------------------------------------
# Helpers for the UI
# ---------------------------------------------------------------------------
def defaults():
    """A sensible default applicant: dataset median (numbers) / mode (flags & categories)."""
    b, feats = _b(), _load_data()[ALL_FEATURES]
    d = {}
    for c in ALL_FEATURES:
        if c in b["continuous_cols"]:
            d[c] = float(round(feats[c].median(), 2))
        else:
            d[c] = int(feats[c].mode().iloc[0])
    return d


def category_options():
    """Valid values for each categorical feature, for select boxes."""
    b, df = _b(), _load_data()
    return {c: sorted(int(x) for x in df[c].unique()) for c in b["categorical_cols"]}


def friendly_labels():
    return _b()["friendly"]


# ---------------------------------------------------------------------------
# Core: preprocessing (the single source of truth) + cluster assignment
# ---------------------------------------------------------------------------
def preprocess(raw):
    """Raw 14-feature dict -> the aligned 1x38 row the model expects (NFR-3, NFR-6)."""
    b = _b()
    full = defaults()
    full.update({k: v for k, v in raw.items() if k in ALL_FEATURES})  # ignore stray keys
    row = pd.DataFrame([full])
    row[b["log_cols"]] = np.log1p(row[b["log_cols"]])
    cont = pd.DataFrame(b["scaler"].transform(row[b["continuous_cols"]]),
                        columns=b["continuous_cols"])
    cat = pd.get_dummies(row[b["categorical_cols"]].astype(str))
    binr = row[b["binary_cols"]].astype(int).reset_index(drop=True)
    return pd.concat([binr, cont, cat], axis=1).reindex(
        columns=b["feature_columns"], fill_value=0)


def assign_cluster(raw):
    return int(_b()["kmeans"].predict(preprocess(raw))[0])


def get_cluster_info(cid):
    b = _b()
    return {
        "name": b["cluster_names"][cid],
        "profile": b["cluster_profiles"][cid],
        "approval_rate": b["approval_rates"][cid],
    }


# ---------------------------------------------------------------------------
# FR-8: the "You are here" map
# ---------------------------------------------------------------------------
def map_position(raw):
    xy = _b()["pca"].transform(preprocess(raw))[0]
    return float(xy[0]), float(xy[1])


def get_training_map():
    b = _b()
    return b["train_pca_coords"], b["train_labels"]


# ---------------------------------------------------------------------------
# FR-9: "How typical are you"
# ---------------------------------------------------------------------------
def typicality(raw):
    b = _b()
    x = preprocess(raw)
    dists = b["kmeans"].transform(x)[0]          # distance to every centroid
    cid = int(np.argmin(dists))
    d_own = dists[cid]
    ref = b["cluster_distances"][cid]            # member distances in this cluster
    pct = float((ref < d_own).mean())            # fraction of members more central
    label = "very central" if pct < 0.33 else "typical" if pct < 0.66 else "on the edge"
    others = [(i, d) for i, d in enumerate(dists) if i != cid]
    nearest_other = int(min(others, key=lambda t: t[1])[0])
    return {
        "cluster": cid,
        "percentile": pct,
        "label": label,
        "nearest_other": nearest_other,
        "nearest_other_name": b["cluster_names"][nearest_other],
    }


# ---------------------------------------------------------------------------
# FR-4 / FR-5: examples & random applicant
# ---------------------------------------------------------------------------
@functools.lru_cache(maxsize=1)
def list_examples():
    """One representative (typical) applicant per cluster."""
    b, df = _b(), _load_data()
    feats = df[ALL_FEATURES].copy()
    f = feats.copy()
    f[b["log_cols"]] = np.log1p(f[b["log_cols"]])
    cont = pd.DataFrame(b["scaler"].transform(f[b["continuous_cols"]]),
                        columns=b["continuous_cols"], index=feats.index)
    cat = pd.get_dummies(feats[b["categorical_cols"]].astype(str))
    binr = feats[b["binary_cols"]].astype(int)
    X = pd.concat([binr, cont, cat], axis=1).reindex(columns=b["feature_columns"], fill_value=0)
    labels = b["kmeans"].predict(X)
    feats = feats.assign(_c=labels)
    out = {}
    for cid in sorted(set(labels)):
        grp = feats[feats["_c"] == cid]
        ex = {c: float(round(grp[c].median(), 2)) for c in b["continuous_cols"]}
        for c in b["binary_cols"] + b["categorical_cols"]:
            ex[c] = int(grp[c].mode().iloc[0])
        out[int(cid)] = ex
    return out


def random_applicant():
    b, df = _b(), _load_data()
    s = df[ALL_FEATURES].sample(1).iloc[0]
    return {c: (float(s[c]) if c in b["continuous_cols"] else int(s[c])) for c in ALL_FEATURES}


# ---------------------------------------------------------------------------
# Recommendations: realistic, actionable steps toward the next segment up.
# Direction comes from the DATA (how the next group differs on changeable
# features); the advice itself is grounded in real credit behaviour.
# Only mutable, realistic features — never age, gender, marital status, etc.
# ---------------------------------------------------------------------------
ACTIONABLE = ["A8", "A3", "A7", "A14"]  # employed, years employed, years at address, income


def next_cluster_up(cid):
    """The segment with the next-higher historical approval rate (None if top)."""
    rates = _b()["approval_rates"]
    order = sorted(rates, key=lambda c: rates[c])  # ascending approval
    i = order.index(cid)
    return order[i + 1] if i < len(order) - 1 else None


def improvement_areas(raw):
    """Actionable features where the next segment up tends to be stronger than this user."""
    cid = assign_cluster(raw)
    nxt = next_cluster_up(cid)
    if nxt is None:
        return {"cid": cid, "next": None, "areas": []}
    typ = list_examples()[nxt]                       # typical member of the next segment
    full = defaults()
    full.update({k: v for k, v in raw.items() if k in ALL_FEATURES})
    scored = []
    for f in ACTIONABLE:
        uv, tv = float(full[f]), float(typ[f])
        if f == "A8":                                # binary: being employed
            if int(uv) == 0 and int(tv) == 1:
                scored.append((100.0, f))
        else:                                        # continuous: meaningfully below
            gap = tv - uv
            if gap > 0.1 * (abs(tv) + 1):
                scored.append((gap / (abs(tv) + 1), f))
    scored.sort(reverse=True)
    return {"cid": cid, "next": nxt, "areas": [f for _, f in scored][:3]}
