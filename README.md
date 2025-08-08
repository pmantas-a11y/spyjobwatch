
# S&P 500 JobWatch (Streamlit)

Type a ticker (e.g., `NVDA`) and get the company's current job postings
organized by date, plus a 7‑day rate of change signal.

> ⚠️ **Important**: This project scrapes public job boards from the company's
ATS (Greenhouse, Lever, SmartRecruiters, Workday*). Please use responsibly,
respect site `robots.txt`, and follow each site's Terms of Service. This is
for research/analysis only.

## Quickstart

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

The first run creates `jobwatch.db` (SQLite) in the project folder.

## What works today

- **Adapters**: Greenhouse, Lever, SmartRecruiters (stable), Workday (*best effort*).
- **UI**: Enter ticker → we resolve to company and ATS from `data/companies.yaml`.
  Click **Scrape now** to fetch, store, and compute 7‑day rate of change (ROC).
- **Storage**: SQLite tables for `companies`, `postings`. De‑duplicates by (ticker, job_id).
- **Metrics**: 7‑day ROC = ((last 7d postings) − (prior 7d)) / max(1, prior 7d).

## Configure companies

We ship a minimal `data/companies.yaml` with a handful of examples. Add more like:

```yaml
- ticker: NVDA
  company: NVIDIA
  ats: workday
  careers_url: https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite
- ticker: ABNB
  company: Airbnb
  ats: greenhouse
  careers_url: https://boards.greenhouse.io/airbnb
- ticker: UBER
  company: Uber
  ats: lever
  careers_url: https://jobs.lever.co/uber
- ticker: SQ
  company: Block
  ats: smartrecruiters
  careers_url: https://careers.smartrecruiters.com/Square
```

> Tip: Many S&P 500 companies use these four ATSs. If a firm uses a custom
site, add your own adapter in `app/scrapers/`.

## Caveats

- **Workday** is fragmented across tenants/paths. The included adapter handles
  common JSON endpoints but may need per-company tweaks (see comments).
- Posting "date" fields differ by ATS (createdAt, updatedAt, liveAt). We use
  the *earliest available* as `posted_date`.
- Historical rates require multiple scrapes over time. Consider running as a
  cron job (e.g., daily) to build history.

## License

MIT — see `LICENSE`.
