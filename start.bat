@echo off
call venv\Scripts\activate
uvicorn notion_bridge:app --host 0.0.0.0 --port 8000