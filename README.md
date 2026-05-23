# 🐱 Credit Cat

**A self-discovery tool that shows credit-card applicants which group of similar applicants they most resemble — what it means, what they might qualify for, and what actually moves their profile forward. Built for the applicant, not the bank.**

Datathon 2026 · **Pillar 2 — Unsupervised ML ("Find Your Cluster")** · Team: Emmet & Prithvi

---

## What it is

We cluster 689 anonymized credit-card applicants into four data-driven **credit segments** and wrap the model in an application a real person could use Monday morning. A user answers a few questions, and Credit Cat shows them their segment, where they sit among everyone else, how typical they are, the credit context for a profile like theirs, and **realistic, actionable steps toward the next segment up**.

As a USML team we are scored on **Cluster Quality & Insight** and **do not** submit a `predictions.csv`.

## Repository structure

```
credit-cat/
├── app.py                      # the application users touch (Streamlit UI)
├── backend.py                  # all model/data logic (no UI)
├── requirements.txt
├── .streamlit/config.toml      # brand theme
├── data/
│   └── Credit_Card_Applications.csv
├── models/
│   └── cluster_model.joblib    # trained model + scaler + PCA + metadata
├── notebooks/
│   └── Clustering_Story.ipynb  # all training code, told as a narrative
├── docs/                       # specification documents (see "How we built it")
│   ├── system-requirements.md
│   ├── backend.md
│   └── frontend.md
├── MODEL_REPORT.md             # 1-page model report (approach, validation, limitations)
├── RESPONSIBLE_AI.md           # required Responsible-AI statement
├── CHANGELOG.md
└── README.md
```

## Setup & run

```bash
pip install -r requirements.txt
streamlit run app.py
```

On macOS, if `streamlit` isn't found or `pip` complains about an externally-managed environment:

```bash
pip3 install -r requirements.txt --break-system-packages --user
python3 -m streamlit run app.py
```

The app opens at `http://localhost:8501`. Click **Get started** to walk the questionnaire, or **Try an example** to preview a real profile from each tier.

## Tech stack

Python · pandas · NumPy · scikit-learn (KMeans, StandardScaler, PCA, silhouette) · Streamlit · matplotlib · joblib · Google Colab · Git / GitHub.

## How we built it (specs first)

We attended a workshop on **specification-driven development** ("vibe coding with specifications") and applied it directly: before writing application code we wrote three specs in [`docs/`](docs/) — `system-requirements.md`, `backend.md`, and `frontend.md` — defining what the system must do, the backend contract, and the UI/UX. The build then followed those specs (e.g., the strict `backend.py` / `app.py` separation comes straight from the requirements).

## The four segments

| Segment | Credit tier | Historical approval (validation) |
|---|---|---|
| The Builder | New-to-credit / thin file | ~20% |
| The Quiet File | Near-prime, light history | ~40% |
| The Established | Prime | ~80% |
| The Veteran | Super-prime, seasoned | ~90% |

The model never saw the approve/deny label — yet the segments separate cleanly by historical approval, which is our core validation result. Full detail in [`MODEL_REPORT.md`](MODEL_REPORT.md).

## Responsible AI

Credit Cat never predicts approval or assigns a score; credit-limit figures are general industry context, not offers; the approve/deny label is used only for validation and clearly-caveated context; recommendations are limited to legitimate, changeable behaviors; and no user data is stored. Full statement in [`RESPONSIBLE_AI.md`](RESPONSIBLE_AI.md).
