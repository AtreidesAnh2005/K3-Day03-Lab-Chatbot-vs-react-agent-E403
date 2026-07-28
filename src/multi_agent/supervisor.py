"""Supervisor logic for deciding which agent should handle the next step."""

from multi_agent.routes import RouteName
from multi_agent.state import AgentState


def choose_next_route(state: AgentState) -> RouteName:
    """Choose the next route from the current state."""
    if not state.profile:
        return "profile"
    if not state.candidates:
        return "matching"
    if not state.plan:
        return "date_planning"
    return "response"
