from openai import OpenAI
from dotenv import load_dotenv
from vector_db.company_knowledge import query_company_knowledge

load_dotenv()
client = OpenAI()

def final_proposal_agent(ba_output: str, architect_output: str) -> str:
    with open("prompts/final_proposal.txt", "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # Retrieve company knowledge using Vector DB (RAG)
    company_context = query_company_knowledge(
        "company overview, services, and technical capabilities"
    )

    combined_input = f"""
COMPANY CONTEXT:
{company_context}

BUSINESS ANALYST OUTPUT:
{ba_output}

SOLUTION ARCHITECT OUTPUT:
{architect_output}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": combined_input}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content
