
import requests, re
from urllib.parse import urlparse
from .base import BaseScraper

# Workday is notoriously fragmented. This adapter tries common JSON endpoints:
# 1) /wday/cxs/{tenant}/{site}/jobs (Workday CxS API)
# 2) Some tenants expose a search API under /wday/cxs/{tenant}/careers/jobs
# If neither works, it returns an empty list (user may need a custom adapter).

class WorkdayScraper(BaseScraper):
    def fetch(self, company: str):
        base = self.careers_url.rstrip('/')
        parsed = urlparse(base)
        host = parsed.netloc
        # guess tenant: subdomain before .myworkdayjobs.com or wdX.myworkdayjobs.com/{tenant}/...
        tenant = None
        m = re.search(r"([^.]+)\.myworkdayjobs\.com", host)
        if m:
            tenant = m.group(1)
        else:
            # try to extract from path
            m2 = re.search(r"myworkdayjobs\.com/([^/]+)/", base)
            if m2:
                tenant = m2.group(1)
        candidates = []
        if tenant:
            candidates.append(f"https://{host}/wday/cxs/{tenant}/careers/jobs")
            # Some sites use a branded site key instead of 'careers'
            path_parts = [p for p in parsed.path.split('/') if p]
            if len(path_parts) >= 1:
                site_key = path_parts[0]
                candidates.append(f"https://{host}/wday/cxs/{tenant}/{site_key}/jobs")
        # Microsoft/Meta/Apple/Google often use fully custom pipelines — likely won't hit here
        res = []
        for api in candidates:
            try:
                r = requests.get(api, timeout=30)
                if r.status_code != 200:
                    continue
                data = r.json()
                for job in data.get("jobPostings", []):
                    # keys vary; do best effort
                    jid = job.get("bulletFields", [{}])[0].get("text") if job.get("bulletFields") else job.get("externalPath")
                    url = f"{base}/{job.get('externalPath')}" if job.get("externalPath") else base
                    posted = (job.get("postedOn") or job.get("startDate") or job.get("createdOn"))
                    if isinstance(posted, str):
                        posted = posted[:10]
                    res.append({
                        "job_id": jid,
                        "title": job.get("title"),
                        "location": (job.get("locationsText") or job.get("location")),
                        "department": job.get("secondaryPostedCategory") or job.get("primaryPostedCategory"),
                        "posted_date": posted,
                        "url": url,
                        "company": company,
                    })
                if res:
                    break
            except Exception:
                continue
        return res
