"""
UniPathAi — Office of Global Admissions
=======================================
Hackathon MVP · Streamlit UI (Amaar)
"""

import html as html_mod

import pandas as pd
import streamlit as st

from modules.recommender import recommend_universities
from modules.ai_engine import generate_explanation, chat_with_advisor

st.set_page_config(page_title="UniPathAi — Global Admissions",
                    page_icon="🎓", layout="wide",
                    initial_sidebar_state="expanded")

DATA_PATH = "data/universities.csv"
FIELDS = ["Computer Science", "Data Science", "Engineering", "Business", "Medicine"]
LEVELS = ["Bachelor", "Master", "PhD"]
DEFAULT_PROFILE = {"name": "", "level": "Master", "field": "Computer Science",
                    "cgpa": 3.2, "budget_usd": 20000, "preferred_countries": [],
                    "needs_scholarship": False, "ielts": 6.5}

ORDINALS = {1: "1st", 2: "2nd", 3: "3rd"}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,500&family=Inter:wght@400;500;600&display=swap');
html, body, [data-testid="stAppViewContainer"] { background: #F6F1E1; }
[data-testid="stAppViewContainer"] { color: #2A2A24; }
h1, h2, h3, h4 { font-family: 'Fraunces', Georgia, serif !important; color: #20261F; font-weight: 500; }
p, li, label, span, div { font-family: 'Inter', 'Segoe UI', sans-serif; }
#MainMenu, footer, [data-testid="stHeader"] { visibility: hidden; }
[data-testid="stSidebar"] { background: #1B3A2E; border-right: 1px solid #A9812E33; }
[data-testid="stSidebar"] * { color: #EDE6D2 !important; }
[data-testid="stSidebar"] .stRadio label { font-size: .98rem; padding: .3rem 0; font-family: 'Inter', sans-serif; }
.seal-wrap { text-align: center; padding: 1.6rem 0 1rem 0; }
.seal {
  width: 68px; height: 68px; margin: 0 auto; border-radius: 50%;
  background: radial-gradient(circle at 32% 28%, #C79A3E, #8C6A25 72%);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 0 rgba(0,0,0,.25) inset, 0 2px 6px rgba(0,0,0,.35);
  font-family: 'Fraunces', serif; font-style: italic; font-weight: 600;
  font-size: 1.7rem; color: #1B3A2E;
}
.letterhead-name { font-family: 'Fraunces', serif; font-size: 1.28rem; font-weight: 500;
  margin-top: .8rem; color: #F6F1E1; }
.letterhead-sub { font-size: .78rem; color: #B7CBBE; margin-top: .1rem; }
.side-rule { border: none; border-top: 1px solid #A9812E4D; margin: 1rem 1.2rem; }
.side-note { font-size: .78rem; color: #AFA98F !important; line-height: 1.75; padding: 0 1.2rem; }
.hero { background: #1B3A2E; border-radius: 2px; padding: 3rem 3.2rem;
  margin-bottom: 2.2rem; position: relative; overflow: hidden;
  animation: hero-in .5s ease-out; }
@keyframes hero-in { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
.hero::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 3px;
  background: linear-gradient(90deg, transparent, #A9812E, transparent); }
.hero-kicker { font-family: 'Fraunces', serif; font-style: italic; font-size: 1.02rem;
  color: #C79A3E; margin-bottom: .5rem; }
.hero-title { font-family: 'Fraunces', serif !important; color: #F6F1E1 !important;
  font-size: 2.5rem; line-height: 1.18; font-weight: 500; max-width: 620px; margin-bottom: .9rem; }
.hero-sub { color: #C9D2C6; font-size: 1.02rem; max-width: 560px; line-height: 1.6; }
.hero-facts { margin-top: 1.8rem; display: flex; gap: 0; flex-wrap: wrap; }
.hero-fact { padding: 0 1.6rem; border-left: 1px solid #A9812E4D; }
.hero-fact:first-child { padding-left: 0; border-left: none; }
.hero-fact b { display: block; font-family: 'Fraunces', serif; color: #F6F1E1; font-size: 1.15rem; font-weight: 500; }
.hero-fact span { display: block; color: #9FB3A6; font-size: .8rem; margin-top: .15rem; }
.section-head { display: flex; align-items: baseline; gap: .7rem; margin: .4rem 0 1.1rem 0; }
.section-mark { font-family: 'Fraunces', serif; font-style: italic; color: #A9812E; font-size: 1.15rem; }
.section-title { font-family: 'Fraunces', serif; font-size: 1.55rem; color: #20261F; font-weight: 500; }
.section-rule { border: none; border-top: 1px solid #20261F26; margin: 0 0 1.3rem 0; }
.ledger-entry { display: flex; gap: 1.4rem; padding: 1.3rem 0; border-top: 1px solid #20261F26; }
.ledger-entry:last-of-type { border-bottom: 1px solid #20261F26; }
.folio { font-family: 'Fraunces', serif; font-style: italic; font-size: 1.9rem; color: #A9812E;
  min-width: 3.2rem; line-height: 1; padding-top: .1rem; }
.ledger-body { flex: 1; min-width: 0; }
.uni-name { font-family: 'Fraunces', serif; font-size: 1.32rem; color: #20261F; font-weight: 500; margin-bottom: .12rem; }
.uni-program { color: #1B3A2E; font-weight: 600; font-size: .96rem; }
.uni-meta { color: #665F4E; font-size: .87rem; margin-top: .3rem; line-height: 1.6; }
.uni-tags { margin-top: .6rem; display: flex; gap: .5rem; flex-wrap: wrap; }
.tag { font-size: .76rem; padding: .2rem .6rem; border: 1px solid #A9812E80; color: #7A5E1F;
  background: transparent; border-radius: 2px; }
.tag-fill { background: #1B3A2E; border-color: #1B3A2E; color: #EDE6D2; }
.ledger-figures { min-width: 118px; text-align: right; }
.match-num { font-family: 'Fraunces', serif; font-size: 1.7rem; color: #20261F; font-weight: 500; }
.match-num small { font-size: .95rem; color: #A9812E; font-weight: 400; }
.match-label { font-size: .72rem; color: #948C72; margin-top: -.15rem; }
.fee { font-family: 'Fraunces', serif; font-size: 1.05rem; color: #20261F; margin-top: .5rem; }
.fee small { display: block; font-size: .7rem; color: #948C72; font-family: 'Inter', sans-serif; }
.reason-li { font-size: .88rem; color: #1B3A2E; padding: .15rem 0; }
.stButton > button, .stFormSubmitButton > button {
  background: #1B3A2E !important; color: #EDE6D2 !important; border: 1px solid #1B3A2E !important;
  border-radius: 2px !important; font-weight: 500 !important; font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
  background: #142E24 !important; border-color: #A9812E !important; color: #F6F1E1 !important;
}
[data-testid="stExpander"] { border: 1px solid #20261F26 !important; border-radius: 2px !important;
  background: #FBF8EF; }
.site-footer { text-align: center; color: #948C72; font-size: .82rem;
  border-top: 1px solid #20261F26; margin-top: 3rem; padding: 1.5rem 0 2.4rem 0;
  font-family: 'Fraunces', serif; font-style: italic; }

/* ---------- chat / AI counsellor readability fix ---------- */
[data-testid="stChatMessage"] { background: #FBF8EF; border: 1px solid #20261F1A;
  border-radius: 4px; }
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span, [data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] table, [data-testid="stChatMessage"] td,
[data-testid="stChatMessage"] th, [data-testid="stChatMessageContent"] * {
  color: #20261F !important; opacity: 1 !important; }
[data-testid="stChatInput"] textarea { color: #20261F !important; }

/* ---------- form widget label readability fix ---------- */
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label,
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stSlider label, .stMultiSelect label, .stCheckbox label,
.stSelectSlider label, .stTextInput p, .stNumberInput p,
.stSelectbox p, .stSlider p, .stMultiSelect p, .stCheckbox p,
.stSelectSlider p {
  color: #20261F !important; opacity: 1 !important; font-weight: 500;
}
/* slider min/max endpoint numbers + current value bubble */
[data-testid="stSlider"] div, [data-testid="stSlider"] span,
[data-testid="stTickBar"] * { color: #20261F !important; }
/* multiselect / selectbox placeholder + selected chip text */
[data-baseweb="select"] * { color: #20261F !important; }
[data-baseweb="select"] input::placeholder { color: #66605080 !important; }

/* ---------- mobile responsiveness ---------- */
@media (max-width: 640px) {
  .hero { padding: 1.6rem 1.4rem; }
  .hero-title { font-size: 1.7rem; max-width: 100%; }
  .hero-sub { font-size: .92rem; max-width: 100%; }
  .hero-facts { gap: .4rem; }
  .hero-fact { padding: 0 .9rem; }
  .ledger-entry { flex-direction: column; gap: .6rem; }
  .ledger-figures { text-align: left; min-width: 0; }
  .section-title { font-size: 1.25rem; }
  [data-testid="column"] { min-width: 100% !important; flex: 1 1 100% !important; }
}
</style>
"""

LETTERHEAD = """
<div class="seal-wrap">
  <div class="seal">U</div>
  <div class="letterhead-name">UniPathAi</div>
  <div class="letterhead-sub">Office of Global Admissions</div>
</div>
<hr class="side-rule">
"""

FOOTER = """
<div class="site-footer">
  Guiding students to the university where they belong, since 2026.
</div>
"""


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def get_profile() -> dict:
    if "profile" not in st.session_state:
        st.session_state.profile = DEFAULT_PROFILE.copy()
    return st.session_state.profile


def esc(s) -> str:
    return html_mod.escape(str(s))


def hero(kicker: str, title: str, sub: str, facts: list) -> None:
    facts_html = "".join(
        f'<div class="hero-fact"><b>{esc(b)}</b><span>{esc(l)}</span></div>'
        for b, l in facts)
    st.markdown(f"""
    <div class="hero">
      <div class="hero-kicker">{esc(kicker)}</div>
      <div class="hero-title">{esc(title)}</div>
      <div class="hero-sub">{esc(sub)}</div>
      <div class="hero-facts">{facts_html}</div>
    </div>""", unsafe_allow_html=True)


def section_head(mark: str, title: str) -> None:
    st.markdown(f"""
    <div class="section-head">
      <span class="section-mark">{esc(mark)}</span>
      <span class="section-title">{esc(title)}</span>
    </div>
    <hr class="section-rule">""", unsafe_allow_html=True)


def uni_card(rank: int, row: pd.Series) -> None:
    folio = ORDINALS.get(rank, f"{rank}th")

    tags = [
        f'<span class="tag tag-fill">Due {esc(row["application_deadline"])}</span>',
        f'<span class="tag">IELTS {esc(row["ielts_min"])}+</span>',
    ]
    if row["scholarship_available"] == "Yes":
        tags.append('<span class="tag">Aid available</span>')
    tags_html = "".join(tags)

    tuition_fmt = f"{int(row['tuition_usd_yearly']):,}"

    st.markdown(f"""
    <div class="ledger-entry">
      <div class="folio">{folio}</div>
      <div class="ledger-body">
        <div class="uni-name">{esc(row['university'])}</div>
        <div class="uni-program">{esc(row['program'])}, {esc(row['level'])}</div>
        <div class="uni-meta">{esc(row['city'])}, {esc(row['country'])} &nbsp;—&nbsp; QS rank {esc(row['qs_rank'])}</div>
        <div class="uni-tags">{tags_html}</div>
      </div>
      <div class="ledger-figures">
        <div class="match-num">{esc(row['match_score'])}<small>% match</small></div>
        <div class="fee">${esc(tuition_fmt)}<small>per year</small></div>
      </div>
    </div>""", unsafe_allow_html=True)

    with st.expander("Admission details & eligibility"):
        d1, d2 = st.columns(2)
        with d1:
            st.markdown(f"**Application deadline:** {row['application_deadline']}")
            st.markdown(f"**Minimum CGPA:** {row['min_cgpa']}/4.0  ·  **IELTS:** {row['ielts_min']}")
            st.markdown(f"**Accommodation on campus:** {row['accommodation_available']}")
            st.markdown(f"**Part-time work allowed:** {row['part_time_work']}")
            if row["scholarship_available"] == "Yes":
                st.markdown(f"**Scholarship:** {row['scholarship_details']}")
        with d2:
            st.markdown("**Why this is a match**")
            for reason in row["match_reasons"]:
                st.markdown(f'<div class="reason-li">— {esc(reason)}</div>',
                            unsafe_allow_html=True)

    if st.button("Ask the AI counsellor about this one", key=f"ai_{rank}_{row['university']}",
                  use_container_width=False):
        with st.spinner("Consulting the AI counsellor..."):
            st.info(generate_explanation(get_profile(), row.to_dict()))


def page_profile(df: pd.DataFrame) -> None:
    hero("Admissions open for the 2027 intake",
         "Find the university where you belong",
         "Complete your applicant profile below and our admissions engine will "
         "match you with universities that fit your record, budget and ambitions.",
         [("500+", "partner universities"), ("40+", "countries"),
          ("$4M+", "scholarships mapped")])

    section_head("§1", "Tell us about yourself")
    profile = get_profile()

    with st.form("student_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            profile["name"] = st.text_input("Full name", value=profile["name"],
                                             placeholder="e.g. Amaar Khan")
            profile["level"] = st.selectbox("Degree level you wish to pursue",
                                             LEVELS, index=LEVELS.index(profile["level"]))
            profile["field"] = st.selectbox("Intended field of study", FIELDS,
                                             index=FIELDS.index(profile["field"]))
            profile["cgpa"] = st.slider("Academic standing — CGPA (4.0 scale)", 0.0, 4.0,
                                         float(profile["cgpa"]), 0.05)
        with col2:
            profile["budget_usd"] = st.number_input(
                "Annual tuition budget (USD)", min_value=0, max_value=200000,
                value=int(profile["budget_usd"]), step=1000)
            all_countries = sorted(df["country"].unique().tolist())
            profile["preferred_countries"] = st.multiselect(
                "Preferred countries (optional)", all_countries,
                default=profile["preferred_countries"])
            profile["needs_scholarship"] = st.checkbox(
                "I require financial aid / scholarship", value=profile["needs_scholarship"])
            profile["ielts"] = st.select_slider(
                "English proficiency — IELTS", options=[5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0],
                value=float(profile["ielts"]))

        submitted = st.form_submit_button("Submit application profile",
                                           use_container_width=True)
        if submitted:
            st.session_state.profile = profile
            st.success("Profile submitted. View your matches under **Matches & offers**.")
            st.balloons()


def page_recommendations(df: pd.DataFrame) -> None:
    profile = get_profile()
    hero("Match results",
         f"Offers curated for {profile.get('name') or 'you'}",
         "Ranked by fit against your academic record, finances and preferences. "
         "Every match is verified against official admission requirements.",
         [(len(df), "universities reviewed"),
          (f"${profile['budget_usd']:,}" if profile.get("budget_usd") else "—", "your yearly budget"),
          (profile.get("cgpa", "—"), "your CGPA")])

    if not profile.get("name"):
        st.info("Please submit your **applicant profile** first.")
        return

    recs = recommend_universities(profile, df)
    if recs.empty:
        st.warning("No eligible universities found for this profile. "
                   "Try widening your budget or preferences.")
        return

    section_head("§2", "Refine your results")
    fcol1, fcol2, fcol3, fcol4 = st.columns(4)
    countries = sorted(recs["country"].unique())
    with fcol1:
        f_country = st.multiselect("Country", countries, default=countries)
    with fcol2:
        f_maxfee = st.number_input("Max tuition (USD/yr)", 0, 200000,
                                    int(recs["tuition_usd_yearly"].max()) + 5000, step=1000)
    with fcol3:
        f_scholarship = st.selectbox("Financial aid", ["Any", "Scholarship available only"])
    with fcol4:
        f_minscore = st.slider("Minimum match score", 0, 100, 0, 5)

    view = recs[recs["country"].isin(f_country)
                & (recs["tuition_usd_yearly"] <= f_maxfee)
                & (recs["match_score"] >= f_minscore)]
    if f_scholarship == "Scholarship available only":
        view = view[view["scholarship_available"] == "Yes"]

    st.markdown("")
    section_head("§3", f"Your shortlist — {len(view)} universities")

    if view.empty:
        st.warning("No matches under these filters — try relaxing them.")
        return
    for rank, (_, row) in enumerate(view.iterrows(), start=1):
        uni_card(rank, row)


def page_browse(df: pd.DataFrame) -> None:
    hero("Course catalogue",
         "Browse our partner universities",
         "Explore the complete catalogue of partner institutions, programmes, "
         "tuition and deadlines before building your profile.",
         [(len(df), "institutions"), (df["country"].nunique(), "countries"),
          (df["program"].nunique(), "programmes")])
    c1, c2, c3 = st.columns(3)
    with c1:
        b_country = st.multiselect("Country", sorted(df["country"].unique()),
                                    default=sorted(df["country"].unique()))
    with c2:
        b_level = st.multiselect("Degree level", LEVELS, default=LEVELS)
    with c3:
        b_field = st.multiselect("Field of study", FIELDS, default=FIELDS)
    view = df[df["country"].isin(b_country) & df["level"].isin(b_level) & df["field"].isin(b_field)]
    st.dataframe(view, use_container_width=True, hide_index=True)


def page_advisor() -> None:
    hero("Student counselling",
         "Ask our AI counsellor",
         "Questions about admissions, scholarships, deadlines or visa rules? "
         "Our counsellor is available around the clock.",
         [("24/7", "availability"), ("40+", "countries covered"), ("2 min", "avg. response")])
    profile = get_profile()
    if not profile.get("name"):
        st.info("Submit your **applicant profile** first for personalised guidance.")
        return
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for role, msg in st.session_state.chat_history:
        st.chat_message(role).write(msg)
    if q := st.chat_input("e.g. Can I get a full scholarship in Germany with CGPA 3.1?"):
        st.session_state.chat_history.append(("user", q))
        st.chat_message("user").write(q)
        with st.spinner("The counsellor is thinking..."):
            answer = chat_with_advisor(profile, q)
        st.session_state.chat_history.append(("assistant", answer))
        st.chat_message("assistant").write(answer)


def main() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    df = load_data()

    with st.sidebar:
        st.markdown(LETTERHEAD, unsafe_allow_html=True)
        page = st.radio("Portal", [
            "Applicant profile",
            "Matches & offers",
            "Course catalogue",
            "AI counsellor",
        ])
        st.markdown("""
        <hr class="side-rule">
        <div class="side-note">
        Office hours<br>Mon–Sat, 9:00–18:00<br><br>
        admissions@unimatch.edu<br>+1 (555) 010-2027
        </div>""", unsafe_allow_html=True)

    if page == "Applicant profile":
        page_profile(df)
    elif page == "Matches & offers":
        page_recommendations(df)
    elif page == "Course catalogue":
        page_browse(df)
    else:
        page_advisor()

    st.markdown(FOOTER, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
