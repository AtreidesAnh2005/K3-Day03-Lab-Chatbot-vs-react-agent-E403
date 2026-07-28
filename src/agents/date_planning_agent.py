"""Date planning agent."""

from multi_agent.state import AgentState
from tools.date_tools import suggest_date_plan


def run_date_planning_agent(state: AgentState) -> AgentState:
    """Create a date plan for the best candidate."""
    best_candidate = state.candidates[0] if state.candidates else {}
    state.plan = suggest_date_plan(state.profile, best_candidate)
    state.trace.append("Date planning agent completed")
    return state
