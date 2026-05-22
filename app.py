"""
app.py — Find Your Cluster (UI only).

All logic comes from backend.py. This file renders the Capital One-inspired,
multi-screen flow: Landing -> Intent -> Questionnaire -> Paywall -> Results.
Run from the repo root:  streamlit run app.py
"""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import backend

st.set_page_config(page_title="Find Your Cluster", page_icon="🔵", layout="centered")

# ---------------------------------------------------------------------------
# Styling — Capital One-inspired (navy + red), Archivo type, clean & calm
# ---------------------------------------------------------------------------
NAVY, RED, INK, MUTED, SURFACE = "#004977", "#D03027", "#11151C", "#6B7280", "#F7F8FA"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stMarkdown, .stButton button {{ font-family:'Archivo',sans-serif; }}
#MainMenu, header, footer {{ visibility:hidden; }}
.block-container {{ max-width:760px; padding-top:2.5rem; }}
h1, h2, h3 {{ color:{NAVY}; font-weight:800; letter-spacing:-0.02em; }}
.hero-title {{ font-size:3.1rem; line-height:1.05; color:{NAVY}; font-weight:800; letter-spacing:-0.03em; margin:0; }}
.hero-sub {{ font-size:1.15rem; color:{MUTED}; margin:1rem 0 2rem; line-height:1.5; }}
.eyebrow {{ color:{RED}; font-weight:700; letter-spacing:.12em; text-transform:uppercase; font-size:.8rem; }}
.stButton>button {{ border-radius:999px; font-weight:600; padding:.55rem 1.4rem; border:1.5px solid {NAVY}; color:{NAVY}; background:#fff; }}
.stButton>button:hover {{ border-color:{NAVY}; color:#fff; background:{NAVY}; }}
.stButton>button[kind="primary"] {{ background:{RED}; border-color:{RED}; color:#fff; }}
.stButton>button[kind="primary"]:hover {{ background:#b1271f; border-color:#b1271f; }}
.card {{ background:{SURFACE}; border-radius:12px; padding:1.4rem 1.6rem; margin:.6rem 0;
        box-shadow:0 1px 3px rgba(17,21,28,.08); }}
.caveat {{ background:{SURFACE}; border-left:4px solid {RED}; border-radius:8px;
          padding:1rem 1.2rem; color:{INK}; font-size:.92rem; line-height:1.5; margin-top:1rem; }}
.price {{ font-size:2.2rem; color:{NAVY}; font-weight:800; }}
.result-name {{ font-size:2.4rem; color:{NAVY}; font-weight:800; letter-spacing:-0.02em; }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# State + content
# ---------------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "answers" not in st.session_state:
    st.session_state.answers = backend.defaults()
if "intent" not in st.session_state:
    st.session_state.intent = "explore"

FRIENDLY = backend.friendly_labels()
CAT_OPTS = backend.category_options()
BINARY = set(backend.load_bundle()["binary_cols"])
CATEG = set(backend.load_bundle()["categorical_cols"])
NAMES = {cid: backend.get_cluster_info(cid)["name"] for cid in range(4)}

RANGES = {"A2": (18.0, 90.0), "A3": (0.0, 30.0), "A7": (0.0, 30.0),
          "A10": (0.0, 70.0), "A13": (0.0, 2000.0), "A14": (0.0, 100001.0)}

GROUPS = [("About you", ["A2", "A1", "A4", "A12"]),
          ("Work & stability", ["A8", "A3", "A6", "A7", "A11"]),
          ("Finances", ["A14", "A10", "A5", "A13", "A9"])]

CLUSTER_DESC = {
    0: "younger applicants early in their financial journey, with limited recorded history.",
    1: "applicants with an active, established financial record.",
    2: "applicants with relatively little recorded activity on file.",
    3: "older applicants with a long, deep financial history.",
}
INTENT_INTRO = {
    "understand": "Here's a clear look at your profile.",
    "similar": "Here are the people most similar to you.",
    "explore": "Here's what we found.",
}
CLUSTER_PALETTE = {0: "#9CC3D5", 1: "#4A90A4", 2: "#C9CDD2", 3: "#1F5C73"}


def goto(page):
    st.session_state.page = page
    st.rerun()


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------
def landing():
    st.markdown('<p class="eyebrow">Find Your Cluster</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">See where you fit.</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">A clear, judgment-free look at which group of '
                'applicants you\'re most like — built for <b>you</b>, not for a bank.</p>',
                unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    if c1.button("Get started", type="primary", use_container_width=True):
        goto("intent")
    if c2.button("Try an example", use_container_width=True):
        ex = backend.list_examples()
        st.session_state.answers = ex[3].copy()  # the "Seasoned profile" example
        st.session_state.intent = "explore"
        goto("results")


def intent():
    st.markdown('<p class="eyebrow">Step 1 of 3</p>', unsafe_allow_html=True)
    st.title("What brings you here?")
    st.write("")
    choices = [("understand", "Understand my profile"),
               ("similar", "See who's similar to me"),
               ("explore", "I'm just exploring")]
    for key, label in choices:
        if st.button(label, use_container_width=True):
            st.session_state.intent = key
            goto("questionnaire")
    st.write("")
    if st.button("← Back"):
        goto("landing")


def render_input(code):
    label = FRIENDLY[code].split(" (")[0].replace("_", " ")
    note = FRIENDLY[code][FRIENDLY[code].find("(") + 1:-1] if "(" in FRIENDLY[code] else ""
    cur = st.session_state.answers[code]
    if code in BINARY:
        val = st.selectbox(label, [0, 1], index=[0, 1].index(int(cur)),
                           help="Coded 0/1; exact meaning of each value is not disclosed in the data.")
    elif code in CATEG:
        opts = CAT_OPTS[code]
        idx = opts.index(int(cur)) if int(cur) in opts else 0
        val = st.selectbox(label, opts, index=idx)
    else:
        lo, hi = RANGES[code]
        val = st.number_input(label, lo, hi, float(min(max(cur, lo), hi)))
    if note:
        st.caption("⚠️ " + note)
    st.session_state.answers[code] = val


def questionnaire():
    st.markdown('<p class="eyebrow">Step 2 of 3</p>', unsafe_allow_html=True)
    st.title("Tell us about yourself")
    st.progress(0.66)
    st.caption("Every field is optional — defaults are typical values. "
               "Some labels are our best guess from anonymized data and are marked.")
    for title, codes in GROUPS:
        st.subheader(title)
        cols = st.columns(2)
        for i, code in enumerate(codes):
            with cols[i % 2]:
                render_input(code)
    st.write("")
    c1, c2 = st.columns([1, 1])
    if c1.button("← Back"):
        goto("intent")
    if c2.button("See my results →", type="primary", use_container_width=True):
        goto("paywall")


def paywall():
    st.markdown('<p class="eyebrow">Almost there</p>', unsafe_allow_html=True)
    st.title("Your profile is ready")
    st.markdown('<div class="card">'
                '<p class="price">$4.99</p>'
                '<b>Unlock your full breakdown</b>'
                '<ul><li>Your cluster and a typical-member comparison</li>'
                '<li>Your position on the applicant map</li>'
                '<li>How central or borderline you are</li></ul>'
                '</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
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
    st.markdown(f'<p class="result-name">You\'re most like<br>“{info["name"]}”</p>', unsafe_allow_html=True)
    st.write(f"This group is **{CLUSTER_DESC[cid]}**")

    # You vs typical
    st.subheader("People like you, typically")
    prof = info["profile"]
    comp = pd.DataFrame(
        {"You": [raw["A2"], raw["A14"], raw["A10"]],
         "Typical in your group": [prof["A2"], prof["A14"], prof["A10"]]},
        index=["Age", "Annual income", "Debt (thousands)"])
    st.table(comp)

    # You are here map
    st.subheader("You are here")
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

    # How typical
    st.subheader("How typical are you")
    st.write(f"Within this group, you're **{typ['label']}**.")
    if typ["label"] == "on the edge":
        st.write(f"You also sit close to the **{typ['nearest_other_name']}** group — "
                 "you're a bit of a blend between the two. That's just where you land, "
                 "not something you need to change.")

    # Historical context
    st.subheader("Historical context")
    st.markdown(f'<div class="caveat">In the source data, applicants most like you were '
                f'approved about <b>{info["approval_rate"]:.0%}</b> of the time. This reflects '
                f'past human lending decisions, which may carry historical bias. It is '
                f'<b>not</b> a prediction or a score for you — it\'s context to help you '
                f'understand where you sit.</div>', unsafe_allow_html=True)

    st.write("")
    c1, c2 = st.columns([1, 1])
    if c1.button("Start over"):
        st.session_state.answers = backend.defaults()
        goto("landing")
    if c2.button("Try an example"):
        st.session_state.answers = backend.list_examples()[0].copy()
        goto("results")


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
PAGES = {"landing": landing, "intent": intent, "questionnaire": questionnaire,
         "paywall": paywall, "results": results}
PAGES[st.session_state.page]()
