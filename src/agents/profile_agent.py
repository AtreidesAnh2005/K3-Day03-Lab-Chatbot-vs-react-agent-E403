"""Profile specialist agent."""

from multi_agent.state import AgentState
from multi_agent.tool_executor import call_tool


def run_profile_agent(state: AgentState) -> AgentState:
    agent = "profile"
    state.record(agent, "started")
    profile_data = call_tool(state, agent, "get_match_profile", user_id=state.user_id)
    completeness = call_tool(
        state,
        agent,
        "check_profile_completeness",
        user_id=state.user_id,
        purpose="matching",
    )
    if profile_data:
        state.profile = profile_data.get("profile") or {}
    state.output = {
        "success": not state.errors,
        "profileId": state.user_id,
        "mode": "consented_dataset",
        "profile": state.profile,
        "completeness": completeness or {},
    }
    state.record(agent, "completed", {"profile_id": state.user_id})
    state.complete(agent)
    return state
