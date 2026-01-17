from agents.client_agent import client_agent
from agents.ba_agent import ba_agent
from memory.session_memory import SessionMemory

from agents.solution_architect_agent import solution_architect_agent

from agents.final_proposal_agent import final_proposal_agent

from utils.markdown_saver import save_markdown

from graph.proposal_graph import build_proposal_graph

from memory.persistent_memory import PersistentSessionMemory
from uuid import uuid4

from utils.pdf_generator import markdown_to_pdf


if __name__ == "__main__":
    print("=== Client ↔ Client Agent (Discovery Mode) ===")
    print("Type 'CONFIRM' when the understanding is correct.\n")

    session = SessionMemory()
    structured_summary = None

    from vector_db.company_knowledge import ensure_company_knowledge_loaded

    # Ensure company knowledge is available before starting chat
    ensure_company_knowledge_loaded("company_docs")


    while not session.is_confirmed():
        user_input = input("Client: ")
        reply, confirmed = client_agent(session, user_input)
        print(f"\nClient Agent:\n{reply}\n")

        if confirmed:
            structured_summary = reply

    print("\n=== BA Agent Analysis ===\n")
    ba_output = ba_agent(structured_summary)
    print(ba_output)

    print("\n=== Solution Architect Output ===\n")
    architect_output = solution_architect_agent(ba_output)
    print(architect_output)

    print("\n=== Final Proposal ===\n")
    final_output = final_proposal_agent(ba_output, architect_output)
    print(final_output)



    file_path = save_markdown(final_output)
    print(f"\n✅ Proposal saved successfully: {file_path}")


    proposal_graph = build_proposal_graph()

    result = proposal_graph.invoke({
        "client_summary": structured_summary
    })

    final_output = result["final_proposal"]
    print("\n=== FINAL PROPOSAL ===\n")
    print(final_output)

    session_id = str(uuid4())
    session = PersistentSessionMemory(session_id)


    pdf_path = markdown_to_pdf(final_output)
    print(f"\n📄 Proposal PDF generated: {pdf_path}")
