"""Matching subgraph."""

from agents.matching_agent import run_matching_agent
from multi_agent.state import AgentState


def run_matching_graph(state: AgentState) -> AgentState:
    """Run the candidate matching subgraph."""
    return run_matching_agent(state)
