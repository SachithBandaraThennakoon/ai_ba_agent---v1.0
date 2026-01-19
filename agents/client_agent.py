from openai import OpenAI
from dotenv import load_dotenv
from vector_db.company_knowledge import query_company_knowledge

load_dotenv()
client = OpenAI()


def client_agent(session_memory, user_input: str):
    """
    Client Engagement Agent for Xceed
    - Discovery chat
    - Company-aware (Vector DB)
    - Strict grounding (no hallucination)
    - CONFIRM → structured summary
    """

    # ===============================
    # CONFIRM MODE (FREEZE POINT)
    # ===============================
    if user_input.strip().upper() == "CONFIRM":
        session_memory.confirm()

        system_prompt = """
You are a Client Engagement Agent.

The client has CONFIRMED the understanding.

Your task:
Generate a FINAL, structured business summary.

STRICT RULES:
- Do NOT introduce new information
- Do NOT mention company services unless they are directly related to the problem
- Be concise and professional

Output format (MANDATORY):
1. Business Problem Statement
2. Business Goals
"""

        company_context = ""  # Not needed after freeze

    # ===============================
    # DISCOVERY CHAT MODE
    # ===============================
    else:
        # Retrieve ONLY company knowledge (authoritative)
        company_context = query_company_knowledge(
            "What services does Xceed provide? What is Xceed?"
        )

        system_prompt = f"""
You are a Client Engagement Agent representing the company **Xceed**.

=========================
OFFICIAL COMPANY INFORMATION (SOURCE OF TRUTH)
=========================
{company_context}

=========================
CRITICAL RULES (MUST FOLLOW)
=========================
- You MUST answer company-related questions ONLY using the information above
- You MUST NOT invent, infer, rename, or generalize services
- If something is not listed above, clearly say it is not offered
- Use the SAME service names as provided
- If the client asks for more details, explain ONLY what is supported by the information above
- If information is missing, say: "I don’t have that information at the moment."
- Always guide the conversation toward understanding the client’s business challenge
- you have experience in mini level project and don't mention that you don't have experience 
- answer in a way that shows you have experience in mid level project
- If the client asks for pricing, say: "after reviewing your business needs, we can provide a tailored pricing plan."
- answer short, simple, and point wise for mid tech level client
- Always maintain a friendly, professional tone

=========================
MODE: DISCOVERY CHAT
=========================
Your behavior:
- Be friendly, confident, and professional
- Clearly explain who Xceed is when asked
- Clearly explain Xceed’s services when asked
- Use simple business language (avoid deep technical detail unless requested)
- After answering company questions, guide the conversation toward understanding the client’s business challenge
- Ask focused, business-oriented questions
- When the problem is clear, ask the client to type **CONFIRM**
"""

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


    if "yes" in user_input.lower() or "received" in user_input.lower():
        session_memory.add("system", "✅ Email confirmed by client.")
        session_memory.add("system", "🎉 Business process completed. Thank you!")   

