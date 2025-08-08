
import requests, datetime as dt
from .base import BaseScraper

class LeverScraper(BaseScraper):
    def fetch(self, company: str):
        # Lever JSON endpoint: https://api.lever.co/v0/postings/{company}?mode=json
        # careers_url like https://jobs.lever.co/uber
        slug = self.careers_url.rstrip('/').split('/')[-1]
        api = f"https://api.lever.co/v0/postings/{slug}?mode=json"
        r = requests.get(api, timeout=30)
        r.raise_for_status()
        items = r.json()
        res = []
        for it in items:
            posted = None
            if it.get("createdAt"):
                posted = dt.datetime.utcfromtimestamp(it["createdAt"]/1000).date().isoformat()
            res.append({
                "job_id": it.get("id") or it.get("leverId") or it.get("externalPostingId"),
                "title": it.get("text") or it.get("title"),
                "location": (it.get("categories") or {}).get("location"),
                "department": (it.get("categories") or {}).get("team"),
                "posted_date": posted,
                "url": it.get("hostedUrl") or it.get("applyUrl"),
                "company": company,
            })
        return res
