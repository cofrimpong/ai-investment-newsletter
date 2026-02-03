import streamlit as st
import feedparser
import pandas as pd
import re
import spacy
from datetime import datetime

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Investment Daily",
    layout="wide"
)

# ---------------------------------------------------------
# BRUTALIST CSS
# ---------------------------------------------------------
st.markdown("""
<style>

    body, .stApp {
        background: #FFFFFF !important;
        color: #000000 !important;
        font-family: 'Inter', sans-serif;
    }

    /* MAXIMALIST SPLIT MASTHEAD */
    .masthead {
        display: grid;
        grid-template-columns: 1fr 300px;
        border: 6px solid #000000;
        margin-bottom: 30px;
    }

    .masthead-left {
        background: #000000;
        color: #FFFFFF;
        padding: 25px;
        font-size: 3.4rem;
        font-weight: 900;
        text-transform: uppercase;
        line-height: 1;
        border-right: 6px solid #000000;
    }

    .masthead-right {
        background: #FFDE00;
        color: #000000;
        padding: 25px;
        font-size: 1.4rem;
        font-weight: 800;
        text-transform: uppercase;
        line-height: 1.2;
    }

    .section-title {
        font-size: 1.6rem;
        font-weight: 900;
        text-transform: uppercase;
        margin: 20px 0 10px 0;
        border-bottom: 4px solid #000000;
        display: inline-block;
    }

    /* BRUTALIST TABLE */
    .dataframe {
        border: 5px solid #000000 !important;
    }

    .dataframe th {
        background: #FFDE00 !important;
        border: 3px solid #000000 !important;
        font-weight: 900 !important;
        text-transform: uppercase;
    }

    .dataframe td {
        border: 3px solid #000000 !important;
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MASTHEAD
# ---------------------------------------------------------
st.markdown("""
<div class="masthead">
    <div class="masthead-left">
        AI Investment Daily
    </div>
    <div class="masthead-right">
        Issue 004<br>February 2026
    </div>
</div>
""", unsafe_allow_html=True)

st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y — %I:%M %p EST')}")

# ---------------------------------------------------------
# LOAD SPACY MODEL
# ---------------------------------------------------------
@st.cache_resource
def load_nlp():
    return spacy.load("en_core_web_sm")

nlp = load_nlp()

# ---------------------------------------------------------
# FETCH TECHCRUNCH AI FEED
# ---------------------------------------------------------
@st.cache_data
def fetch_articles():
    url = "https://techcrunch.com/tag/artificial-intelligence/feed/"
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:30]:
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "summary": entry.summary
        })
    return articles

with st.spinner("Collecting latest AI investment articles..."):
    articles = fetch_articles()

# ---------------------------------------------------------
# EXTRACT INVESTMENT + ENTITY INFO
# ---------------------------------------------------------
def extract_investment_info(article):
    text = article["title"] + " " + article["summary"]

    # Funding amounts
    amounts = re.findall(r"\$[0-9,.]+[MB]?", text)

    # Round types
    rounds = re.findall(r"(Series [A-Z]|Seed round|funding round)", text, re.IGNORECASE)

    # Investors (simple pattern)
    investors = re.findall(r"([A-Z][a-zA-Z0-9& ]+)(?= (invested|led))", text)

    # spaCy NER for companies / AI entities
    doc = nlp(text)
    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

    # Heuristic: first ORG as "company/AI entity"
    company_ai = orgs[0] if orgs else ""

    return {
        "title": article["title"],
        "link": article["link"],
        "published": article["published"],
        "company_ai": company_ai,
        "amounts": amounts,
        "rounds": rounds,
        "investors": [i[0].strip() for i in investors],
    }

structured = [extract_investment_info(a) for a in articles]

# ---------------------------------------------------------
# BUILD STRUCTURED TABLE
# ---------------------------------------------------------
df = pd.DataFrame(structured)

df["Company / AI"] = df["company_ai"]
df["Funding"] = df["amounts"].apply(lambda x: ", ".join(x) if x else "")
df["Round"] = df["rounds"].apply(lambda x: ", ".join(x) if x else "")
df["Investors"] = df["investors"].apply(lambda x: ", ".join(x) if x else "")
df["Article"] = df["title"]
df["Link"] = df["link"]

display_cols = ["Company / AI", "Funding", "Round", "Investors", "Article", "Link"]
df_display = df[display_cols]

# ---------------------------------------------------------
# MAIN SECTION — AI INVESTMENT DATABASE
# ---------------------------------------------------------
st.markdown('<span class="section-title">AI Investment Database</span>', unsafe_allow_html=True)
st.write(
    "This table is generated by an AI factory that ingests TechCrunch’s AI feed, "
    "uses spaCy to detect organizations, and extracts structured information about "
    "who is investing in what AI companies or platforms."
)

st.dataframe(df_display, use_container_width=True)

# ---------------------------------------------------------
# OPTIONAL: SIMPLE SUMMARY COUNTS
# ---------------------------------------------------------
st.markdown('<span class="section-title">Quick Snapshot</span>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Unique Companies / AI Entities", df["Company / AI"].replace("", pd.NA).nunique())
with col2:
    st.metric("Articles Parsed", len(df))
with col3:
    st.metric("Entries With Funding Info", (df["Funding"] != "").sum())
