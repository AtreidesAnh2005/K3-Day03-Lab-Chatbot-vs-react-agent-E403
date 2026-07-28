"""Date planning tools and legacy demo tools."""


def suggest_date_plan(profile: dict, candidate: dict) -> dict:
    """Suggest a simple date plan based on profile and candidate data."""
    return {
        "idea": "Cafe yen tinh de tro chuyen va tim hieu nhau",
        "location": "Quan cafe trung tam",
        "safety_note": "Gap o noi cong cong va tu bao quan thong tin ca nhan.",
    }


def search_date_activities(city: str, interests: list[str], max_budget: int) -> dict:
    """Search fixture-backed activities through the tool registry."""
    from . import search_date_activities as registry_search_date_activities

    result = registry_search_date_activities(city, interests, max_budget)
    if result.get("status") not in {"success", "warning"}:
        error = result.get("error") or {}
        return {
            "activities": [],
            "error": error.get("message", "Activity search failed."),
        }
    return {"activities": (result.get("data") or {}).get("activities", [])}


def get_weather(location: str) -> str:
    """
    Look up current weather for a city.

    Kept for compatibility with the original lab examples.
    """
    loc_lower = location.lower()
    if "ha noi" in loc_lower or "hà nội" in loc_lower:
        return "Thoi tiet Ha Noi: 28°C, Nang nhe, Do am 65%."
    if "ho chi minh" in loc_lower or "hồ chí minh" in loc_lower or "tp.hcm" in loc_lower or "hcm" in loc_lower:
        return "Thoi tiet TP.HCM: 33°C, Nang nong, Co may."
    if "da nang" in loc_lower or "đà nẵng" in loc_lower:
        return "Thoi tiet Da Nang: 30°C, Gio nhe, Mat me."
    return f"LOI: Khong tim thay du lieu thoi tiet cho dia diem '{location}'."


def search_flights(origin: str, destination: str) -> str:
    """
    Look up flights between two locations.

    Kept for compatibility with the original lab examples.
    """
    return (
        f"Chuyen bay tu {origin} -> {destination} ngay mai:\n"
        "1. VN123 (08:00) - Gia: 1,500,000 VND (Con ve)\n"
        "2. VJ456 (14:30) - Gia: 1,200,000 VND (Con ve)"
    )
