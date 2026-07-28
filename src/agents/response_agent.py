"""Final response agent."""

from multi_agent.state import AgentState


def run_response_agent(state: AgentState) -> AgentState:
    """Compose the final user-facing answer."""
    candidate_name = state.candidates[0].get("name", "ung vien phu hop") if state.candidates else "ung vien phu hop"
    date_idea = state.plan.get("idea", "mot buoi gap nhe nhang") if state.plan else "mot buoi gap nhe nhang"
    state.final_answer = (
        f"Goi y match tot nhat hien tai la {candidate_name}. "
        f"Ke hoach hen ho phu hop: {date_idea}."
    )
    state.trace.append("Response agent completed")
    return state
