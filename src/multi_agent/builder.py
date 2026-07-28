"""Builder for the multi-agent workflow."""

from multi_agent.dispatcher import dispatch
from multi_agent.state import AgentState
from multi_agent.supervisor import choose_next_route


def run_multi_agent_workflow(user_query: str, max_steps: int = 5) -> AgentState:
    """Run a simple supervisor-dispatcher loop."""
    state = AgentState(user_query=user_query)

    for _ in range(max_steps):
        route = choose_next_route(state)
        state.trace.append(f"Route: {route}")
        state = dispatch(route, state)
        if state.final_answer:
            break

    return state
