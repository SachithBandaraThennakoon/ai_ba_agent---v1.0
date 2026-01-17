from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def solution_architect_agent(ba_output: str) -> str:
    with open("prompts/solution_architect.txt", "r") as f:
        system_prompt = f.read()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ba_output}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content
