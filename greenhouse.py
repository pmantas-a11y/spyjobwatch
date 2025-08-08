
import requests, datetime as dt
from bs4 import BeautifulSoup
from .base import BaseScraper

class GreenhouseScraper(BaseScraper):
    def fetch(self, company: str):
        r = requests.get(self.careers_url, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        res = []
        for job in soup.select("div.opening a"):
            title = job.text.strip()
            href = job.get("href")
            url = href if href.startswith("http") else self.careers_url.rstrip("/") + "/" + href.lstrip("/")
            # try to get job_id from URL
            job_id = url.split("/")[-1].split("?")[0]
            # Greenhouse doesn't expose posted date on board; leave None
            res.append({
                "job_id": job_id,
                "title": title,
                "location": None,
                "department": None,
                "posted_date": None,
                "url": url,
                "company": company,
            })
        return res
