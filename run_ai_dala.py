# run_ai_dala.py
from openai import OpenAI
import os, json, requests
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = "asst_6BwDC3xABW9Ed5mqA3bFeRBg"  # use the one printed earlier
BRIDGE_URL = os.getenv("BRIDGE_URL")
BRIDGE_KEY = os.getenv("BRIDGE_KEY")

def execute_bridge_call(args):
    """Send GPT's bridge request to your FastAPI backend."""
    headers = {"Content-Type": "application/json", "X-API-KEY": BRIDGE_KEY}
    response = requests.post(BRIDGE_URL, headers=headers, json=args)
    return response.json()

def chat_with_ai_dala(message):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(thread_id=thread.id, role="user", content=message)
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == "requires_action":
            action = run.required_action.submit_tool_outputs.tool_calls[0]
            args = json.loads(action.function.arguments)
            print("🧠 GPT requested bridge call:", args)
            result = execute_bridge_call(args)
            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=[{"tool_call_id": action.id, "output": json.dumps(result)}]
            )
        elif run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for m in messages.data:
                if m.role == "assistant":
                    print("🤖 AI Dala:", m.content[0].text.value)
            break
        else:
            pass

if __name__ == "__main__":
    chat_with_ai_dala("Create a new project in projects called AI Dala Core Integration")
