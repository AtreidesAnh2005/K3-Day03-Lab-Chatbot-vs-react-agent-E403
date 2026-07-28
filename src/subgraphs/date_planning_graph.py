"""Date planning subgraph."""

from agents.date_planning_agent import run_date_planning_agent
from multi_agent.state import AgentState


def run_date_planning_graph(state: AgentState) -> AgentState:
    """Run the date planning subgraph."""
    return run_date_planning_agent(state)
