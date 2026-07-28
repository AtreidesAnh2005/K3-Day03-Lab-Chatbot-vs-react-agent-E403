"""Date planning specialist subgraph."""

from agents.date_planning_agent import run_date_planning_agent
from multi_agent.state import AgentState


def run_date_planning_graph(state: AgentState) -> AgentState:
    state.record("date_planning_graph", "started")
    state = run_date_planning_agent(state)
    state.record("date_planning_graph", "completed")
    return state
