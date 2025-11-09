# run_ai_dala_extended.py — AI Dala Assistant with Persistent Workspace Memory
import os
import json
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv
from openai import OpenAI

# our new modules
from core.memory_manager import load_memory, save_memory
from bridge.bridge_client import fetch_lookup_from_bridge, execute_bridge_call

load_dotenv()

# --- CONFIG ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = os.getenv("ASSISTANT_ID")  # set after creation

# defaults point to your domain, but can be overridden in .env
BRIDGE_LOOKUP_URL = os.getenv("LOOKUP_URL", "https://ai-dala.com/lookup")
MEMORY_FILE = os.getenv("MEMORY_FILE", "data/ai_dala_memory.json")


# --- HELPERS ---
def needs_refresh(memory, hours=12):
    if not memory.get("last_sync"):
        return True
    last = datetime.fromisoformat(memory["last_sync"])
    return datetime.now() - last > timedelta(hours=hours)


def refresh_lookup(memory):
    print("🔄 Syncing Notion lookup from bridge...")
    lookup = fetch_lookup_from_bridge()
    if lookup is not None:
        memory["lookup"] = lookup
        memory["last_sync"] = datetime.now().isoformat()
        save_memory(MEMORY_FILE, memory)
        # if your lookup has `_meta` or service keys, just show non-underscore ones
        visible = [k for k in lookup.keys() if not k.startswith("_")]
        print(f"✅ Memory synced: {len(visible)} aliases updated.")
    else:
        print("⚠️ Failed to sync lookup.")


def build_context_summary(memory):
    """Summarize workspace structure for the model."""
    summary = ["This is the current Notion workspace structure:"]
    for alias, data in memory.get("lookup", {}).items():
        if alias.startswith("_"):
            continue
        summary.append(f"• {alias} ({data.get('type')}) under {data.get('parent')}")
    return "\n".join(summary)


# --- MAIN CHAT LOOP ---
def chat_with_ai_dala(message: str):
    # load memory from file
    memory = load_memory(MEMORY_FILE)

    # optionally refresh from bridge
    if needs_refresh(memory):
        refresh_lookup(memory)

    context_summary = build_context_summary(memory)
    print("🧠 Context summary injected.\n")

    # create thread
    thread = client.beta.threads.create()

    system_prompt = (
        "You are AI Dala, a persistent project manager connected to Notion. "
        "You know the current workspace structure and aliases. "
        "Use your knowledge to plan, organize, and manage projects.\n\n"
        + context_summary
    )

    # inject system + user
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="system",
        content=system_prompt,
    )
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message,
    )

    # run assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
    )

    # main loop
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status == "requires_action":
            # assistant wants to call our bridge
            action = run.required_action.submit_tool_outputs.tool_calls[0]
            args = json.loads(action.function.arguments)
            print("🔧 GPT requested bridge call:", args)

            result = execute_bridge_call(args)

            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=[
                    {
                        "tool_call_id": action.id,
                        "output": json.dumps(result),
                    }
                ],
            )

        elif run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for m in messages.data:
                if m.role == "assistant":
                    print("\n🤖 AI Dala:", m.content[0].text.value)
            break
        else:
            time.sleep(1)


if __name__ == "__main__":
    print("🚀 AI Dala Persistent Assistant Ready")
    chat_with_ai_dala(
        "Show me the current structure and create a project 'AI Dala Core System'."
    )
