"""
app.py — ClusterDawg (UI only).

All model/data logic comes from backend.py. Display copy (cluster names, what each
segment means, credit-limit context) lives in CONTENT below — it is presentation,
not model logic, so the bundle is unchanged.

Flow: Landing -> Intent -> Questionnaire (one question at a time) -> Paywall -> Results
Run from the repo root:  streamlit run app.py
"""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import backend

st.set_page_config(page_title="ClusterDawg", page_icon="🐾", layout="centered")

NAVY, RED, INK, MUTED, SURFACE = "#004977", "#D03027", "#11151C", "#6B7280", "#F7F8FA"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"], .stMarkdown, .stButton button {{ font-family:'Archivo',sans-serif; }}
#MainMenu, header, footer {{ visibility:hidden; }}
.block-container {{ max-width:820px; padding-top:1.6rem; }}
@keyframes fadeUp {{ from {{opacity:0; transform:translateY(14px);}} to {{opacity:1; transform:translateY(0);}} }}

h1,h2,h3 {{ color:{NAVY}; font-weight:800; letter-spacing:-0.02em; }}
.brand {{ font-weight:900; color:{NAVY}; font-size:1.15rem; letter-spacing:-0.02em; }}
.brand span {{ color:{RED}; }}
.eyebrow {{ color:{RED}; font-weight:700; letter-spacing:.12em; text-transform:uppercase; font-size:.76rem; margin-bottom:.3rem; }}

.hero h1 {{ font-size:3.4rem; line-height:1.02; color:{NAVY}; font-weight:900; letter-spacing:-0.03em; margin:.2rem 0; }}
.hero p {{ font-size:1.18rem; color:{MUTED}; line-height:1.5; margin:.6rem 0 1.4rem; max-width:34rem; }}

.band {{ background:{NAVY}; color:#fff; border-radius:16px; padding:1.4rem 1.6rem; margin:1.6rem 0; }}
.band b {{ color:#fff; }}
.step {{ background:{SURFACE}; border-radius:14px; padding:1.1rem 1.1rem; height:100%; }}
.step .n {{ color:{RED}; font-weight:900; font-size:1.4rem; }}
.step .t {{ color:{NAVY}; font-weight:800; margin:.2rem 0; }}
.step .d {{ color:{MUTED}; font-size:.92rem; line-height:1.45; }}
.learn {{ border:1px solid #E3E8EE; border-radius:14px; padding:1rem 1.15rem; height:100%; background:#fff; }}
.learn .t {{ color:{NAVY}; font-weight:800; }}
.learn .d {{ color:{MUTED}; font-size:.9rem; line-height:1.45; }}
.section-h {{ font-size:1.5rem; font-weight:800; color:{NAVY}; margin:1.8rem 0 .4rem; }}
.section-sub {{ color:{MUTED}; margin:0 0 1rem; }}

[data-testid="stVerticalBlockBorderWrapper"] {{ border:1px solid #E3E8EE; border-radius:16px; background:#fff;
  box-shadow:0 1px 3px rgba(17,21,28,.06); padding:.6rem .4rem; }}
.sec-title {{ font-size:1.15rem; font-weight:800; color:{NAVY}; border-left:4px solid {RED}; padding-left:.6rem; margin:.1rem 0 1rem; }}
.q-title {{ font-size:1.7rem; font-weight:800; color:{NAVY}; margin:.2rem 0 .9rem; letter-spacing:-0.02em; }}

.result-name {{ font-size:2.6rem; color:{NAVY}; font-weight:900; line-height:1.05; letter-spacing:-0.02em; }}
.badge {{ display:inline-block; background:{NAVY}; color:#fff; font-weight:700; font-size:.78rem;
  letter-spacing:.04em; padding:.25rem .7rem; border-radius:999px; }}
.metric {{ background:{SURFACE}; border-radius:14px; padding:1rem 1.1rem; height:100%; }}
.metric .l {{ color:{MUTED}; font-size:.8rem; text-transform:uppercase; letter-spacing:.06em; }}
.metric .v {{ color:{NAVY}; font-weight:900; font-size:1.5rem; line-height:1.2; margin-top:.2rem; }}
.metric .s {{ color:{MUTED}; font-size:.85rem; margin-top:.15rem; }}

.dots {{ display:flex; gap:7px; margin:.3rem 0 1.3rem; flex-wrap:wrap; }}
.dot {{ width:11px; height:11px; border-radius:50%; background:#CFE3EE; transition:background .35s ease; }}
.dot.on {{ background:#2E8BC0; }}

.stButton>button {{ border-radius:999px; font-weight:600; padding:.55rem 1.4rem; border:1.5px solid {NAVY}; color:{NAVY}; background:#fff; }}
.stButton>button:hover {{ color:#fff; background:{NAVY}; }}
.stButton>button[kind="primary"] {{ background:{RED}; border-color:{RED}; color:#fff; }}
.stButton>button[kind="primary"]:hover {{ background:#b1271f; border-color:#b1271f; }}
.caveat {{ background:{SURFACE}; border-left:4px solid {RED}; border-radius:8px; padding:1rem 1.2rem; color:{INK}; font-size:.9rem; line-height:1.5; margin-top:.6rem; }}
.card {{ background:{SURFACE}; border-radius:12px; padding:1.2rem 1.4rem; margin:.5rem 0; }}
ul.matters {{ margin:.3rem 0 0; padding-left:1.1rem; color:{INK}; }}
ul.matters li {{ margin:.35rem 0; line-height:1.45; }}
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

# Display content per cluster (presentation only). Credit context is GENERAL
# industry guidance for similar profiles — not an offer, score, or prediction.
CONTENT = {
    0: {"name": "The Builder", "tier": "New-to-credit · Thin file",
        "meaning": "You look like someone early in their credit journey, with a light track "
                   "record for lenders to read. Approvals are tougher and starting limits are "
                   "modest — but this is also the most improvable place to be.",
        "limit": "$200 – $1,000", "cards": "Secured & student cards (a deposit often sets the limit)",
        "matters": ["On-time payments are the single biggest driver from here.",
                    "A secured card lets your deposit set the limit, so you control it.",
                    "Keeping balances under ~30% of the limit builds score fastest."]},
    2: {"name": "The Quiet File", "tier": "Near-prime · Light history",
        "meaning": "You resemble applicants with relatively little recent activity on file. "
                   "There's a foundation, but not much fresh signal — so approvals can be a "
                   "coin-flip and limits stay cautious until there's more history.",
        "limit": "$500 – $2,500", "cards": "Entry unsecured or secured starter cards",
        "matters": ["Small, regular, fully-paid activity adds the recent signal lenders want.",
                    "A starter card used lightly and paid in full reads well over time.",
                    "Utilization under 30% matters even at lower limits."]},
    1: {"name": "The Established", "tier": "Prime",
        "meaning": "You resemble applicants with an active, healthy record. You're in the range "
                   "most mainstream cards are designed for, with solid approval odds and room to grow.",
        "limit": "$3,000 – $10,000", "cards": "Standard unsecured cards, with rewards cards in reach",
        "matters": ["Strong approval odds for mainstream cards.",
                    "A credit-line increase after 6–12 clean months is common.",
                    "Low utilization keeps you trending toward super-prime."]},
    3: {"name": "The Veteran", "tier": "Super-prime · Seasoned",
        "meaning": "You resemble the lowest-risk tier — a long, deep credit history. Approvals "
                   "are typically easy and limits are the highest, often well above the national average.",
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


def dots_html(qidx, total):
    spans = "".join(f'<span class="dot {"on" if i <= qidx else ""}"></span>' for i in range(total))
    return f'<div class="dots">{spans}</div>'


def brand_bar():
    st.markdown('<p class="brand">🐾 Cluster<span>Dawg</span></p>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Landing — a real multi-section title page
# ---------------------------------------------------------------------------
def landing():
    brand_bar()
    st.markdown('<div class="hero"><h1>Find your<br>credit cluster.</h1>'
                '<p>Answer a few quick questions and see which group of real applicants '
                'you most resemble — what it means, what you might qualify for, and what '
                'actually moves the needle. Built for <b>you</b>, not for a bank.</p></div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("Get started", type="primary", use_container_width=True):
        st.session_state.qidx = 0
        goto("intent")
    if c2.button("Try an example", use_container_width=True):
        st.session_state.answers = backend.list_examples()[3].copy()
        st.session_state.intent = "explore"
        goto("results")

    st.markdown('<p class="section-h">How it works</p>', unsafe_allow_html=True)
    steps = [("1", "Answer a few questions", "A handful of details about you — one at a time, takes a minute."),
             ("2", "We find your cluster", "An unsupervised model matches you to one of four real applicant groups."),
             ("3", "See what it means", "Your segment, a typical credit-limit range, and what to focus on next.")]
    cols = st.columns(3)
    for col, (n, t, d) in zip(cols, steps):
        col.markdown(f'<div class="step"><div class="n">{n}</div><div class="t">{t}</div>'
                     f'<div class="d">{d}</div></div>', unsafe_allow_html=True)

    st.markdown('<p class="section-h">What you\'ll learn</p>', unsafe_allow_html=True)
    learn = [("Where you fit", "Which of four credit segments you most resemble — and how clearly."),
             ("What you might get", "Typical starting credit-limit ranges and card types for that profile."),
             ("What actually matters", "The few things that move a profile like yours forward."),
             ("How typical you are", "Whether you're squarely in your group or sitting between two.")]
    r1 = st.columns(2)
    r2 = st.columns(2)
    for col, (t, d) in zip(list(r1) + list(r2), learn):
        col.markdown(f'<div class="learn"><div class="t">{t}</div><div class="d">{d}</div></div>',
                     unsafe_allow_html=True)

    st.markdown('<div class="band"><b>A tool, not a verdict.</b><br>'
                'ClusterDawg never decides whether you\'ll be approved. It shows you where you '
                'sit and what it tends to mean. Nothing you enter is stored.</div>',
                unsafe_allow_html=True)

    mid = st.columns([1, 2, 1])[1]
    if mid.button("Find my cluster →", type="primary", use_container_width=True):
        st.session_state.qidx = 0
        goto("intent")


def intent():
    brand_bar()
    st.markdown('<p class="eyebrow">Step 1 of 3</p>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<p class="q-title">What brings you here?</p>', unsafe_allow_html=True)
        for key, label in [("understand", "Understand my profile"),
                           ("similar", "See who's similar to me"),
                           ("explore", "I'm just exploring")]:
            if st.button(label, use_container_width=True):
                st.session_state.intent = key
                st.session_state.qidx = 0
                goto("questionnaire")
    if st.button("← Back"):
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

    brand_bar()
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
    if c1.button("← Back", use_container_width=True):
        if qidx == 0:
            goto("intent")
        else:
            st.session_state.qidx -= 1
            st.rerun()
    if c2.button("See my results →" if last else "Next →", type="primary", use_container_width=True):
        if last:
            goto("paywall")
        else:
            st.session_state.qidx += 1
            st.rerun()


def paywall():
    brand_bar()
    st.markdown('<p class="eyebrow">Almost there</p>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<p class="sec-title">Your profile is ready</p>', unsafe_allow_html=True)
        st.markdown('<div class="card"><span class="metric"><span class="v">$4.99</span></span>'
                    '<p><b>Unlock your full breakdown</b></p>'
                    '<ul class="matters"><li>Your segment and what it means</li>'
                    '<li>Typical credit-limit range & card types</li>'
                    '<li>Your position on the applicant map</li></ul></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("Unlock — $4.99", type="primary", use_container_width=True):
            st.toast("Payment is disabled in this demo — use 'Continue for free'.")
        if c2.button("Continue for free", use_container_width=True):
            goto("results")
    st.markdown('<div class="caveat">This paywall is a <b>demonstration</b> of a common monetization '
                'point, switched off by default. Charging applicants to see information about themselves '
                'raises real fairness concerns, which we name openly rather than hide.</div>',
                unsafe_allow_html=True)


def results():
    raw = st.session_state.answers
    cid = backend.assign_cluster(raw)
    info = backend.get_cluster_info(cid)
    typ = backend.typicality(raw)
    c = CONTENT[cid]

    brand_bar()
    st.markdown(f'<p class="eyebrow">{INTENT_INTRO[st.session_state.intent]}</p>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f'<span class="badge">{c["tier"]}</span>', unsafe_allow_html=True)
        st.markdown(f'<p class="result-name">{c["name"]}</p>', unsafe_allow_html=True)
        st.write(c["meaning"])

    # what you might get — two metric cards
    m1, m2 = st.columns(2)
    m1.markdown(f'<div class="metric"><div class="l">Typical starting limit</div>'
                f'<div class="v">{c["limit"]}</div><div class="s">general range for similar profiles</div></div>',
                unsafe_allow_html=True)
    m2.markdown(f'<div class="metric"><div class="l">Likely card types</div>'
                f'<div class="v" style="font-size:1.05rem;">{c["cards"]}</div></div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<p class="sec-title">What actually matters from here</p>', unsafe_allow_html=True)
        st.markdown('<ul class="matters">' + "".join(f"<li>{m}</li>" for m in c["matters"]) + '</ul>',
                    unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<p class="sec-title">You are here</p>', unsafe_allow_html=True)
        st.caption("Every applicant in the data, mapped to 2-D. The red star is you.")
        coords, labels = backend.get_training_map()
        ux, uy = backend.map_position(raw)
        fig, ax = plt.subplots(figsize=(6, 5))
        for cc in sorted(set(labels)):
            m = labels == cc
            ax.scatter(coords[m, 0], coords[m, 1], s=16, alpha=0.55,
                       color=CLUSTER_PALETTE.get(int(cc), "#999"), label=NAMES[int(cc)])
        ax.scatter([ux], [uy], s=320, marker="*", color=RED, edgecolor="white",
                   linewidth=1.3, zorder=5, label="You")
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.legend(loc="best", fontsize=8, frameon=False)
        fig.tight_layout()
        st.pyplot(fig)

    with st.container(border=True):
        st.markdown('<p class="sec-title">How typical are you</p>', unsafe_allow_html=True)
        st.write(f"Within this group, you're **{typ['label']}**.")
        if typ["label"] == "on the edge":
            st.write(f"You also sit close to **{NAMES[typ['nearest_other']]}** — a bit of a blend "
                     "between the two. That's just where you land, not something you need to change.")

    with st.container(border=True):
        st.markdown('<p class="sec-title">Historical context</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="caveat">In the source data, applicants most like you were approved '
                    f'about <b>{info["approval_rate"]:.0%}</b> of the time. Limit ranges and card types '
                    f'above are <b>general industry context</b> for similar profiles — they vary by lender '
                    f'and income, and are <b>not</b> an offer, a score, or a prediction for you. This data '
                    f'reflects past human lending decisions, which may carry historical bias.</div>',
                    unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    if c1.button("Start over"):
        st.session_state.answers = backend.defaults()
        st.session_state.qidx = 0
        goto("landing")
    if c2.button("Try another example"):
        order = sorted(CONTENT)
        nxt = order[(order.index(cid) + 1) % len(order)]
        st.session_state.answers = backend.list_examples()[nxt].copy()
        goto("results")


PAGES = {"landing": landing, "intent": intent, "questionnaire": questionnaire,
         "paywall": paywall, "results": results}
PAGES[st.session_state.page]()
