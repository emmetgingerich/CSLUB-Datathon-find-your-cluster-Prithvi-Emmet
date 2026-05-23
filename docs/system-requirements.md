# System Requirements — Credit Cat

**Project:** Credit Cat (Datathon Pillar 2 · USML) — formerly "Find Your Cluster / ClusterDawg"
**Doc:** 1 of 3 (System Requirements → Backend → Frontend)
**Version:** 0.3 · **Owners:** Emmet, Prithvi

---

## 1. Purpose

A self-discovery tool that lets a credit-card applicant find which *credit segment* of
similar applicants they belong to, understand what that means (likely card types and
typical limit ranges), see where they sit among everyone else, and read honest
historical context — so the user can navigate their own situation.

It is explicitly **a tool for the applicant, not a screening tool for a bank.**

## 2. Users

| User | Need |
|---|---|
| **Primary: an applicant** | "Where do I fit? What does it mean? What might I qualify for? What should I focus on?" |
| Secondary: a judge / demo viewer | Understand the model + product in <8 minutes |
| **Not a user: a lender** | Must not function as a pre-screening or approval engine |

## 3. Scope

**In scope** — assign to one of 4 credit segments; describe the segment in plain language;
show typical credit-limit range and likely card types as general guidance; show "what
actually matters" for that profile; "You are here" map; how-typical indicator; historical
approval context with caveat; example users + random applicant.

**Out of scope** — predicting approval/denial; advice to "game" an application; storing or
transmitting user input; any lender pre-screening use.

## 4. Functional Requirements

| ID | Requirement |
|---|---|
| FR-1 | Load the trained model bundle (`models/cluster_model.joblib`) on startup. |
| FR-2 | Accept all 14 applicant features as input, one question at a time. |
| FR-3 | Use friendly labels where meaning is reasonably inferable; keep original codes with helper text where it isn't. |
| FR-4 | Provide one "example user" per segment + a random real applicant. |
| FR-5 | Route through Landing → Intent → Questionnaire → Paywall (skippable) → Results. |
| FR-6 | Assign the user to a segment using the same preprocessing pipeline as training. |
| FR-7 | Show the segment name, tier, what it means, and a "You vs. typical" sense of fit. |
| FR-8 | **"You are here" map** — user highlighted on a 2-D PCA scatter; the user's own segment is vibrant, others faded in their own colour. |
| FR-9 | **"How typical are you"** — central / typical / on-the-edge, naming the nearest other segment when borderline. |
| FR-10 | Show **typical starting credit-limit range and likely card types** as general guidance for the segment. |
| FR-11 | Display the segment's historical approval rate with an explicit bias/limitations caveat. |
| FR-12 | Never display an approve/deny prediction or score for the user. |

## 5. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 Performance | Model, data, PCA load once and are cached; renders instantly. |
| NFR-2 Reproducibility | Same input → same segment & map position; fixed `random_state`; pinned deps. |
| NFR-3 Single source of truth | Preprocessing/PCA/distance logic in one place, shared by training and serving. |
| NFR-4 Separation of concerns | All logic in `backend.py`; `app.py` is presentation only. |
| NFR-5 Privacy | No user input stored, logged, or transmitted; in-memory only. |
| NFR-6 Robustness | Out-of-range / unexpected inputs handled gracefully. |
| NFR-7 Portability | Runs locally on macOS and Windows via `streamlit run app.py`. |
| NFR-8 Design | Credit Cat brand: Capital One-inspired navy/red palette, Archivo type, a recoloured cat logo, a persistent white top bar, and a Curology-inspired multi-section landing — not default Streamlit styling. |

## 6. Data & Model Requirements

- **Source:** `data/Credit_Card_Applications.csv` — 689 applicants, 14 anonymized features, `Class`, `CustomerID`.
- `Class` / `CustomerID` never used for clustering; `Class` only for validation + historical context.
- **Bundle (`cluster_model.joblib`) contains:** KMeans (k=4), scaler, column lists, 38-col layout, segment names, profiles, approval rates, inferred friendly labels, fitted PCA(2), training PCA coords + labels, and per-segment centroid distances.
- **Segments (k=4):** The Builder (new-to-credit / thin file), The Quiet File (near-prime), The Established (prime), The Veteran (super-prime). Names are credit-tier-based; display copy lives in `app.py`.

## 7. Constraints & Assumptions

- Features anonymized; friendly labels inferred and marked as such.
- Streamlit only; no server/database.
- Log-transform of skewed continuous features before scaling (fixes A14 singleton).
- k=4 for the product (silhouette 0.158, no tiny clusters); k=2 reported as strongest split (0.186).
- 2-D PCA map captures ~35% of variance — a simplified view.
- Credit-limit ranges and card types are **general industry figures** for similar profiles, not derived from this dataset.

## 8. Responsible-AI Requirements

| ID | Requirement |
|---|---|
| RAI-1 | Never present as predicting approval; framing is "where you sit / who is similar." |
| RAI-2 | Historical approval figures shown with a bias caveat. |
| RAI-3 | Inferred feature labels marked as inferred; codes shown where meaning is unknown. |
| RAI-4 | No user data retained. |
| RAI-5 | How-typical / nearest-segment framed as orientation, never steps to change an outcome. |
| RAI-6 | Credit-limit ranges and card types labelled **general guidance, not an offer, score, or prediction**, and noted to vary by lender and income. |

## 9. Acceptance Criteria

- [ ] Launches with one command from the repo root.
- [ ] Top bar (logo + nav + CTA) appears on every screen.
- [ ] One-question-at-a-time flow with 14-dot progress; Back/Next work.
- [ ] Each example user lands in its own segment.
- [ ] Results dashboard shows segment, KPIs (limit / approval / typicality), what-matters, likely cards, the map, and the caveat.
- [ ] Map shows the user's segment vibrant, others faded; red star = user.
- [ ] No approve/deny output anywhere.
- [ ] Same inputs → same segment & map position.

## 10. Future / Out of Scope

- Counterfactual nudges (tight RAI framing only).
- Saved/exportable summary.
- Sticky-on-scroll top bar.
