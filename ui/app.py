import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Xceed AI Pre-Sales Agent", layout="centered")

st.title("🚀 Xceed AI Pre-Sales Assistant")
st.caption("Empowering Humans & Businesses to Exceed")

# ----------------------------------
# STATE
# ----------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "chat" not in st.session_state:
    st.session_state.chat = []

if "confirmed" not in st.session_state:
    st.session_state.confirmed = False

# ----------------------------------
# INPUT
# ----------------------------------
user_input = st.text_input(
    "You",
    placeholder="Ask about services, AI, BI, or describe your business problem"
)

if st.button("Send") and user_input:
    payload = {
        "message": user_input,
        "session_id": st.session_state.session_id
    }

    try:
        response = requests.post(f"{API_URL}/chat", json=payload).json()
    except Exception as e:
        st.error(f"Backend not reachable: {e}")
        st.stop()

    st.session_state.session_id = response["session_id"]
    st.session_state.confirmed = response.get("confirmed", False)

    st.session_state.chat.append(("Client", user_input))
    st.session_state.chat.append(("Xceed AI", response["reply"]))

# ----------------------------------
# CHAT DISPLAY
# ----------------------------------
for role, msg in st.session_state.chat:
    if role == "Client":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Xceed AI:** {msg}")

# ----------------------------------
# CONFIRM INFO
# ----------------------------------
if st.session_state.confirmed:
    st.success("✅ Discovery confirmed. You can generate the proposal.")

# ----------------------------------
# PROPOSAL
# ----------------------------------
if st.session_state.confirmed and st.button("Generate Proposal"):
    res = requests.post(
        f"{API_URL}/generate-proposal",
        params={"session_id": st.session_state.session_id}
    ).json()

    if "final_proposal" in res:
        st.markdown("---")
        st.subheader("📄 Final Proposal (Markdown)")
        st.markdown(res["final_proposal"])
    else:
        st.error(res.get("error", "Unable to generate proposal"))
