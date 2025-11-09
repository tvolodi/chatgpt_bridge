# notion_bridge.py — Integrated Bridge with Object Tree Indexing
from fastapi import FastAPI, Request
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# --- LOAD ENVIRONMENT ---
load_dotenv()

# --- CONFIGURATION ---
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")
PORT = int(os.getenv("PORT", 8000))
API_KEY = os.getenv("API_KEY", NOTION_TOKEN)
ROOT_PAGE_ID = os.getenv("ROOT_PAGE_ID")
LOOKUP_PATH = os.getenv("LOOKUP_PATH", "lookup.json")

app = FastAPI(title="AI Dala ↔ Notion Bridge")

# --- UTILITIES ---
def notion_headers():
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

# --- OBJECT TREE INDEXING ---
def list_children(block_id: str):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children?page_size=100"
    try:
        res = requests.get(url, headers=notion_headers())
        res.raise_for_status()
        return res.json().get("results", [])
    except Exception as e:
        print(f"⚠️  Error listing children for {block_id}: {e}")
        return []

def crawl_tree(root_id: str, depth: int = 3):
    lookup = {}
    queue = [(root_id, 0)]
    seen = set()
    while queue:
        current, level = queue.pop(0)
        if current in seen or level > depth:
            continue
        seen.add(current)
        children = list_children(current)
        for child in children:
            obj_id = child["id"].replace("-", "")
            obj_type = child["type"]
            title = None
            if "child_page" in child:
                title = child["child_page"].get("title")
            elif "child_database" in child:
                title = child["child_database"].get("title")
            if title:
                lookup[title.strip().lower()] = {
                    "id": obj_id,
                    "type": obj_type,
                    "parent": current,
                    "level": level,
                }
            if obj_type in ("child_page", "child_database"):
                queue.append((obj_id, level + 1))
    lookup["_meta"] = {"updated": datetime.now().isoformat(), "root": root_id}
    return lookup

def update_lookup(root_id: str = None, path: str = LOOKUP_PATH):
    root_id = root_id or ROOT_PAGE_ID
    if not root_id:
        raise ValueError("Root page ID not configured.")
    lookup = crawl_tree(root_id)
    with open(path, "w") as f:
        json.dump(lookup, f, indent=2)
    print(f"✅ Object tree updated: {len(lookup) - 1} entries saved → {path}")
    return lookup

def resolve_alias(alias_or_id: str):
    if not os.path.exists(LOOKUP_PATH):
        return alias_or_id
    try:
        with open(LOOKUP_PATH) as f:
            lookup = json.load(f)
        alias = alias_or_id.lower()
        if alias in lookup:
            return lookup[alias]["id"]
        return alias_or_id
    except Exception:
        return alias_or_id

# --- NOTION API OPERATIONS ---
def notion_create_page(title: str, parent_id: str):
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"page_id": parent_id},
        "properties": {"title": {"title": [{"text": {"content": title}}]}}
    }
    return requests.post(url, headers=notion_headers(), data=json.dumps(payload))

def notion_update_page(page_id: str, properties: dict):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"properties": properties}
    return requests.patch(url, headers=notion_headers(), data=json.dumps(payload))

def notion_add_block(page_id: str, text: str, block_type: str = "paragraph"):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    if block_type.startswith("heading_"):
        block = {"object": "block", "type": block_type, block_type: {"rich_text": [{"text": {"content": text}}]}}
    else:
        block = {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": text}}]}}
    payload = {"children": [block]}
    return requests.patch(url, headers=notion_headers(), data=json.dumps(payload))

def notion_list_children(block_id: str):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children?page_size=100"
    return requests.get(url, headers=notion_headers())

def notion_query_database(database_id: str, filter_obj: dict = None):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    payload = {"filter": filter_obj} if filter_obj else {}
    return requests.post(url, headers=notion_headers(), data=json.dumps(payload))

def notion_search(query: str):
    url = "https://api.notion.com/v1/search"
    payload = {"query": query, "page_size": 20}
    return requests.post(url, headers=notion_headers(), data=json.dumps(payload))

# --- API ENDPOINTS ---
@app.post("/notion")
async def handle_notion_action(request: Request):
    api_key = request.headers.get("X-API-KEY")
    if api_key != API_KEY:
        return {"status": "error", "message": "Unauthorized: invalid API key"}

    body = await request.json()
    action = body.get("action")

    # Resolve aliases if provided
    if body.get("alias") and not body.get("parent_id"):
        body["parent_id"] = resolve_alias(body["alias"])

    if action == "create_page":
        res = notion_create_page(body.get("title", "Untitled"), body.get("parent_id"))
    elif action == "update_page":
        res = notion_update_page(body.get("page_id"), body.get("properties", {}))
    elif action == "add_block":
        res = notion_add_block(body.get("page_id"), body.get("text", ""), body.get("block_type", "paragraph"))
    elif action == "list_children":
        res = notion_list_children(body.get("block_id"))
    elif action == "query_database":
        res = notion_query_database(body.get("database_id"), body.get("filter"))
    elif action == "search":
        res = notion_search(body.get("query", ""))
    elif action == "template":
        return create_template(body.get("template_type", "project"), body.get("parent_id"))
    elif action == "batch":
        return batch_execute(body.get("operations", []))
    else:
        return {"status": "error", "message": f"Unknown action: {action}"}

    if res.status_code == 200:
        try:
            return {"status": "success", "response": res.json()}
        except Exception:
            return {"status": "success", "message": "Action completed."}
    else:
        return {"status": "error", "code": res.status_code, "details": res.text}

# --- OBJECT TREE ENDPOINTS ---
@app.post("/update_tree")
async def update_tree_endpoint(request: Request):
    body = await request.json()
    root_id = body.get("root_id", ROOT_PAGE_ID)
    lookup = update_lookup(root_id)
    return {"status": "success", "updated": lookup.get("_meta", {})}

@app.get("/lookup")
def get_lookup():
    if not os.path.exists(LOOKUP_PATH):
        return {"status": "empty"}
    with open(LOOKUP_PATH) as f:
        lookup = json.load(f)
    return lookup

# --- WEBHOOK ENDPOINT ---
@app.post("/notion/webhook")
async def notion_webhook(request: Request):
    data = await request.json()
    print(f"\n🔔 Notion Webhook Received @ {datetime.now().isoformat()}\n{json.dumps(data, indent=2)}\n")
    update_lookup(ROOT_PAGE_ID)
    return {"status": "logged"}

# --- TEMPLATE CREATION ---
def create_template(template_type: str, parent_id: str):
    templates = {
        "project": [
            {"type": "heading_1", "text": "Project Overview"},
            {"type": "paragraph", "text": "Goals, scope, and stakeholders."},
            {"type": "heading_2", "text": "Milestones"},
            {"type": "paragraph", "text": "List key milestones here."}
        ],
        "task": [
            {"type": "heading_1", "text": "Task Details"},
            {"type": "paragraph", "text": "Describe the task and assign owners."}
        ],
        "meeting": [
            {"type": "heading_1", "text": "Meeting Notes"},
            {"type": "paragraph", "text": "Agenda and discussion points."}
        ]
    }
    title = f"New {template_type.capitalize()} Template"
    page_res = notion_create_page(title, parent_id)
    if page_res.status_code != 200:
        return {"status": "error", "details": page_res.text}
    page_id = page_res.json().get("id")
    for block in templates.get(template_type, []):
        notion_add_block(page_id, block["text"], block["type"])
    return {"status": "success", "page_id": page_id, "url": page_res.json().get("url")}

# --- BATCH EXECUTION ---
def batch_execute(operations: list):
    results = []
    for op in operations:
        try:
            subreq = requests.post("http://localhost:8000/notion", json=op)
            results.append({"op": op, "status": subreq.status_code})
        except Exception as e:
            results.append({"op": op, "error": str(e)})
    return {"status": "success", "results": results}

# --- RUN LOCALLY ---
if __name__ == "__main__":
    import uvicorn
    if ROOT_PAGE_ID:
        update_lookup(ROOT_PAGE_ID)
    print(f"🚀 Starting AI Dala ↔ Notion Bridge on http://localhost:{PORT} ...")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
