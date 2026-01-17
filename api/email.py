from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.email_service import send_proposal_email
from memory.persistent_memory import PersistentSessionMemory

router = APIRouter()

class EmailRequest(BaseModel):
    session_id: str
    email: str

@router.post("/send-email")
def send_email(req: EmailRequest):
    session = PersistentSessionMemory(req.session_id)
    proposal = session.get_final_proposal()

    if not proposal:
        raise HTTPException(status_code=400, detail="Final proposal not found")


    html = f"""
    <html>
      <body style="font-family:Arial">
        <h2>Xceed – Proposal</h2>
        <pre>{proposal}</pre>
      </body>
    </html>
    """

    msg_id = send_proposal_email(
        to_email=req.email,
        subject="Your Proposal from Xceed",
        html_content=html
    )

    return {"status": "sent", "message_id": msg_id}
