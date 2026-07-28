"""Matching specialist subgraph."""

from agents.matching_agent import run_matching_agent
from multi_agent.state import AgentState


def run_matching_graph(state: AgentState) -> AgentState:
    state.record("matching_graph", "started")
    state = run_matching_agent(state)
    state.record("matching_graph", "completed")
    return state
