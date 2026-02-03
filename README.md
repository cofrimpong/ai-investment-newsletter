# 📰 AI Investment Newsletter Factory

This project is an **AI Factory** that automatically generates a daily-style newsletter summarizing **who is investing in AI** and **what AI companies are receiving funding**, using real‑time articles from **TechCrunch**.

The goal is to demonstrate a repeatable, automated pipeline — a “factory” — that can be triggered any time to produce structured insights about AI investment activity.

---

## 🚀 Features

- **Fetches live AI-related articles** from TechCrunch’s Artificial Intelligence RSS feed  
- **Extracts structured investment data**, including:
  - Funding amounts  
  - Round types (Seed, Series A, etc.)  
  - Investors (pattern‑based extraction)  
- **Generates a clean newsletter** summarizing the latest AI funding activity  
- **Runs entirely in the cloud** using Streamlit  
- **No local installation required**

---

## 🧠 How It Works

1. **Collect**  
   The app pulls the latest AI‑tagged articles from TechCrunch.

2. **Process**  
   A lightweight extraction layer identifies:
   - Funding amounts  
   - Round types  
   - Investor names  

3. **Generate**  
   The app formats the extracted information into a readable newsletter.

4. **Display**  
   Streamlit renders the newsletter and article list in a simple web interface.

---

## 📦 Tech Stack

- **Python**
- **Streamlit** — for the web interface  
- **Feedparser** — for reading TechCrunch RSS feeds  
- **Regex** — for lightweight entity extraction  

---

## ▶️ Running the App

This app is deployed on **Streamlit Cloud**.  
Once deployed, you can access it through a public link.

To run locally (optional):

```bash
pip install -r requirements.txt
streamlit run app.py
