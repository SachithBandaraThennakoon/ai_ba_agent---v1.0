import base64
import os
from azure.communication.email import EmailClient

email_client = EmailClient.from_connection_string(
    os.getenv("ACS_CONNECTION_STRING")
)

SENDER = os.getenv("ACS_SENDER_EMAIL")

def send_proposal_email(to_email: str, pdf_bytes: bytes):
    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

    message = {
        "senderAddress": SENDER,
        "recipients": {
            "to": [{"address": to_email}]
        },
        "content": {
            "subject": "Xceed | AI & Data Solution Proposal",
            "plainText": (
                "Dear Client,\n\n"
                "Thank you for the opportunity to understand your business needs.\n\n"
                "Please find attached the detailed proposal prepared by Xceed.\n\n"
                "We look forward to discussing next steps.\n\n"
                "Best regards,\n"
                "Xceed Team\n"
                "Empowering Humans & Businesses to Exceed"
            )
        },
        "attachments": [
            {
                "name": "Xceed_Proposal.pdf",
                "contentType": "application/pdf",
                "contentInBase64": encoded_pdf
            }
        ]
    }

    poller = email_client.begin_send(message)
    poller.result()
