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

    /* TWO-COLUMN NEWSPAPER GRID */
    .newspaper-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 40px;
    }

    /* LEFT COLUMN — TOP STORIES */
    .story-card {
        border: 5px solid #000000;
        padding: 20px;
        margin-bottom: 25px;
        background: #FFFFFF;
    }

    .story-title {
        font-size: 1.4rem;
        font-weight: 900;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .story-amount {
        background: #FFDE00;
        padding: 6px 10px;
        font-weight: 900;
        font-size: 1.2rem;
        display: inline-block;
        margin-bottom: 10px;
        border: 3px solid #000000;
    }

    .story-date {
        font-family: monospace;
        font-size: 0.9rem;
        margin-bottom: 10px;
    }

    /* RIGHT COLUMN — NEWSLETTER */
    .newsletter-block {
        border-left: 6px solid #000000;
        padding-left: 25px;
    }

    .newsletter-title {
        font-size: 2.2rem;
        font-weight: 900;
        text-transform: uppercase;
        margin-bottom: 20px;
    }

    .newsletter-entry {
        margin-bottom: 25px;
        padding-bottom: 15px;
        border-bottom: 4px solid #000000;
    }

    .newsletter-entry h3 {
        font-size: 1.4rem;
        font-weight: 800;
        text-transform: uppercase;
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

# ---------------------------------------------------------
# FETCH TECHCRUNCH AI FEED
# ---------------------------------------------------------
@st.cache_data
def fetch_articles():
    url = "https://techcrunch.com/tag/artificial-intelligence/feed/"
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:20]:
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "summary": entry.summary
        })
    return articles

articles = fetch_articles()

# ---------------------------------------------------------
# EXTRACT INVESTMENT INFO
# ---------------------------------------------------------
def extract_investment_info(article):
    text = article["title"] + " " + article["summary"]

    amounts = re.findall(r"\$[0-9,.]+[MB]?", text)
    rounds = re.findall(r"(Series [A-Z]|Seed round|funding round)", text, re.IGNORECASE)
    investors = re.findall(r"([A-Z][a-zA-Z0-9& ]+)(?= (invested|led))", text)

    return {
        "title": article["title"],
        "link": article["link"],
        "published": article["published"],
        "amounts": amounts,
        "rounds": rounds,
        "investors": [i[0].strip() for i in investors]
    }

structured = [extract_investment_info(a) for a in articles]

# ---------------------------------------------------------
# NEWSPAPER GRID LAYOUT
# ---------------------------------------------------------
st.markdown('<div class="newspaper-grid">', unsafe_allow_html=True)

# LEFT COLUMN — TOP STORIES
st.markdown('<div>', unsafe_allow_html=True)
for item in structured[:6]:
    st.markdown(f"""
        <div class="story-card">
            <div class="story-title">{item['title']}</div>
            <div class="story-amount">{', '.join(item['amounts']) if item['amounts'] else '—'}</div>
            <div class="story-date">{item['published']}</div>
            <a href="{item['link']}" target="_blank">Read more</a>
        </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# RIGHT COLUMN — NEWSLETTER
st.markdown('<div class="newsletter-block">', unsafe_allow_html=True)
st.markdown('<div class="newsletter-title">The Newsletter</div>', unsafe_allow_html=True)

for item in structured:
    st.markdown(f"""
        <div class="newsletter-entry">
            <h3>{item['title']}</h3>
            <p><strong>Funding:</strong> {', '.join(item['amounts']) if item['amounts'] else '—'}</p>
            <p><strong>Round:</strong> {', '.join(item['rounds']) if item['rounds'] else '—'}</p>
            <p><strong>Investors:</strong> {', '.join(item['investors']) if item['investors'] else '—'}</p>
            <a href="{item['link']}" target="_blank">Read more</a>
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
