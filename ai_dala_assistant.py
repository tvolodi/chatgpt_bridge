# ai_dala_assistant.py
from openai import OpenAI
import requests, os, json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BRIDGE_URL = os.getenv("BRIDGE_URL")
BRIDGE_KEY = os.getenv("BRIDGE_KEY")

# Define how GPT can use your Notion bridge
tools = [
    {
        "type": "function",
        "function": {
            "name": "call_bridge",
            "description": "Send an action to the AI Dala ↔ Notion Bridge",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "Type of Notion operation"},
                    "alias": {"type": "string", "description": "Alias name for page or database"},
                    "title": {"type": "string", "description": "Page title"},
                    "properties": {"type": "object", "description": "Notion properties or content"}
                },
                "required": ["action"]
            }
        }
    }
]

assistant = client.beta.assistants.create(
    name="AI Dala Assistant",
    instructions=(
        "You are AI Dala, a project manager connected to a Notion workspace. "
        "When managing projects, you can use the 'call_bridge' function to create, update, "
        "and organize content in Notion through the bridge."
    ),
    model="gpt-4-turbo",
    tools=tools
)

print("✅ Assistant created:", assistant.id)
