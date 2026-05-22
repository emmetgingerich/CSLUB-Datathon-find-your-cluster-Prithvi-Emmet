"""
app.py — Find Your Cluster (UI only).

All logic comes from backend.py. Flow:
  Landing -> Intent -> Questionnaire (one question at a time) -> Paywall -> Results
Run from the repo root:  streamlit run app.py
"""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import backend

st.set_page_config(page_title="Find Your Cluster", page_icon="🔵", layout="centered")

NAVY, RED, INK, MUTED, SURFACE = "#004977", "#D03027", "#11151C", "#6B7280", "#F7F8FA"

# ---------------------------------------------------------------------------
# Styling — Capital One-inspired (navy + red), Archivo type, sectioned cards
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stMarkdown, .stButton button {{ font-family:'Archivo',sans-serif; }}
#MainMenu, header, footer {{ visibility:hidden; }}
.block-container {{ max-width:760px; padding-top:2.4rem; }}

@keyframes fadeUp {{ from {{ opacity:0; transform:translateY(14px); }} to {{ opacity:1; transform:translateY(0); }} }}

h1,h2,h3 {{ color:{NAVY}; font-weight:800; letter-spacing:-0.02em; }}
.hero-title {{ font-size:3.1rem; line-height:1.05; color:{NAVY}; font-weight:800; letter-spacing:-0.03em; margin:0; }}
.hero-sub {{ font-size:1.15rem; color:{MUTED}; margin:1rem 0 1.6rem; line-height:1.5; }}
.eyebrow {{ color:{RED}; font-weight:700; letter-spacing:.12em; text-transform:uppercase; font-size:.78rem; margin-bottom:.3rem; }}

/* every bordered container becomes a clean section card */
[data-testid="stVerticalBlockBorderWrapper"] {{
  border:1px solid #E3E8EE; border-radius:14px; background:#fff;
  box-shadow:0 1px 3px rgba(17,21,28,.06); padding:.4rem .2rem;
}}
.sec-title {{ font-size:1.2rem; font-weight:800; color:{NAVY};
  border-left:4px solid {RED}; padding-left:.6rem; margin:.1rem 0 1rem; }}
.q-title {{ font-size:1.7rem; font-weight:800; color:{NAVY}; margin:.2rem 0 .9rem; letter-spacing:-0.02em; }}
.result-name {{ font-size:2.3rem; color:{NAVY}; font-weight:800; line-height:1.1; letter-spacing:-0.02em; }}
.price {{ font-size:2.2rem; color:{NAVY}; font-weight:800; }}

/* light-blue progress dots */
.dots {{ display:flex; gap:7px; margin:.3rem 0 1.3rem; flex-wrap:wrap; }}
.dot {{ width:11px; height:11px; border-radius:50%; background:#CFE3EE; transition:background .35s ease; }}
.dot.on {{ background:#2E8BC0; }}

/* buttons */
.stButton>button {{ border-radius:999px; font-weight:600; padding:.55rem 1.4rem;
  border:1.5px solid {NAVY}; color:{NAVY}; background:#fff; }}
.stButton>button:hover {{ color:#fff; background:{NAVY}; }}
.stButton>button[kind="primary"] {{ background:{RED}; border-color:{RED}; color:#fff; }}
.stButton>button[kind="primary"]:hover {{ background:#b1271f; border-color:#b1271f; }}

.caveat {{ background:{SURFACE}; border-left:4px solid {RED}; border-radius:8px;
  padding:1rem 1.2rem; color:{INK}; font-size:.92rem; line-height:1.5; margin-top:.6rem; }}
.card {{ background:{SURFACE}; border-radius:12px; padding:1.3rem 1.5rem; margin:.5rem 0; }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# State + content
# ---------------------------------------------------------------------------
st.session_state.setdefault("page", "landing")
st.session_state.setdefault("answers", backend.defaults())
st.session_state.setdefault("intent", "explore")
st.session_state.setdefault("qidx", 0)

FRIENDLY = backend.friendly_labels()
CAT_OPTS = backend.category_options()
BINARY = set(backend.load_bundle()["binary_cols"])
CATEG = set(backend.load_bundle()["categorical_cols"])
NAMES = {cid: backend.get_cluster_info(cid)["name"] for cid in range(4)}

RANGES = {"A2": (18.0, 90.0), "A3": (0.0, 30.0), "A7": (0.0, 30.0),
          "A10": (0.0, 70.0), "A13": (0.0, 2000.0), "A14": (0.0, 100001.0)}

# flatten the three sections into one ordered list of 14 questions
QUESTION_ORDER = []
for _section, _codes in [("About you", ["A2", "A1", "A4", "A12"]),
                         ("Work & stability", ["A8", "A3", "A6", "A7", "A11"]),
                         ("Finances", ["A14", "A10", "A5", "A13", "A9"])]:
    for _c in _codes:
        QUESTION_ORDER.append((_c, _section))

CLUSTER_DESC = {
    0: "younger applicants early in their financial journey, with limited recorded history.",
    1: "applicants with an active, established financial record.",
    2: "applicants with relatively little recorded activity on file.",
    3: "older applicants with a long, deep financial history.",
}
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


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------
def landing():
    with st.container(border=True):
        st.markdown('<p class="eyebrow">Find Your Cluster</p>', unsafe_allow_html=True)
        st.markdown('<p class="hero-title">See where you fit.</p>', unsafe_allow_html=True)
        st.markdown('<p class="hero-sub">A clear, judgment-free look at which group of '
                    'applicants you\'re most like — built for <b>you</b>, not for a bank.</p>',
                    unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("Get started", type="primary", use_container_width=True):
            st.session_state.qidx = 0
            goto("intent")
        if c2.button("Try an example", use_container_width=True):
            st.session_state.answers = backend.list_examples()[3].copy()
            st.session_state.intent = "explore"
            goto("results")


def intent():
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
        val = st.selectbox(label, [0, 1], index=[0, 1].index(int(cur)),
                           label_visibility="collapsed",
                           help="Coded 0/1; the exact meaning of each value isn't disclosed in the data.")
    elif code in CATEG:
        opts = CAT_OPTS[code]
        idx = opts.index(int(cur)) if int(cur) in opts else 0
        val = st.selectbox(label, opts, index=idx, label_visibility="collapsed")
    else:
        lo, hi = RANGES[code]
        val = st.number_input(label, lo, hi, float(min(max(cur, lo), hi)),
                              label_visibility="collapsed")
    st.session_state.answers[code] = val


def questionnaire():
    qidx = st.session_state.qidx
    total = len(QUESTION_ORDER)
    code, section = QUESTION_ORDER[qidx]
    last = qidx == total - 1

    # fade + slide-up on each question (replays every rerun on this page)
    st.markdown("<style>.block-container{animation:fadeUp .35s ease;}</style>", unsafe_allow_html=True)

    st.markdown(f'<p class="eyebrow">{section} · Question {qidx + 1} of {total}</p>',
                unsafe_allow_html=True)
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
    st.markdown('<p class="eyebrow">Almost there</p>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<p class="sec-title">Your profile is ready</p>', unsafe_allow_html=True)
        st.markdown('<div class="card"><p class="price">$4.99</p>'
                    '<b>Unlock your full breakdown</b>'
                    '<ul><li>Your cluster and a typical-member comparison</li>'
                    '<li>Your position on the applicant map</li>'
                    '<li>How central or borderline you are</li></ul></div>',
                    unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("Unlock — $4.99", type="primary", use_container_width=True):
            st.toast("Payment is disabled in this demo — use 'Continue for free'.")
        if c2.button("Continue for free", use_container_width=True):
            goto("results")
    st.markdown('<div class="caveat">Note: this paywall is a <b>demonstration</b> of a common '
                'monetization point, switched off by default. Charging applicants to see information '
                'about themselves raises real fairness concerns, which we address openly rather than hide.'
                '</div>', unsafe_allow_html=True)


def results():
    raw = st.session_state.answers
    cid = backend.assign_cluster(raw)
    info = backend.get_cluster_info(cid)
    typ = backend.typicality(raw)

    st.markdown(f'<p class="eyebrow">{INTENT_INTRO[st.session_state.intent]}</p>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f'<p class="result-name">You\'re most like<br>“{info["name"]}”</p>',
                    unsafe_allow_html=True)
        st.write(f"This group is **{CLUSTER_DESC[cid]}**")

    with st.container(border=True):
        st.markdown('<p class="sec-title">People like you, typically</p>', unsafe_allow_html=True)
        prof = info["profile"]
        st.table(pd.DataFrame(
            {"You": [raw["A2"], raw["A14"], raw["A10"]],
             "Typical in your group": [prof["A2"], prof["A14"], prof["A10"]]},
            index=["Age", "Annual income", "Debt (thousands)"]))

    with st.container(border=True):
        st.markdown('<p class="sec-title">You are here</p>', unsafe_allow_html=True)
        coords, labels = backend.get_training_map()
        ux, uy = backend.map_position(raw)
        fig, ax = plt.subplots(figsize=(6, 5))
        for c in sorted(set(labels)):
            m = labels == c
            ax.scatter(coords[m, 0], coords[m, 1], s=16, alpha=0.55,
                       color=CLUSTER_PALETTE.get(int(c), "#999"), label=NAMES[int(c)])
        ax.scatter([ux], [uy], s=300, marker="*", color=RED,
                   edgecolor="white", linewidth=1.3, zorder=5, label="You")
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
            st.write(f"You also sit close to the **{typ['nearest_other_name']}** group — "
                     "you're a bit of a blend between the two. That's just where you land, "
                     "not something you need to change.")

    with st.container(border=True):
        st.markdown('<p class="sec-title">Historical context</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="caveat">In the source data, applicants most like you were '
                    f'approved about <b>{info["approval_rate"]:.0%}</b> of the time. This reflects '
                    f'past human lending decisions, which may carry historical bias. It is '
                    f'<b>not</b> a prediction or a score for you — it\'s context to help you '
                    f'understand where you sit.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    if c1.button("Start over"):
        st.session_state.answers = backend.defaults()
        st.session_state.qidx = 0
        goto("landing")
    if c2.button("Try an example"):
        st.session_state.answers = backend.list_examples()[0].copy()
        goto("results")


PAGES = {"landing": landing, "intent": intent, "questionnaire": questionnaire,
         "paywall": paywall, "results": results}
PAGES[st.session_state.page]()
