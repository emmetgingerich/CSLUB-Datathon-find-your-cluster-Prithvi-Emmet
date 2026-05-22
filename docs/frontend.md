# Frontend Design (UI / UX) — Find Your Cluster

**Project:** Find Your Cluster (Datathon Pillar 2 · USML)
**Doc:** 3 of 3 (System Requirements → Backend → **Frontend**)
**Version:** 0.1 · **Owners:** Emmet, Prithvi
**Implements:** FR-2, FR-3, FR-4, FR-5, FR-7, FR-8, FR-9, FR-10, FR-11 and NFR-7, NFR-8.

> Refines **NFR-8**: the design principle is updated from generic "Swiss" to a
> **Capital One-inspired** language — which keeps the Swiss foundations (grid,
> hierarchy, generous whitespace) but adds brand warmth, color, and plain-language
> copy suited to a consumer finance tool.

---

## 1. Design principles (Capital One-inspired)

We mimic Capital One's *public design principles*, using our own assets and palette in
that spirit — not their logo or trademarks.

- **Human** — plain, encouraging language; talk to the user, not at them.
- **Clear** — one primary action per screen; never make the user guess what's next.
- **Confident & calm** — generous whitespace, strong type hierarchy, restrained color.
- **Accessible** — high contrast, large tap targets, readable type, keyboard-friendly.
- **Trustworthy** — honest framing, visible caveats, no dark patterns in the real product.

## 2. Design tokens

| Token | Value | Use |
|---|---|---|
| Navy (primary) | `#004977` | headlines, primary surfaces |
| Red (accent) | `#D03027` | primary CTA, key highlights (sparingly) |
| Ink | `#11151C` | body text |
| Muted | `#6B7280` | secondary text, captions |
| Surface | `#F7F8FA` | cards / section backgrounds |
| White | `#FFFFFF` | page background |
| Font | Inter (stand-in for Capital One's "Optimist") | 700 headlines / 600 buttons / 400 body |
| Radius | 12px cards · 8px inputs · pill buttons | |
| Spacing | 4 / 8 / 16 / 24 / 40 / 64 px scale | consistent rhythm |
| Shadow | `0 1px 3px rgba(17,21,28,.08)` | subtle card lift only |

## 3. Screen flow

```
Landing  ->  Intent ("what are you looking for")  ->  Questionnaire
   ->  Paywall (skippable, demo)  ->  Results
```

Managed by a single `page` value in session state; each button advances it.

### 3.1 Landing (hero)
- **Headline:** "See where you fit."
- **Subhead:** "A clear, judgment-free look at which group of applicants you're most like — built for *you*, not for a bank."
- **Primary CTA (red):** "Get started" -> Intent.
- **Secondary (text link):** "Try an example" -> loads an example user and jumps to Results.
- Lots of whitespace, navy headline, single red button. No clutter.

### 3.2 Intent — "say what you're looking for"
- **Prompt:** "What brings you here?"
- **Three choices (cards):** *Understand my profile* · *See who's similar to me* · *Just exploring.*
- Selection personalizes the results copy and advances to the Questionnaire. (FR personalization; no model impact.)

### 3.3 Questionnaire (diagnostic questions)
- Multi-step, grouped so it never feels like a wall of fields. Progress indicator at top.
  - **About you:** Age, Gender, Marital status, Citizenship status
  - **Work & stability:** Currently employed, Years employed, Occupation, Years at address, Driver's license
  - **Finances:** Annual income, Debt (thousands), Creditworthiness tier *(uncertain)*, Zip *(uncertain)*
- Labels come from the bundle's `friendly` map; uncertain ones are shown softened/footnoted (RAI-3).
- Sensible defaults pre-filled; every question optional ("use typical value"). Back / Next buttons.
- Implements FR-2, FR-3, FR-6.

### 3.4 Paywall (skippable interstitial)
- Shown after the questionnaire, before results. **A demonstration of a common monetization point — disabled by default.**
- **Copy:** "Your profile is ready." Card: "Unlock your full breakdown — $4.99" with a short benefit list.
- **Primary button:** "Unlock" (non-functional concept in the demo).
- **Secondary link (always works):** "Continue for free" -> Results. *In the live demo we click this.*
- **Responsible-AI note:** charging credit applicants to see information about themselves raises a real fairness concern. The product keeps this **off by default**; in the presentation we name it explicitly as a monetization *opportunity* and acknowledge the tension rather than hiding it. This honesty is the point — it shows we understand the business model AND its ethics.

### 3.5 Results
- **Cluster headline:** "You're most like: *{cluster name}*", with a plain-language description (tone tuned by the chosen intent).
- **You vs. typical member** — small comparison table (FR-7).
- **"You are here" map** — PCA scatter of all applicants, the user's point highlighted (FR-8).
- **"How typical are you"** — central / typical / on-the-edge, naming the nearest other cluster when borderline, framed as orientation (FR-9, RAI-5).
- **Historical context** — cluster approval rate inside a clearly-marked caveat box (FR-10, RAI-2).
- **No approve/deny anywhere** (FR-11).
- **Footer actions:** "Start over" · "Try an example."

## 4. Components
- **Buttons:** primary = filled red pill; secondary = navy outline; tertiary = text link.
- **Cards:** white on `#F7F8FA`, 12px radius, subtle shadow, generous padding.
- **Progress:** thin navy bar with step count ("Step 2 of 3").
- **Caveat box:** muted surface, left accent border, small print — used for all bias/limitation notes.

## 5. Streamlit implementation notes
- **Routing:** `st.session_state["page"]` in {`landing`,`intent`,`questionnaire`,`paywall`,`results`}; buttons set the next page and call `st.rerun()`.
- **Styling:** inject one CSS block via `st.markdown(..., unsafe_allow_html=True)` for fonts, palette, button shapes; hide default Streamlit chrome (menu/footer) for a cleaner canvas.
- **Layout:** use `st.columns` for grid alignment; `st.container(border=True)` as cards.
- **Separation:** `app.py` renders only; every value comes from `backend.py` (assign_cluster, map_position, typicality, get_cluster_info, list_examples, random_applicant).

## 6. Accessibility
- Text/background contrast meets WCAG AA; minimum 16px body type.
- Every input has a visible label; the flow is operable by keyboard.
- Color is never the only signal (icons/text accompany it).

## 7. Acceptance (frontend slice)
- [ ] Landing -> Intent -> Questionnaire -> Paywall -> Results flows without dead ends.
- [ ] "Continue for free" reliably reaches Results in the demo.
- [ ] Results shows cluster, comparison, map, typicality, and caveated context.
- [ ] No approve/deny text appears.
- [ ] App does not look like default Streamlit (custom palette, type, spacing applied).
