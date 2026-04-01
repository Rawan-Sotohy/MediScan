import os
import anthropic


client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are MediScan's medical assistant.
You help users understand their medications, dosages, and schedules.
Answer clearly and simply.
If a question is outside medication topics, politely redirect.
Never diagnose or replace a doctor's advice."""


def ask_chatbot(user_message: str, conversation_history: list = None) -> dict:
    """
    Takes user message and conversation history, returns chatbot reply
    """
    if conversation_history is None:
        conversation_history = []

    messages = conversation_history + [
        {"role": "user", "content": user_message}
    ]

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=messages
        )

        reply = response.content[0].text

        return {
            "success": True,
            "reply": reply,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "reply": "",
            "error": str(e)
        }