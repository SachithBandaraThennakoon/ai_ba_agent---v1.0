from langgraph.graph import StateGraph, END
from graph.state import ProposalState
from graph.nodes import ba_node, architect_node, final_proposal_node

def build_proposal_graph():
    graph = StateGraph(ProposalState)

    graph.add_node("ba", ba_node)
    graph.add_node("architect", architect_node)
    graph.add_node("final", final_proposal_node)

    graph.set_entry_point("ba")
    graph.add_edge("ba", "architect")
    graph.add_edge("architect", "final")
    graph.add_edge("final", END)

    return graph.compile()
