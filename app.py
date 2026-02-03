import streamlit as st
import feedparser
import pandas as pd
import re
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

articles = fetch_articles()

# ---------------------------------------------------------
# LIGHTWEIGHT INVESTMENT EXTRACTION (NO SPACY)
# ---------------------------------------------------------

def extract_company(text):
    """
    Heuristic: company/AI entity is usually the first capitalized phrase
    before 'raises', 'lands', 'secures', etc.
    """
    match = re.search(r"([A-Z][A-Za-z0-9&\-\s]+?) (raises|lands|secures|scores|gets)", text)
    if match:
        return match.group(1).strip()
    return ""

def extract_investors(text):
    """
    Heuristic: capture investors after 'led by', 'from', 'backed by'
    """
    patterns = [
        r"led by ([A-Z][A-Za-z0-9&\s,]+)",
        r"from ([A-Z][A-Za-z0-9&\s,]+)",
        r"backed by ([A-Z][A-Za-z0-9&\s,]+)"
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1).strip()
    return ""

def extract_investment_info(article):
    text = article["title"] + " " + article["summary"]

    # Funding amounts
    amounts = re.findall(r"\$[0-9,.]+[MB]?", text)

    # Round types
    rounds = re.findall(r"(Series [A-Z]|Seed round|funding round)", text, re.IGNORECASE)

    # Company / AI entity
    company = extract_company(text)

    # Investors
    investors = extract_investors(text)

    return {
        "title": article["title"],
        "link": article["link"],
        "published": article["published"],
        "company_ai": company,
        "amounts": amounts,
        "rounds": rounds,
        "investors": investors,
    }

structured = [extract_investment_info(a) for a in articles]

# ---------------------------------------------------------
# BUILD STRUCTURED TABLE
# ---------------------------------------------------------
df = pd.DataFrame(structured)

df["Company / AI"] = df["company_ai"]
df["Funding"] = df["amounts"].apply(lambda x: ", ".join(x) if x else "")
df["Round"] = df["rounds"].apply(lambda x: ", ".join(x) if x else "")
df["Investors"] = df["investors"]
df["Article"] = df["title"]
df["Link"] = df["link"]

display_cols = ["Company / AI", "Funding", "Round", "Investors", "Article", "Link"]
df_display = df[display_cols]

# ---------------------------------------------------------
# MAIN SECTION — AI INVESTMENT DATABASE
# ---------------------------------------------------------
st.markdown('<span class="section-title">AI Investment Database</span>', unsafe_allow_html=True)
st.write(
    "This table is generated by an AI factory that ingests TechCrunch’s AI feed "
    "and uses lightweight extraction rules to identify companies, funding amounts, "
    "rounds, and investors — without heavy NLP models."
)

st.dataframe(df_display, use_container_width=True)

# ---------------------------------------------------------
# SNAPSHOT METRICS
# ---------------------------------------------------------
st.markdown('<span class="section-title">Quick Snapshot</span>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Unique Companies / AI Entities", df["Company / AI"].replace("", pd.NA).nunique())
with col2:
    st.metric("Articles Parsed", len(df))
with col3:
    st.metric("Entries With Funding Info", (df["Funding"] != "").sum())
