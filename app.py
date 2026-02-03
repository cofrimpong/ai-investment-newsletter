import streamlit as st
import feedparser
import pandas as pd
import re
from datetime import datetime

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="AI Investment Daily",
    layout="wide"
)

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown(
    """
    <style>

        /* GLOBAL RESET */
        body, .stApp {
            background: #ffffff !important;
            color: #000000 !important;
            font-family: 'Inter', sans-serif;
        }

        /* NEO-BRUTALIST COLORS */
        :root {
            --primary: #000000;
            --accent: #ffde00;
            --border: 4px solid #000000;
        }

        /* HEADERS */
        .hero-title {
            font-size: 3.2rem;
            font-weight: 900;
            padding: 10px 0;
            border-bottom: var(--border);
            text-transform: uppercase;
        }

        .hero-sub {
            font-size: 1.2rem;
            font-weight: 500;
            margin-top: 10px;
            padding: 10px;
            background: var(--accent);
            border: var(--border);
        }

        .section-title {
            font-size: 1.6rem;
            font-weight: 800;
            margin-top: 40px;
            padding: 8px 12px;
            background: #ffffff;
            border-left: var(--border);
            border-bottom: var(--border);
        }

        /* DIVIDERS */
        .divider {
            border-bottom: var(--border);
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }

        /* HEADLINES */
        .headline {
            font-size: 1.2rem;
            font-weight: 800;
            padding: 6px;
            border: var(--border);
            background: #ffffff;
        }

        .subtle {
            font-size: 0.85rem;
            color: #333333;
            margin-bottom: 5px;
        }

        /* TABLE */
        .dataframe {
            border: var(--border) !important;
        }

        .dataframe th {
            background: var(--accent) !important;
            border: var(--border) !important;
            font-weight: 900 !important;
        }

        .dataframe td {
            border: var(--border) !important;
        }

        /* LINKS */
        a {
            color: #000000 !important;
            font-weight: 700;
            text-decoration: underline !important;
        }

        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background: #ffde00 !important;
            border-right: var(--border);
        }

        section[data-testid="stSidebar"] * {
            color: #000000 !important;
            font-weight: 700 !important;
        }

        /* BUTTONS */
        .stButton>button {
            background: #ffffff !important;
            border: var(--border) !important;
            color: #000000 !important;
            font-weight: 800 !important;
            padding: 10px 20px;
            text-transform: uppercase;
        }

        .stButton>button:hover {
            background: var(--accent) !important;
        }

    </style>
    """,
    unsafe_allow_html=True
)
# -----------------------------
# Hero Section
# -----------------------------
st.markdown("<p class='hero-title'>AI Investment Daily</p>", unsafe_allow_html=True)
st.markdown("<p class='hero-sub'>Tracking who is funding the future of AI — updated continuously using TechCrunch’s AI feed.</p>", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# Timestamp
now = datetime.now().strftime("%B %d, %Y — %I:%M %p EST")
st.caption(f"Last updated: {now}")

# -----------------------------
# Fetch Articles
# -----------------------------
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

with st.spinner("Fetching latest AI investment articles..."):
    articles = fetch_articles()

# -----------------------------
# Extract Investment Info
# -----------------------------
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

# Convert to DataFrame for table
df = pd.DataFrame(structured)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filter Investments")

min_amount = st.sidebar.selectbox(
    "Minimum Funding Amount",
    ["None", "$1M", "$10M", "$50M", "$100M"]
)

round_filter = st.sidebar.selectbox(
    "Round Type",
    ["All", "Seed", "Series A", "Series B", "Series C"]
)

# -----------------------------
# Top 5 Deals Section
# -----------------------------
st.markdown("<p class='section-title'>🔥 Top 5 AI Deals Today</p>", unsafe_allow_html=True)

top_deals = df[df["amounts"].map(lambda x: len(x) > 0)]

for _, row in top_deals.head(5).iterrows():
    st.markdown(f"**{row['title']}**")
    if row["amounts"]:
        st.write("Funding:", ", ".join(row["amounts"]))
    if row["rounds"]:
        st.write("Round:", ", ".join(row["rounds"]))
    if row["investors"]:
        st.write("Investors:", ", ".join(row["investors"]))
    st.markdown(f"[Read more]({row['link']})")
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# -----------------------------
# Investment Table
# -----------------------------
st.markdown("<p class='section-title'>📊 AI Investment Database</p>", unsafe_allow_html=True)

df_display = df.copy()
df_display["Funding"] = df_display["amounts"].apply(lambda x: ", ".join(x) if x else "")
df_display["Round"] = df_display["rounds"].apply(lambda x: ", ".join(x) if x else "")
df_display["Investors"] = df_display["investors"].apply(lambda x: ", ".join(x) if x else "")

df_display = df_display[["title", "Funding", "Round", "Investors", "link"]]

st.dataframe(df_display, use_container_width=True)

# -----------------------------
# Newsletter Section
# -----------------------------
st.markdown("<p class='section-title'>📰 Generated Newsletter</p>", unsafe_allow_html=True)

newsletter = ""
for _, row in df_display.iterrows():
    newsletter += f"### {row['title']}\n"
    if row['Funding']:
        newsletter += f"- **Funding:** {row['Funding']}\n"
    if row['Round']:
        newsletter += f"- **Round:** {row['Round']}\n"
    if row['Investors']:
        newsletter += f"- **Investors:** {row['Investors']}\n"
    newsletter += f"- [Read more]({row['link']})\n\n"

st.markdown(newsletter)
