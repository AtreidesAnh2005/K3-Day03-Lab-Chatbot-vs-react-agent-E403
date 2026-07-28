"""Tool registry and schemas for the ReAct Agent."""

from tools.date_tools import get_weather, search_date_activities, search_flights, suggest_date_plan
from tools.matching_tools import calculate_compatibility, find_candidate_matches, get_shared_interests
from tools.profile_tools import extract_profile


AVAILABLE_TOOLS = {
    "calculate_compatibility": calculate_compatibility,
    "get_shared_interests": get_shared_interests,
    "search_date_activities": search_date_activities,
    "extract_profile": extract_profile,
    "find_candidate_matches": find_candidate_matches,
    "suggest_date_plan": suggest_date_plan,
    "get_weather": get_weather,
    "search_flights": search_flights,
}
