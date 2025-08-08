
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseScraper(ABC):
    def __init__(self, careers_url: str):
        self.careers_url = careers_url

    @abstractmethod
    def fetch(self, company: str) -> List[Dict]:
        """Return a list of postings with keys:
        job_id, title, location, department, posted_date (ISO), url, company
        """
        raise NotImplementedError
