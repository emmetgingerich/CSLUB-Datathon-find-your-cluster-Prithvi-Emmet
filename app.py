"""
app.py — Credit Cat (UI only).

All model/data logic comes from backend.py. Display copy (cluster names, what each
segment means, credit-limit context) lives in CONTENT below — presentation, not model
logic, so the bundle is unchanged.

Flow: Landing -> Intent -> Questionnaire (one at a time) -> Paywall -> Results (dashboard)
Run from the repo root:  streamlit run app.py
"""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import backend

st.set_page_config(page_title="Credit Cat", page_icon="🐱", layout="centered")

NAVY, RED, INK, MUTED, SURFACE = "#004977", "#D03027", "#11151C", "#6B7280", "#F7F8FA"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"], .stMarkdown, .stButton button {{ font-family:'Archivo',sans-serif; }}
#MainMenu, header, footer {{ visibility:hidden; }}
.block-container {{ max-width:840px; padding-top:1.1rem; }}
@keyframes fadeUp {{ from {{opacity:0; transform:translateY(14px);}} to {{opacity:1; transform:translateY(0);}} }}
h1,h2,h3 {{ color:{NAVY}; font-weight:800; letter-spacing:-0.02em; }}

/* top header bar */
.logo {{ font-weight:900; color:{NAVY}; font-size:1.3rem; letter-spacing:-0.02em; line-height:2.4rem; }}
.logo b {{ color:{RED}; }}
.navlinks {{ color:{MUTED}; font-weight:600; font-size:.9rem; line-height:2.4rem; }}
hr.rule {{ border:none; border-top:1px solid #E3E8EE; margin:.2rem 0 1.4rem; }}

.eyebrow {{ color:{RED}; font-weight:700; letter-spacing:.12em; text-transform:uppercase; font-size:.76rem; margin-bottom:.3rem; }}
.hero h1 {{ font-size:3.5rem; line-height:1.02; color:{NAVY}; font-weight:900; letter-spacing:-0.03em; margin:.2rem 0; }}
.hero p {{ font-size:1.18rem; color:{MUTED}; line-height:1.5; margin:.6rem 0 1.4rem; max-width:34rem; }}

.band {{ background:{NAVY}; color:#fff; border-radius:16px; padding:1.4rem 1.6rem; margin:1.6rem 0; }}
.band b {{ color:#fff; }}
.statband {{ background:{SURFACE}; border-radius:16px; padding:1.1rem 1.3rem; margin:1.4rem 0;
  display:flex; justify-content:space-around; text-align:center; flex-wrap:wrap; gap:.6rem; }}
.statband .v {{ color:{NAVY}; font-weight:900; font-size:1.5rem; }}
.statband .l {{ color:{MUTED}; font-size:.82rem; }}
.step {{ background:{SURFACE}; border-radius:14px; padding:1.1rem; height:100%; }}
.step .n {{ color:{RED}; font-weight:900; font-size:1.4rem; }}
.step .t {{ color:{NAVY}; font-weight:800; margin:.2rem 0; }}
.step .d {{ color:{MUTED}; font-size:.92rem; line-height:1.45; }}
.learn {{ border:1px solid #E3E8EE; border-radius:14px; padding:1rem 1.15rem; height:100%; background:#fff; }}
.learn .t {{ color:{NAVY}; font-weight:800; }}
.learn .d {{ color:{MUTED}; font-size:.9rem; line-height:1.45; }}
.section-h {{ font-size:1.5rem; font-weight:800; color:{NAVY}; margin:1.8rem 0 .4rem; }}

[data-testid="stVerticalBlockBorderWrapper"] {{ border:1px solid #E3E8EE; border-radius:16px; background:#fff;
  box-shadow:0 1px 3px rgba(17,21,28,.06); padding:.6rem .4rem; }}
.sec-title {{ font-size:1.15rem; font-weight:800; color:{NAVY}; border-left:4px solid {RED}; padding-left:.6rem; margin:.1rem 0 1rem; }}
.q-title {{ font-size:1.7rem; font-weight:800; color:{NAVY}; margin:.2rem 0 .9rem; letter-spacing:-0.02em; }}

.result-name {{ font-size:2.6rem; color:{NAVY}; font-weight:900; line-height:1.05; letter-spacing:-0.02em; }}
.badge {{ display:inline-block; background:{NAVY}; color:#fff; font-weight:700; font-size:.78rem;
  letter-spacing:.04em; padding:.25rem .7rem; border-radius:999px; }}
.kpi {{ background:{SURFACE}; border-radius:14px; padding:1rem 1.1rem; height:100%; }}
.kpi .l {{ color:{MUTED}; font-size:.74rem; text-transform:uppercase; letter-spacing:.06em; }}
.kpi .v {{ color:{NAVY}; font-weight:900; font-size:1.7rem; line-height:1.15; margin-top:.2rem; }}
.kpi .s {{ color:{MUTED}; font-size:.82rem; margin-top:.15rem; }}
.panel-text {{ color:{INK}; font-size:.95rem; line-height:1.5; }}

.dots {{ display:flex; gap:7px; margin:.3rem 0 1.3rem; flex-wrap:wrap; }}
.dot {{ width:11px; height:11px; border-radius:50%; background:#CFE3EE; transition:background .35s ease; }}
.dot.on {{ background:#2E8BC0; }}

.stButton>button {{ border-radius:999px; font-weight:600; padding:.5rem 1.3rem; border:1.5px solid {NAVY}; color:{NAVY}; background:#fff; }}
.stButton>button:hover {{ color:#fff; background:{NAVY}; }}
.stButton>button[kind="primary"] {{ background:{RED}; border-color:{RED}; color:#fff; }}
.stButton>button[kind="primary"]:hover {{ background:#b1271f; border-color:#b1271f; }}
.caveat {{ background:{SURFACE}; border-left:4px solid {RED}; border-radius:8px; padding:1rem 1.2rem; color:{INK}; font-size:.9rem; line-height:1.5; margin-top:.6rem; }}
.card {{ background:{SURFACE}; border-radius:12px; padding:1.2rem 1.4rem; margin:.5rem 0; }}
ul.matters {{ margin:.3rem 0 0; padding-left:1.1rem; color:{INK}; }}
ul.matters li {{ margin:.35rem 0; line-height:1.45; }}
.foot {{ color:{MUTED}; font-size:.8rem; text-align:center; margin:2.4rem 0 .5rem; line-height:1.5; }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
st.session_state.setdefault("page", "landing")
st.session_state.setdefault("answers", backend.defaults())
st.session_state.setdefault("intent", "explore")
st.session_state.setdefault("qidx", 0)

FRIENDLY = backend.friendly_labels()
CAT_OPTS = backend.category_options()
BINARY = set(backend.load_bundle()["binary_cols"])
CATEG = set(backend.load_bundle()["categorical_cols"])

RANGES = {"A2": (18.0, 90.0), "A3": (0.0, 30.0), "A7": (0.0, 30.0),
          "A10": (0.0, 70.0), "A13": (0.0, 2000.0), "A14": (0.0, 100001.0)}

QUESTION_ORDER = []
for _section, _codes in [("About you", ["A2", "A1", "A4", "A12"]),
                         ("Work & stability", ["A8", "A3", "A6", "A7", "A11"]),
                         ("Finances", ["A14", "A10", "A5", "A13", "A9"])]:
    for _c in _codes:
        QUESTION_ORDER.append((_c, _section))

CONTENT = {
    0: {"name": "The Builder", "tier": "New-to-credit · Thin file",
        "meaning": "You look like someone early in their credit journey, with a light track record "
                   "for lenders to read. Approvals are tougher and starting limits are modest — but "
                   "this is also the most improvable place to be.",
        "limit": "$200 – $1,000", "cards": "Secured & student cards (a deposit often sets the limit)",
        "matters": ["On-time payments are the single biggest driver from here.",
                    "A secured card lets your deposit set the limit, so you control it.",
                    "Keeping balances under ~30% of the limit builds score fastest."]},
    2: {"name": "The Quiet File", "tier": "Near-prime · Light history",
        "meaning": "You resemble applicants with relatively little recent activity on file. There's a "
                   "foundation, but not much fresh signal — so approvals can be a coin-flip and limits "
                   "stay cautious until there's more history.",
        "limit": "$500 – $2,500", "cards": "Entry unsecured or secured starter cards",
        "matters": ["Small, regular, fully-paid activity adds the recent signal lenders want.",
                    "A starter card used lightly and paid in full reads well over time.",
                    "Utilization under 30% matters even at lower limits."]},
    1: {"name": "The Established", "tier": "Prime",
        "meaning": "You resemble applicants with an active, healthy record. You're in the range most "
                   "mainstream cards are designed for, with solid approval odds and room to grow.",
        "limit": "$3,000 – $10,000", "cards": "Standard unsecured cards, with rewards cards in reach",
        "matters": ["Strong approval odds for mainstream cards.",
                    "A credit-line increase after 6–12 clean months is common.",
                    "Low utilization keeps you trending toward super-prime."]},
    3: {"name": "The Veteran", "tier": "Super-prime · Seasoned",
        "meaning": "You resemble the lowest-risk tier — a long, deep credit history. Approvals are "
                   "typically easy and limits are the highest, often well above the national average.",
        "limit": "$10,000+", "cards": "Rewards & premium cards, highest limits",
        "matters": ["You likely qualify for the best rates and rewards.",
                    "High limits keep utilization low almost automatically.",
                    "Worth comparing premium cards for perks you'd actually use."]},
}
NAMES = {cid: CONTENT[cid]["name"] for cid in CONTENT}
INTENT_INTRO = {"understand": "Here's a clear look at your profile.",
                "similar": "Here are the people most similar to you.",
                "explore": "Here's what we found."}
CLUSTER_PALETTE = {0: "#9CC3D5", 1: "#4A90A4", 2: "#C9CDD2", 3: "#1F5C73"}


def goto(page):
    st.session_state.page = page
    st.rerun()


def top_bar():
    """White header bar with logo + nav + CTA — rendered on every page."""
    left, right = st.columns([3, 1.2])
    left.markdown('<span class="logo">🐱 Credit<b>Cat</b></span>'
                  '<span class="navlinks">&nbsp;&nbsp;&nbsp;Home&nbsp;·&nbsp;How it works&nbsp;·&nbsp;Why Credit Cat</span>',
                  unsafe_allow_html=True)
    if right.button("Find my cluster", type="primary", use_container_width=True, key="nav_cta"):
        st.session_state.qidx = 0
        goto("intent")
    st.markdown('<hr class="rule">', unsafe_allow_html=True)


def footer():
    st.markdown('<p class="foot">Credit Cat · a self-discovery tool, not a lender. '
                'Nothing you enter is stored. Not a credit decision.</p>', unsafe_allow_html=True)


def dots_html(qidx, total):
    spans = "".join(f'<span class="dot {"on" if i <= qidx else ""}"></span>' for i in range(total))
    return f'<div class="dots">{spans}</div>'


# ---------------------------------------------------------------------------
# Landing
# ---------------------------------------------------------------------------
def landing():
    top_bar()
    st.markdown('<div class="hero"><h1>Find your<br>credit cluster.</h1>'
                '<p>Answer a few quick questions and see which group of real applicants you most '
                'resemble — what it means, what you might qualify for, and what actually moves the '
                'needle. Built for <b>you</b>, not for a bank.</p></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("Get started", type="primary", use_container_width=True, key="hero_start"):
        st.session_state.qidx = 0
        goto("intent")
    if c2.button("Try an example", use_container_width=True, key="hero_example"):
        st.session_state.answers = backend.list_examples()[3].copy()
        st.session_state.intent = "explore"
        goto("results")

    st.markdown('<div class="statband">'
                '<div><div class="v">4</div><div class="l">credit segments</div></div>'
                '<div><div class="v">689</div><div class="l">applicants analyzed</div></div>'
                '<div><div class="v">38</div><div class="l">signals per person</div></div>'
                '<div><div class="v">$0</div><div class="l">data stored</div></div></div>',
                unsafe_allow_html=True)

    st.markdown('<p class="section-h">How it works</p>', unsafe_allow_html=True)
    steps = [("1", "Answer a few questions", "A handful of details, one at a time. Takes about a minute."),
             ("2", "We find your cluster", "An unsupervised model matches you to one of four real applicant groups."),
             ("3", "See what it means", "Your segment, a typical credit-limit range, and what to focus on next.")]
    for col, (n, t, d) in zip(st.columns(3), steps):
        col.markdown(f'<div class="step"><div class="n">{n}</div><div class="t">{t}</div>'
                     f'<div class="d">{d}</div></div>', unsafe_allow_html=True)

    st.markdown('<p class="section-h">What you\'ll learn</p>', unsafe_allow_html=True)
    learn = [("Where you fit", "Which of four credit segments you most resemble — and how clearly."),
             ("What you might get", "Typical starting credit-limit ranges and card types for that profile."),
             ("What actually matters", "The few things that move a profile like yours forward."),
             ("How typical you are", "Whether you're squarely in your group or sitting between two.")]
    cells = list(st.columns(2)) + list(st.columns(2))
    for col, (t, d) in zip(cells, learn):
        col.markdown(f'<div class="learn"><div class="t">{t}</div><div class="d">{d}</div></div>',
                     unsafe_allow_html=True)

    st.markdown('<div class="band"><b>A tool, not a verdict.</b><br>'
                'Credit Cat never decides whether you\'ll be approved. It shows you where you sit and '
                'what it tends to mean. Nothing you enter is stored.</div>', unsafe_allow_html=True)

    st.markdown('<p class="section-h">Common questions</p>', unsafe_allow_html=True)
    with st.expander("Is this a credit score or an approval decision?"):
        st.write("No. Credit Cat groups you with similar applicants and explains what that tends to "
                 "mean. It never predicts approval or assigns a score.")
    with st.expander("Where do the credit-limit ranges come from?"):
        st.write("They're general industry figures for similar credit profiles, not offers. Your real "
                 "limit depends on the lender, your income, and your full credit file.")
    with st.expander("Do you store my answers?"):
        st.write("No. Everything is processed in your browser session and discarded — nothing is saved.")

    mid = st.columns([1, 2, 1])[1]
    if mid.button("Find my cluster →", type="primary", use_container_width=True, key="cta_bottom"):
        st.session_state.qidx = 0
        goto("intent")
    footer()


def intent():
    top_bar()
    st.markdown('<p class="eyebrow">Step 1 of 3</p>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<p class="q-title">What brings you here?</p>', unsafe_allow_html=True)
        for key, label in [("understand", "Understand my profile"),
                           ("similar", "See who's similar to me"),
                           ("explore", "I'm just exploring")]:
            if st.button(label, use_container_width=True, key=f"intent_{key}"):
                st.session_state.intent = key
                st.session_state.qidx = 0
                goto("questionnaire")
    if st.button("← Back", key="intent_back"):
        goto("landing")


def render_widget(code):
    label = FRIENDLY[code].split(" (")[0].replace("_", " ")
    cur = st.session_state.answers[code]
    if code in BINARY:
        val = st.selectbox(label, [0, 1], index=[0, 1].index(int(cur)), label_visibility="collapsed",
                           help="Coded 0/1; the exact meaning of each value isn't disclosed in the data.")
    elif code in CATEG:
        opts = CAT_OPTS[code]
        idx = opts.index(int(cur)) if int(cur) in opts else 0
        val = st.selectbox(label, opts, index=idx, label_visibility="collapsed")
    else:
        lo, hi = RANGES[code]
        val = st.number_input(label, lo, hi, float(min(max(cur, lo), hi)), label_visibility="collapsed")
    st.session_state.answers[code] = val


def questionnaire():
    qidx = st.session_state.qidx
    total = len(QUESTION_ORDER)
    code, section = QUESTION_ORDER[qidx]
    last = qidx == total - 1
    st.markdown("<style>.block-container{animation:fadeUp .35s ease;}</style>", unsafe_allow_html=True)

    top_bar()
    st.markdown(f'<p class="eyebrow">{section} · Question {qidx + 1} of {total}</p>', unsafe_allow_html=True)
    st.markdown(dots_html(qidx, total), unsafe_allow_html=True)

    label = FRIENDLY[code].split(" (")[0].replace("_", " ")
    note = FRIENDLY[code][FRIENDLY[code].find("(") + 1:-1] if "(" in FRIENDLY[code] else ""
    with st.container(border=True):
        st.markdown(f'<p class="q-title">{label}</p>', unsafe_allow_html=True)
        render_widget(code)
        if note:
            st.caption("⚠️ " + note)

    c1, c2 = st.columns(2)
    if c1.button("← Back", use_container_width=True, key="q_back"):
        if qidx == 0:
            goto("intent")
        else:
            st.session_state.qidx -= 1
            st.rerun()
    if c2.button("See my results →" if last else "Next →", type="primary", use_container_width=True, key="q_next"):
        if last:
            goto("paywall")
        else:
            st.session_state.qidx += 1
            st.rerun()


def paywall():
    top_bar()
    st.markdown('<p class="eyebrow">Almost there</p>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<p class="sec-title">Your profile is ready</p>', unsafe_allow_html=True)
        st.markdown('<div class="card"><div class="kpi" style="display:inline-block;background:transparent;padding:0;">'
                    '<span class="v">$4.99</span></div>'
                    '<p style="margin:.4rem 0;"><b>Unlock your full breakdown</b></p>'
                    '<ul class="matters"><li>Your segment and what it means</li>'
                    '<li>Typical credit-limit range &amp; card types</li>'
                    '<li>Your position on the applicant map</li></ul></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("Unlock — $4.99", type="primary", use_container_width=True, key="pay_unlock"):
            st.toast("Payment is disabled in this demo — use 'Continue for free'.")
        if c2.button("Continue for free", use_container_width=True, key="pay_free"):
            goto("results")
    st.markdown('<div class="caveat">This paywall is a <b>demonstration</b> of a common monetization '
                'point, switched off by default. Charging applicants to see information about themselves '
                'raises real fairness concerns, which we name openly rather than hide.</div>',
                unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Results — dashboard
# ---------------------------------------------------------------------------
def results():
    raw = st.session_state.answers
    cid = backend.assign_cluster(raw)
    info = backend.get_cluster_info(cid)
    typ = backend.typicality(raw)
    c = CONTENT[cid]

    top_bar()
    st.markdown(f'<p class="eyebrow">{INTENT_INTRO[st.session_state.intent]}</p>', unsafe_allow_html=True)

    # header panel
    with st.container(border=True):
        st.markdown(f'<span class="badge">{c["tier"]}</span>', unsafe_allow_html=True)
        st.markdown(f'<p class="result-name">{c["name"]}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="panel-text">{c["meaning"]}</p>', unsafe_allow_html=True)

    # KPI row
    k1, k2, k3 = st.columns(3)
    k1.markdown(f'<div class="kpi"><div class="l">Typical starting limit</div>'
                f'<div class="v">{c["limit"]}</div><div class="s">general range for similar profiles</div></div>',
                unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi"><div class="l">Approved in the data</div>'
                f'<div class="v">{info["approval_rate"]:.0%}</div><div class="s">historical, not a prediction</div></div>',
                unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi"><div class="l">How typical you are</div>'
                f'<div class="v" style="font-size:1.25rem;">{typ["label"].title()}</div>'
                f'<div class="s">within your group</div></div>', unsafe_allow_html=True)

    # two panels: what matters | likely cards
    p1, p2 = st.columns([1.4, 1])
    with p1.container(border=True):
        st.markdown('<p class="sec-title">What actually matters from here</p>', unsafe_allow_html=True)
        st.markdown('<ul class="matters">' + "".join(f"<li>{m}</li>" for m in c["matters"]) + '</ul>',
                    unsafe_allow_html=True)
    with p2.container(border=True):
        st.markdown('<p class="sec-title">Likely cards</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="panel-text">{c["cards"]}</p>', unsafe_allow_html=True)

    # map panel
    with st.container(border=True):
        st.markdown('<p class="sec-title">You are here</p>', unsafe_allow_html=True)
        st.caption("Every applicant in the data, mapped to 2-D. The red star is you.")
        coords, labels = backend.get_training_map()
        ux, uy = backend.map_position(raw)
        fig, ax = plt.subplots(figsize=(6, 4.6))
        for cc in sorted(set(labels)):
            m = labels == cc
            ax.scatter(coords[m, 0], coords[m, 1], s=15, alpha=0.55,
                       color=CLUSTER_PALETTE.get(int(cc), "#999"), label=NAMES[int(cc)])
        ax.scatter([ux], [uy], s=320, marker="*", color=RED, edgecolor="white",
                   linewidth=1.3, zorder=5, label="You")
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.legend(loc="best", fontsize=8, frameon=False)
        fig.tight_layout()
        st.pyplot(fig)

    if typ["label"] == "on the edge":
        with st.container(border=True):
            st.markdown('<p class="sec-title">A blend</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="panel-text">You also sit close to <b>{NAMES[typ["nearest_other"]]}</b> — '
                        "a bit of a blend between the two. That's just where you land, not something you "
                        "need to change.</p>", unsafe_allow_html=True)

    st.markdown(f'<div class="caveat">Limit ranges and card types above are <b>general industry context</b> '
                f'for similar profiles — they vary by lender and income, and are <b>not</b> an offer, a score, '
                f'or a prediction for you. The historical approval figure reflects past human lending '
                f'decisions, which may carry bias.</div>', unsafe_allow_html=True)

    st.write("")
    c1, c2 = st.columns(2)
    if c1.button("Start over", key="res_restart"):
        st.session_state.answers = backend.defaults()
        st.session_state.qidx = 0
        goto("landing")
    if c2.button("Try another example", key="res_example"):
        order = sorted(CONTENT)
        nxt = order[(order.index(cid) + 1) % len(order)]
        st.session_state.answers = backend.list_examples()[nxt].copy()
        goto("results")
    footer()


PAGES = {"landing": landing, "intent": intent, "questionnaire": questionnaire,
         "paywall": paywall, "results": results}
PAGES[st.session_state.page]()
