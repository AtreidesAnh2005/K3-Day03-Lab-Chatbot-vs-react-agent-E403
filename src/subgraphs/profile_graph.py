"""Profile specialist subgraph."""

from agents.profile_agent import run_profile_agent
from multi_agent.state import AgentState


def run_profile_graph(state: AgentState) -> AgentState:
    state.record("profile_graph", "started")
    state = run_profile_agent(state)
    state.record("profile_graph", "completed")
    return state
