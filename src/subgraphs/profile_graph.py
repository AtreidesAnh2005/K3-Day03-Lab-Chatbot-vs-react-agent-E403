"""Profile subgraph."""

from agents.profile_agent import run_profile_agent
from multi_agent.state import AgentState


def run_profile_graph(state: AgentState) -> AgentState:
    """Run the profile extraction subgraph."""
    return run_profile_agent(state)
