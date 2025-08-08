
    import streamlit as st
    import pandas as pd
    from datetime import date
    from scrapers.greenhouse import GreenhouseScraper
    from scrapers.lever import LeverScraper
    from scrapers.smartrecruiters import SmartRecruitersScraper
    from scrapers.workday import WorkdayScraper
    from storage import init_db, upsert_company, upsert_postings, get_postings, compute_week_roc
    from utils import resolve_company

    st.set_page_config(page_title="S&P 500 JobWatch", page_icon="🧭", layout="wide")
    st.title("S&P 500 JobWatch")
    st.write("Type a ticker (e.g., `NVDA`) to see job postings and a 7‑day rate-of-change signal.")

    init_db()

    ticker = st.text_input("Ticker", "NVDA").upper().strip()
    if not ticker:
        st.stop()
    meta = resolve_company(ticker)
    if not meta:
        st.warning("Ticker not found in `companies.yaml`. Add it and reload.")
        st.stop()

    ats = meta["ats"]
    careers_url = meta["careers_url"]
    company = meta["company"]
    upsert_company(ticker, company, ats, careers_url)

    st.markdown(f"**{company}** — ATS: `{ats}`  
Careers: {careers_url}")

    SCRAPER_MAP = {
        "greenhouse": GreenhouseScraper,
        "lever": LeverScraper,
        "smartrecruiters": SmartRecruitersScraper,
        "workday": WorkdayScraper,
    }

    colA, colB = st.columns([1,1])
    with colA:
        if st.button("🔄 Scrape now"):
            Scr = SCRAPER_MAP.get(ats)
            if not Scr:
                st.error(f"No scraper registered for ATS '{ats}'. Add an adapter in app/scrapers/.")
            else:
                try:
                    rows = Scr(careers_url).fetch(company)
                    upsert_postings(ticker, rows)
                    st.success(f"Fetched {len(rows)} postings and stored to DB.")
                except Exception as e:
                    st.exception(e)

    rows = get_postings(ticker)
    if rows:
        df = pd.DataFrame(rows)
        df["posted_date"] = pd.to_datetime(df["posted_date"], errors="coerce").dt.date
        st.subheader("Postings")
        st.dataframe(df[["posted_date","title","location","department","url"]].sort_values("posted_date", ascending=False), use_container_width=True)
        last7, prev7, roc = compute_week_roc(ticker)
        st.subheader("7‑day Rate of Change")
        st.metric(label="Last 7d vs Prior 7d", value=f"{last7} vs {prev7}", delta=f"{roc:+.1%}")
    else:
        st.info("No postings in DB yet. Click **Scrape now**.")
