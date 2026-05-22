# System Requirements — Find Your Cluster

**Project:** Find Your Cluster (Datathon Pillar 2 · USML)
**Doc:** 1 of 3 (System Requirements → Backend → Frontend)
**Version:** 0.2 · **Owners:** Emmet, Prithvi

---

## 1. Purpose

A self-discovery tool that lets a credit-card applicant find which *cluster* of
similar applicants they belong to, understand what that group looks like, see
where they sit relative to everyone else, and read honest historical context —
so the user can navigate their own situation.

It is explicitly **a tool for the applicant, not a screening tool for a bank.**

## 2. Users

| User | Need |
|---|---|
| **Primary: an applicant** | "Where do I fit? Who is similar to me? How typical am I? What's the history for people like me?" |
| Secondary: a judge / demo viewer | Understand the model and product in <8 minutes |
| **Not a user: a lender** | The tool must not function as a pre-screening or approval engine |

## 3. Scope

**In scope**
- Take an applicant's details and assign them to one of 4 clusters
- Describe the typical member of that cluster in plain language
- Show the user their position among all applicants on a 2-D map ("You are here")
- Tell the user how central vs. borderline they are within their cluster
- Show historical approval context for that cluster, with a bias caveat
- Offer example users + a random real applicant for exploration/demo

**Out of scope (explicitly)**
- Predicting approval / denial for the user (no score, no yes/no)
- Advice on how to "game" an application
- Storing, logging, or transmitting any user input
- Any use by a lender to rank or filter applicants

## 4. Functional Requirements

| ID | Requirement |
|---|---|
| FR-1 | Load the trained model bundle (`models/cluster_model.joblib`) on startup. |
| FR-2 | Accept all 14 applicant features as input. |
| FR-3 | Use friendly labels (Age, Income/balance, # accounts) where meaning is reasonably inferable; keep original codes with helper text where it is not. |
| FR-4 | Provide one "example user" per cluster that loads a representative applicant. |
| FR-5 | Provide a "random real applicant" loader for quick exploration. |
| FR-6 | Assign the user to a cluster using the **same** preprocessing pipeline as training (log → scale → one-hot → align to 38 columns). |
| FR-7 | Display the assigned cluster's name and a "You vs. typical member" comparison. |
| FR-8 | **"You are here" map** — plot the user as a highlighted point on a 2-D PCA scatter of all 689 applicants, colored by cluster. |
| FR-9 | **"How typical are you"** — report how central the user is within their cluster (distance to centroid vs. the cluster's own distribution) and name the nearest *other* cluster if they are borderline. |
| FR-10 | Display the cluster's historical approval rate **with** an explicit bias/limitations caveat. |
| FR-11 | Never display an approve/deny prediction or score for the user. |

## 5. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 (Performance) | Model, data, and PCA load once and are cached; results and the map render instantly on interaction. |
| NFR-2 (Reproducibility) | Same input always yields the same cluster and map position; fixed `random_state`; dependency versions recorded in `requirements.txt`. |
| NFR-3 (Single source of truth) | Preprocessing, PCA, and centroid-distance logic exist in exactly one place, shared by training and serving; no drift permitted. |
| NFR-4 (Separation of concerns) | Model/data logic is separable from UI code so the backend can be reasoned about and tested independently. |
| NFR-5 (Privacy) | No user input is stored, logged, or sent anywhere; all processing is in-memory and discarded. |
| NFR-6 (Robustness) | Out-of-range or unexpected inputs are handled gracefully, never crashing the app. |
| NFR-7 (Portability) | Runs locally on macOS and Windows with `streamlit run app.py` after `pip install -r requirements.txt`. |
| NFR-8 (Design) | UI follows the chosen design principle (Swiss / International Typographic Style) — grid alignment, typographic hierarchy, restrained palette, generous whitespace — not default Streamlit styling. |

## 6. Data & Model Requirements

- **Source data:** `data/Credit_Card_Applications.csv` — 689 applicants, 14 anonymized features (A1–A14), plus a `Class` column (historical approve/deny) and `CustomerID`.
- **`Class` and `CustomerID` are never used for clustering.** `Class` is used only for post-hoc validation and historical-context display.
- **Model bundle (`cluster_model.joblib`) must contain:**
  - the fitted KMeans model (k=4) and the fitted scaler
  - the column lists (binary / categorical / continuous / log) and the 38-column training layout
  - the cluster name map, per-cluster profiles, and per-cluster approval rates
  - **the fitted PCA (2 components)** and **the PCA coordinates + cluster labels of all training applicants** (for the "You are here" map — FR-8)
  - **per-cluster reference distances to centroid** (for the "How typical are you" indicator — FR-9)

## 7. Constraints & Assumptions

- Features are anonymized; friendly labels are *inferred* and presented as such, never asserted as ground truth.
- Built on Streamlit (Python); no separate web server or database.
- Continuous features are log-transformed before scaling to control extreme right-skew (A14 skewness ≈ 13) that otherwise produced a singleton cluster.
- k=4 chosen for the product (richer, navigable groups, silhouette 0.158, no tiny clusters); k=2 reported as the single strongest split (silhouette 0.186).
- The 2-D PCA map captures ~35% of total variance and is presented as a simplified view, not the full picture.

## 8. Responsible-AI Requirements

| ID | Requirement |
|---|---|
| RAI-1 | The app must never present itself as predicting approval; framing is always "who is similar to you / where do you sit." |
| RAI-2 | Any historical approval figure must appear with a caveat that it reflects past human decisions which may carry bias. |
| RAI-3 | Inferred feature labels must be marked as inferred, with anonymized codes shown where meaning is unknown. |
| RAI-4 | No user data is retained (see NFR-5). |
| RAI-5 | The "How typical are you" / nearest-cluster feature is framed as orientation ("you sit between these groups"), never as steps to change an outcome. |

## 9. Acceptance Criteria (demo-ready checklist)

- [ ] App launches with one command from the repo root.
- [ ] Clicking each "example user" loads a person who lands in that cluster.
- [ ] Entering details and submitting returns a cluster name + comparison + caveated context.
- [ ] The "You are here" map shows the user's point highlighted among all applicants.
- [ ] The "How typical are you" indicator reports central vs. borderline and names the nearest other cluster when relevant.
- [ ] No approve/deny output appears anywhere.
- [ ] App handles an empty/extreme input without crashing.
- [ ] Same inputs reliably give the same cluster and map position.

## 10. Future / Out of Scope (nice-to-have)

- Counterfactual nudges (which features most separate clusters) — only with tight RAI framing per RAI-5; deferred due to misuse risk.
- Cluster-comparison view (all four side by side).
- Exportable summary the user can save.
