from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4

from agents.client_agent import client_agent
from memory.persistent_memory import PersistentSessionMemory
from vector_db.company_knowledge import ensure_company_knowledge_loaded
from graph.proposal_graph import build_proposal_graph

# --------------------------------
# INIT
# --------------------------------
app = FastAPI(title="Xceed AI Pre-Sales Agent")

# Ensure company knowledge is loaded at startup
ensure_company_knowledge_loaded("company_docs")

proposal_graph = build_proposal_graph()
sessions = {}  # session_id -> PersistentSessionMemory


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    confirmed: bool = False


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Create or reuse session
    if req.session_id and req.session_id in sessions:
        session = sessions[req.session_id]
        session_id = req.session_id
    else:
        session_id = str(uuid4())
        session = PersistentSessionMemory(session_id)
        sessions[session_id] = session

    reply, confirmed = client_agent(session, req.message)

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        confirmed=confirmed
    )



@app.post("/generate-proposal")
def generate_proposal(session_id: str):
    if session_id not in sessions:
        return {"error": "Invalid session ID"}

    session = sessions[session_id]

    if not session.is_confirmed():
        return {"error": "Discovery not confirmed yet"}

    # Last assistant message = structured business summary
    client_summary = session.get()[-1]["content"]

    result = proposal_graph.invoke({
        "client_summary": client_summary
    })

    return {
        "final_proposal": result["final_proposal"]
    }



