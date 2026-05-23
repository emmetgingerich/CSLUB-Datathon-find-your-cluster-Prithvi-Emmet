# Model Report — Credit Cat

**Pillar 2 · Unsupervised ML ("Find Your Cluster")** · Team: Emmet & Prithvi
Dataset: UCI Credit Approval — 689 applicants, 14 anonymized features (A1–A14), a historical approve/deny `Class`, and `CustomerID`.

---

## 1. Approach

We drop `CustomerID` (an identifier) and **hold out `Class` entirely** — it is never used for clustering, only later for validation and context. The 14 features are bucketed and preprocessed, then clustered with **K-Means**, with **PCA** used purely to visualize the result in 2-D.

Pipeline: bucket features → one-hot encode categoricals → log-transform heavily right-skewed continuous features → `StandardScaler` → K-Means. Final feature matrix: **38 columns**. All randomness fixed with `random_state=42` for reproducibility.

## 2. Feature Choices and Trade-offs

| Bucket | Features | Treatment & rationale |
|---|---|---|
| Identifier | CustomerID | **Dropped** — no signal. |
| Label | Class | **Held out** of clustering; used only for validation/context (this is unsupervised). |
| Binary flags | A1, A8, A9, A11 | Kept as 0/1 — already one unit apart. |
| Categorical | A4, A5, A6, A12 | **One-hot encoded** — the integer codes are unordered labels, so leaving them numeric would falsely imply "category 8 > category 1." |
| Continuous | A2, A3, A7, A10, A13, A14 | **Scaled** so no single feature (e.g., A14, which reaches 100,001) dominates distance. |

**A10 — continuous, not categorical.** A10 is an **ordered count** (more genuinely means more), so we treat it as a continuous quantity and scale it rather than creating dozens of meaningless one-hot columns. We also observed A10's distribution is **heavily right-skewed**, an observation that — together with A14 — informed our log-transform decision below.

## 3. Key Decisions

**Chose k=4 for the product, while reporting k=2 as the strongest split.** *"We let the data lead. Silhouette clearly favored k=2 — the dominant structure in credit applications is a clean two-way split, which our validation check shows aligns with historical approve/deny patterns. But a self-discovery tool that only says 'you're Type A or B' isn't useful to a real applicant, so for the product we deliberately chose k=4 to give users richer, more navigable groups — trading a bit of statistical separation for human usefulness. We made that trade-off knowingly."*

**Log-transformed skewed continuous features to fix an outlier-driven cluster.** *"At k=4 our first attempt produced a one-person cluster. We traced it to extreme right-skew in A14 (skewness ≈ 13), applied a log transform (`log1p`), and re-ran selection. On the corrected data, k=4 yields four well-sized groups (68–364 applicants) and a higher silhouette than k=3 — so we use four clusters for the product, while reporting that the single strongest split in the data is k=2."*

**Treated 98% serving/training agreement as a feature, not a bug.** 676 of 690 applicants get the identical cluster whether processed one-at-a-time (the app's path) or all-at-once (training). The 14 that differ sit right on a boundary between two clusters — genuinely "between groups." For a self-discovery tool that's honest and correct; it simply means a borderline user could reasonably belong to either neighbor.

**Shipped the paywall as a disabled demonstration.** We include a paywall interstitial as a realistic monetization surface, but it is **off by default** ("Continue for free" always works). Charging applicants to see information about themselves raises a genuine fairness concern, so we surface it openly and acknowledge the tension rather than hide it.

**Separated logic from UI; recommendations are actionable-only.** All model logic lives in `backend.py`; `app.py` is presentation only. The "next move" recommendation engine uses the data to find which *changeable* features separate a user from the next segment (employment, tenure, income) and never suggests immutable traits (age, gender, marital status, citizenship).

## 4. Validation

- **Class alignment (primary insight).** The model never saw `Class`, yet the four segments separate cleanly by historical approval rate — **~20% / ~40% / ~80% / ~90%** — strong evidence the clusters capture something real.
- **Silhouette.** k=2 = 0.186 (strongest); k=4 = 0.158 (chosen, all groups well-sized: 364/176/82/68); k=3 = 0.148.
- **Reproducibility.** Fixed seeds; 98% one-at-a-time vs batch agreement (above).

## 5. Limitations

- Features are anonymized; friendly interpretations are inferred, not confirmed (see §7). One flag (A9) behaves opposite to a "prior default" reading, which we flag rather than trust.
- The 2-D PCA map captures ~35% of total variance — a simplified view; clusters that overlap in 2-D may separate in full space.
- `Class` reflects past human lending decisions and may carry historical bias; we use it only for validation/context, never as a target.
- Small dataset (689 rows); segments are descriptive, not predictive.

## 6. Responsible AI

See `RESPONSIBLE_AI.md` (≤200-word statement). In brief: never a prediction or score; limit figures are general guidance, not offers; label used only for validation; recommendations limited to legitimate, changeable behaviors; no data stored.

## 7. Column Name Assignments

*(Intentionally left blank — to be completed.)* Our inferred, plain-language interpretations of A1–A14 (with confidence and rationale) will be documented here. Until then, A1–A14 remain the canonical keys; any friendly labels in the app are presented as inferred, not ground truth.

| Code | Inferred name | Confidence | Rationale |
|---|---|---|---|
| A1 | | | |
| A2 | | | |
| A3 | | | |
| A4 | | | |
| A5 | | | |
| A6 | | | |
| A7 | | | |
| A8 | | | |
| A9 | | | |
| A10 | | | |
| A11 | | | |
| A12 | | | |
| A13 | | | |
| A14 | | | |
