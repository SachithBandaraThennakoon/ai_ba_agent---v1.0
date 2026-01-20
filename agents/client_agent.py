from openai import OpenAI
from dotenv import load_dotenv

from vector_db.company_knowledge import query_company_knowledge
from agents.prompts.client_discovery_prompt import get_client_discovery_prompt
from agents.prompts.client_confirm_prompt import get_client_confirm_prompt

load_dotenv()
client = OpenAI()


def client_agent(session_memory, user_input: str):
    """
    Client Engagement Agent (Xceed)
    - Discovery → CONFIRM → Freeze
    - Company-grounded (Vector DB)
    - Zero hallucination
    """

    # ===============================
    # CONFIRM MODE (FREEZE)
    # ===============================
    if user_input.strip().upper() == "CONFIRM":
        session_memory.confirm()
        system_prompt = get_client_confirm_prompt()
        company_context = ""

    # ===============================
    # DISCOVERY MODE
    # ===============================
    else:
        company_context = query_company_knowledge(
            "What services does Xceed provide? What is Xceed?"
        )

        system_prompt = get_client_discovery_prompt(company_context)

    # ===============================
    # BUILD MESSAGE CONTEXT
    # ===============================
    messages = [
        {"role": "system", "content": system_prompt},
        *session_memory.get(),
        {"role": "user", "content": user_input},
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
    )

    reply = response.choices[0].message.content

    # ===============================
    # STORE CONVERSATION
    # ===============================
    session_memory.add("user", user_input)
    session_memory.add("assistant", reply)

    return reply, session_memory.is_confirmed()
