
import yaml, os, pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_companies_yaml():
    path = os.path.join(DATA_DIR, "companies.yaml")
    with open(path, "r") as f:
        return yaml.safe_load(f)

def resolve_company(ticker:str):
    items = load_companies_yaml()
    for it in items:
        if it["ticker"].upper() == ticker.upper():
            return it
    return None
