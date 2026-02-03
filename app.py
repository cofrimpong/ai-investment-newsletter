import streamlit as st
import feedparser
import re

st.set_page_config(page_title="AI Investment Newsletter Factory", layout="wide")

st.title("📰 AI Investment Newsletter Factory")
st.write("Automatically generates a newsletter about who is investing in AI and what AI companies are receiving funding — powered by TechCrunch.")

# --- Fetch TechCrunch AI Feed ---
@st.cache_data
def fetch_articles():
    url = "https://techcrunch.com/tag/artificial-intelligence/feed/"
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:15]:
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "summary": entry.summary
        })
    return articles

articles = fetch_articles()

st.subheader("📡 Latest AI Headlines from TechCrunch")
for a in articles:
    st.markdown(f"**{a['title']}**  \n[{a['link']}]({a['link']})")
    st.write("—", a["published"])
    st.write("")

# --- Extract Investment Info ---
def extract_investment_info(article):
    text = article["title"] + " " + article["summary"]

    # Funding amounts
    amount_pattern = r"\$[0-9,.]+[MB]?"
    amounts = re.findall(amount_pattern, text)

    # Round types
    rounds = re.findall(r"(Series [A-Z]|Seed round|funding round)", text, re.IGNORECASE)

    # Investors (very rough pattern)
    investor_pattern = r"([A-Z][a-zA-Z0-9& ]+)(?= (invested|led))"
    investors = re.findall(investor_pattern, text)

    return {
        "title": article["title"],
        "link": article["link"],
        "amounts": amounts,
        "rounds": rounds,
        "investors": [i[0].strip() for i in investors]
    }

structured = [extract_investment_info(a) for a in articles]

# --- Newsletter Generator ---
def generate_newsletter(structured):
    newsletter = "## 📰 AI Investment Daily — Structured Edition\n\n"

    for item in structured:
        newsletter += f"### {item['title']}\n"
        if item['amounts']:
            newsletter += f"- **Funding:** {', '.join(item['amounts'])}\n"
        if item['rounds']:
            newsletter += f"- **Round:** {', '.join(item['rounds'])}\n"
        if item['investors']:
            newsletter += f"- **Investors:** {', '.join(item['investors'])}\n"
        newsletter += f"- [Read more]({item['link']})\n\n"

    return newsletter

st.subheader("🧠 Generated Newsletter")
newsletter_output = generate_newsletter(structured)
st.markdown(newsletter_output)
