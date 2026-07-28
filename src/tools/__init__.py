"""Tool registry and schemas for the ReAct Agent."""

from tools.date_tools import get_weather, search_flights, suggest_date_plan
from tools.matching_tools import find_candidate_matches
from tools.profile_tools import extract_profile


AVAILABLE_TOOLS = {
    "extract_profile": extract_profile,
    "find_candidate_matches": find_candidate_matches,
    "suggest_date_plan": suggest_date_plan,
    "get_weather": get_weather,
    "search_flights": search_flights,
}
