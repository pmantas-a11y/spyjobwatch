
import sqlite3, os, datetime as dt
from typing import List, Dict, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "jobwatch.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS postings(
            ticker TEXT,
            company TEXT,
            job_id TEXT,
            title TEXT,
            location TEXT,
            department TEXT,
            posted_date TEXT,
            url TEXT,
            scraped_at TEXT,
            PRIMARY KEY (ticker, job_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS companies(
            ticker TEXT PRIMARY KEY,
            company TEXT,
            ats TEXT,
            careers_url TEXT
        )
    """)
    conn.commit()
    conn.close()

def upsert_company(ticker:str, company:str, ats:str, careers_url:str):
    conn = get_conn()
    conn.execute("""INSERT INTO companies(ticker, company, ats, careers_url)
                  VALUES(?,?,?,?)
                  ON CONFLICT(ticker) DO UPDATE SET company=excluded.company,
                                                   ats=excluded.ats,
                                                   careers_url=excluded.careers_url""",
               (ticker, company, ats, careers_url))
    conn.commit(); conn.close()

def upsert_postings(ticker:str, rows:List[Dict]):
    conn = get_conn()
    now = dt.datetime.utcnow().isoformat()
    for r in rows:
        conn.execute("""INSERT OR REPLACE INTO postings
            (ticker, company, job_id, title, location, department, posted_date, url, scraped_at)
            VALUES(?,?,?,?,?,?,?,?,?)""" ,
            (ticker, r.get("company"), r.get("job_id"), r.get("title"),
             r.get("location"), r.get("department"), r.get("posted_date"),
             r.get("url"), now))
    conn.commit(); conn.close()

def get_postings(ticker:str):
    conn = get_conn()
    cur = conn.execute("SELECT * FROM postings WHERE ticker=? ORDER BY COALESCE(posted_date, '0000-00-00') DESC", (ticker,))
    cols = [c[0] for c in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    conn.close()
    return rows

def compute_week_roc(ticker:str, today:Optional[str]=None):
    # return tuple (last7, prev7, roc)
    conn = get_conn()
    if not today:
        today = dt.date.today()
    else:
        today = dt.date.fromisoformat(today)
    d7 = today - dt.timedelta(days=7)
    d14 = today - dt.timedelta(days=14)
    cur = conn.execute("""
        SELECT COUNT(*) FROM postings
        WHERE ticker=? AND posted_date IS NOT NULL AND date(posted_date) > date(?)""", (ticker, d7.isoformat()))
    last7 = cur.fetchone()[0]
    cur = conn.execute("""
        SELECT COUNT(*) FROM postings
        WHERE ticker=? AND posted_date IS NOT NULL AND date(posted_date) > date(?) AND date(posted_date) <= date(?)""",
        (ticker, d14.isoformat(), d7.isoformat()))
    prev7 = cur.fetchone()[0]
    conn.close()
    denom = prev7 if prev7 else 1
    roc = (last7 - prev7) / denom
    return last7, prev7, roc
