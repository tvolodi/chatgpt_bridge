# bridge/bridge_client.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BRIDGE_URL = os.getenv("BRIDGE_URL", "https://ai-dala.com/notion")
BRIDGE_LOOKUP_URL = os.getenv("LOOKUP_URL", "https://ai-dala.com/lookup")
BRIDGE_KEY = os.getenv("BRIDGE_KEY")


def _headers():
    headers = {"Content-Type": "application/json"}
    if BRIDGE_KEY:
        headers["X-API-KEY"] = BRIDGE_KEY
    return headers


def fetch_lookup_from_bridge():
    try:
        res = requests.get(BRIDGE_LOOKUP_URL, headers=_headers(), timeout=10)
        if res.status_code == 200:
            return res.json()
        else:
            print("⚠️ Bridge lookup failed:", res.text)
            return None
    except Exception as e:
        print("⚠️ Bridge lookup error:", e)
        return None


def execute_bridge_call(args: dict):
    try:
        res = requests.post(BRIDGE_URL, headers=_headers(), json=args, timeout=15)
        # return JSON or raw text
        try:
            return res.json()
        except Exception:
            return {"status": res.status_code, "text": res.text}
    except Exception as e:
        return {"error": str(e)}
