import os
from groq import Groq

from .utils import with_retry


# Configurable via .env for the same reason as the vision model - swap it
# in one place if Groq deprecates it, instead of hunting through the code.
CHAT_MODEL = os.getenv("GROQ_CHAT_MODEL", "openai/gpt-oss-120b")

SYSTEM_PROMPT_TEMPLATE = """You are MediScan's medical assistant.
You help users understand their medications, dosages, and schedules.
User's current medications: {medications_context}
Provide helpful, accurate, and concise responses about medications, dosages, or general health advice.
Always remind users to consult their doctor for medical decisions.
Be friendly and professional. Keep responses under 150 words.
If a question is outside medication topics, politely redirect.
Never diagnose or replace a doctor's advice."""


@with_retry(max_retries=3, base_delay=2)
def _call_chat_model(client: Groq, messages: list):
    return client.chat.completions.create(
        model=CHAT_MODEL,
        max_tokens=300,
        messages=messages,
    )


def ask_chatbot(user_message: str, conversation_history: list = None, medications_context: str = None) -> dict:
    """
    Takes user message, conversation history, and optional medications context.
    Returns chatbot reply using Groq.
    """
    if not user_message or not user_message.strip():
        return {"success": False, "reply": "", "error": "Empty message"}

    if conversation_history is None:
        conversation_history = []

    if not medications_context:
        medications_context = "No medications on record"

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(medications_context=medications_context)

    messages = [{"role": "system", "content": system_prompt}] + conversation_history + [
        {"role": "user", "content": user_message}
    ]

    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = _call_chat_model(client, messages)
        reply = response.choices[0].message.content.strip()

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
