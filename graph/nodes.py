from agents.ba_agent import ba_agent
from agents.solution_architect_agent import solution_architect_agent
from agents.final_proposal_agent import final_proposal_agent

def ba_node(state):
    state["ba_output"] = ba_agent(state["client_summary"])
    return state

def architect_node(state):
    state["architect_output"] = solution_architect_agent(state["ba_output"])
    return state

def final_proposal_node(state):
    state["final_proposal"] = final_proposal_agent(
        state["ba_output"],
        state["architect_output"]
    )
    return state
