# Frontend Design (UI / UX) — Credit Cat

**Doc:** 3 of 3 · **Version:** 0.2 · **Owners:** Emmet, Prithvi
**Implements:** FR-2, FR-3, FR-4, FR-5, FR-7..FR-12 and NFR-7, NFR-8.

---

## 1. Brand & principles
**Credit Cat** — friendly but trustworthy consumer finance tool. Capital One-inspired
(human, clear, confident, accessible, honest) with a Curology-style multi-section landing.

## 2. Design tokens
| Token | Value |
|---|---|
| Navy (primary) | `#004977` |
| Red (accent / CTA) | `#D03027` |
| Ink / Muted / Surface | `#11151C` / `#6B7280` / `#F7F8FA` |
| Font | Archivo (400–900) |
| Logo | recoloured cat: navy outline, white face, red accent ear + nose, pink cheeks |
| Segment colours | Builder = green `#1F9E55` · Established = blue `#2E7DD1` · Quiet File = silver `#9AA3AB` · Veteran = gold `#E0A53B` |
| Radius / shadow | 14–16px cards · subtle `0 1px 3px rgba(17,21,28,.06)` |

## 3. Top bar (every page)
White header: cat logo + "CreditCat" wordmark (left), spaced nav buttons **Home · How it works · Why Credit Cat**, and a red **Find my cluster** CTA (right), with a rule beneath.

## 4. Screens
- **Landing:** hero; stats band (4 segments · 689 applicants · 38 signals · $0 stored); "How it works" (3 steps); "What you'll learn" (2×2); navy "A tool, not a verdict" band; FAQ (3 expanders); closing CTA; footer.
- **Intent:** "What brings you here?" (3 choices) → personalises results copy.
- **Questionnaire:** one question per screen, fade + slide-up, 14 light-blue progress dots, Back/Next.
- **Paywall (skippable):** large standout "Your profile is almost ready" headline; pricing card; "Unlock" (demo) + "Continue for free"; RAI caveat. Off by default.
- **Results (dashboard):** header panel (tier badge + segment name + meaning); KPI row (typical limit / approval-in-data / how-typical); two panels (what matters | likely cards); "You are here" map (own segment vibrant, others faded, red star = you); optional "A blend" panel; combined caveat; footer.

## 5. Implementation
- Routing via `st.session_state["page"]`; one CSS block; default Streamlit chrome hidden.
- `st.container(border=True)` for section cards; `st.columns` for grid/KPIs; matplotlib for the map (custom full-colour legend).
- All values come from `backend.py`; display copy from `CONTENT`.

## 6. Accessibility — AA contrast; ≥16px body; visible labels; colour never the only signal (the user is also marked by a star + text).

## 7. Acceptance — flows end-to-end with no dead ends; top bar on every page; map highlights the user's segment; no approve/deny text; does not look like default Streamlit.
