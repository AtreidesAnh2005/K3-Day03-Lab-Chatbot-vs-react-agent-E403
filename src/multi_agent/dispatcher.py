"""Dispatcher for routing state to the selected agent."""

from agents.date_planning_agent import run_date_planning_agent
from agents.matching_agent import run_matching_agent
from agents.profile_agent import run_profile_agent
from agents.response_agent import run_response_agent
from agents.safety_critic_agent import run_safety_critic_agent
from multi_agent.routes import RouteName
from multi_agent.state import AgentState


def dispatch(route: RouteName, state: AgentState) -> AgentState:
    """Run one agent based on the supervisor route."""
    handlers = {
        "profile": run_profile_agent,
        "matching": run_matching_agent,
        "date_planning": run_date_planning_agent,
        "safety_critic": run_safety_critic_agent,
        "response": run_response_agent,
    }
    return handlers[route](state)
