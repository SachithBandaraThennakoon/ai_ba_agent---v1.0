from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4
import os
from dotenv import load_dotenv

# ---- Load env ----
load_dotenv()

#--------------------------------------------------
from fastapi.middleware.cors import CORSMiddleware



# ---- Azure Communication Services ----
from azure.communication.email import EmailClient

ACS_CONNECTION_STRING = os.getenv("ACS_CONNECTION_STRING")
ACS_SENDER_EMAIL = os.getenv("ACS_SENDER_EMAIL")

if not ACS_CONNECTION_STRING or not ACS_SENDER_EMAIL:
    raise RuntimeError("ACS email environment variables not set")

email_client = EmailClient.from_connection_string(
    ACS_CONNECTION_STRING
)

# ---- Internal imports ----
from agents.client_agent import client_agent
from memory.persistent_memory import PersistentSessionMemory
from vector_db.company_knowledge import ensure_company_knowledge_loaded

def get_final_proposal_from_session(session) -> str | None:
    messages = session.get()
    for msg in reversed(messages):
        if msg.get("type") == "proposal":
            return msg["content"]
    return None



# --------------------------------------------------
# FASTAPI APP
# --------------------------------------------------
app = FastAPI(title="Xceed AI Backend")

# --------------------------------------------------
# CORS
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# STARTUP
# --------------------------------------------------
@app.on_event("startup")
def startup_event():
    ensure_company_knowledge_loaded("company_docs")
    print("✅ Company knowledge loaded")

# --------------------------------------------------
# MODELS
# --------------------------------------------------
class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str

class EmailRequest(BaseModel):
    session_id: str
    email: str

# --------------------------------------------------
# IN-MEMORY SESSION STORE
# --------------------------------------------------
sessions: dict[str, PersistentSessionMemory] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",                 # local dev (Vite)
        "http://localhost:3000",                 # local dev (CRA)
        "https://sachithbandarathennakoon.github.io",
        "https://www.xceed.live",
        "https://xceed.live",
        'https://sachithbandarathennakoon.github.io/xceed-ai-ui/',
        "https://sachiththennakoon.com",
        "https://www.sachiththennakoon.com",
        "http://localhost:5174/xceed-ai-ui/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#--------------------------------------------------

# --------------------------------------------------
# CHAT ENDPOINT
# --------------------------------------------------
@app.post("/chat")
def chat(req: ChatRequest):
    if req.session_id and req.session_id in sessions:
        session = sessions[req.session_id]
        session_id = req.session_id
    else:
        session_id = str(uuid4())
        session = PersistentSessionMemory(session_id)
        sessions[session_id] = session

    reply, confirmed = client_agent(session, req.message)

    return {
        "session_id": session_id,
        "reply": reply,
        "confirmed": confirmed
    }

# --------------------------------------------------
# GENERATE PROPOSAL
# --------------------------------------------------
@app.post("/generate-proposal")
def generate_proposal(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Invalid session ID")

    session = sessions[session_id]

    if not session.is_confirmed():
        raise HTTPException(status_code=400, detail="Discovery not confirmed")

    client_summary = session.get()[-1]["content"]

    from graph.proposal_graph import build_proposal_graph
    graph = build_proposal_graph()

    result = graph.invoke({
        "client_summary": client_summary
    })

    final_proposal = result["final_proposal"]

    session.add(
        role="assistant",
        content=final_proposal,
        message_type="proposal"   # 👈 IMPORTANT
    )

    return {"final_proposal": final_proposal}


# --------------------------------------------------
# SEND PROPOSAL EMAIL (ACS)
# --------------------------------------------------
@app.post("/send-email")
def send_email(req: EmailRequest):
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[req.session_id]
    proposal = get_final_proposal_from_session(session)

    if not proposal:
        raise HTTPException(status_code=400, detail="Final proposal not found")

    pdf_path = markdown_to_pdf(proposal)

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    send_proposal_email(
        to_email=req.email,
        pdf_bytes=pdf_bytes
    )

    return {"status": "sent"}

# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------
@app.get("/")
def health():
    return {"status": "Xceed AI backend running"}


#--------------------------------------------------

from fastapi import HTTPException
from pydantic import BaseModel

from services.pdf_service import markdown_to_pdf
from services.email_service import send_proposal_email

# -------------------------------
# REQUEST MODEL
# -------------------------------
class EmailRequest(BaseModel):
    session_id: str
    email: str


# -------------------------------
# SEND PROPOSAL EMAIL (PDF)
# -------------------------------
@app.post("/send-proposal-email")
def send_proposal_email_api(req: EmailRequest):
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[req.session_id]

    # ✅ Get explicitly stored final proposal
    proposal = session.get_final_proposal()
    if not proposal:
        raise HTTPException(status_code=400, detail="Final proposal not found")

    # ✅ Generate PDF from markdown proposal
    pdf_path = markdown_to_pdf(proposal)

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # ✅ Send email with PDF attachment
    send_proposal_email(
        to_email=req.email,
        pdf_bytes=pdf_bytes
    )

    return {
        "status": "sent",
        "message": "Proposal email sent successfully"
    }


## ---------------------------------greeting endpoint
from agents.greeting_agent import generate_greeting

@app.get("/greeting")
def greeting():
    return {
        "message": generate_greeting()
    }
## --------------------------------------------------