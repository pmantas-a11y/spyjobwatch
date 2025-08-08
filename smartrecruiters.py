
import requests, datetime as dt
from .base import BaseScraper

class SmartRecruitersScraper(BaseScraper):
    def fetch(self, company: str):
        # careers_url like https://careers.smartrecruiters.com/Square
        # API: https://api.smartrecruiters.com/v1/companies/{slug}/postings
        slug = self.careers_url.rstrip('/').split('/')[-1]
        url = f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=200"
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        res = []
        for it in data.get("content", []):
            posted = it.get("releasedDate") or it.get("createdOn")
            if posted and isinstance(posted, str):
                posted = posted[:10]
            res.append({
                "job_id": it.get("id"),
                "title": it.get("name"),
                "location": (it.get("location") or {}).get("city"),
                "department": (it.get("department") or {}).get("label"),
                "posted_date": posted,
                "url": (it.get("applyUrl") or it.get("referralUrl") or it.get("uuId")),
                "company": company,
            })
        return res
