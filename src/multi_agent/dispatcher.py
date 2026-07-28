"""Dispatcher that invokes one specialist or subgraph at a time."""

from agents.response_agent import run_response_agent
from agents.safety_critic_agent import run_safety_critic_agent
from multi_agent.routes import RouteName
from multi_agent.state import AgentState
from subgraphs.date_planning_graph import run_date_planning_graph
from subgraphs.matching_graph import run_matching_graph
from subgraphs.profile_graph import run_profile_graph


def dispatch(route: RouteName, state: AgentState) -> AgentState:
    handlers = {
        "profile": run_profile_graph,
        "matching": run_matching_graph,
        "date_planning": run_date_planning_graph,
        "safety_critic": run_safety_critic_agent,
        "response": run_response_agent,
    }
    if route == "done":
        return state
    return handlers[route](state)
