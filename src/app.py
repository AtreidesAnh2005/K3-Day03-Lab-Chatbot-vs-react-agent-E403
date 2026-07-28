"""Core runtime and HTTP API for the Cupid Agent lab.

Run the CLI demo:
    python src/app.py

Run the frontend API:
    python src/app.py --serve
"""

from __future__ import annotations
# 
import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


try:
    from .prompts import (
        CHATBOT_BASELINE_PROMPT,
        MAX_ITERATIONS,
        MAX_REPEATED_ACTIONS,
        REACT_SYSTEM_PROMPT,
        SAFE_FALLBACK_MESSAGE,
    )
    from .providers import get_llm_provider
    from .tools import AVAILABLE_TOOLS
except ImportError:
    from prompts import (  # type: ignore[no-redef]
        CHATBOT_BASELINE_PROMPT,
        MAX_ITERATIONS,
        MAX_REPEATED_ACTIONS,
        REACT_SYSTEM_PROMPT,
        SAFE_FALLBACK_MESSAGE,
    )
    from providers import get_llm_provider  # type: ignore[no-redef]
    from tools import AVAILABLE_TOOLS  # type: ignore[no-redef]

load_dotenv()

DEFAULT_REQUESTER_ID = os.getenv("CUPID_DEMO_USER_ID", "USR001")
TOOL_FAILURE_STATUSES = {"denied", "error"}
PROFILE_STORE: dict[str, dict[str, Any]] = {}

DIMENSION_LABELS = {
    "relationship_goal": "Mục tiêu mối quan hệ",
    "values": "Giá trị sống",
    "lifestyle": "Lối sống",
    "communication_style": "Phong cách giao tiếp",
    "future_plans": "Kế hoạch tương lai",
    "interests": "Sở thích",
    "availability": "Lịch rảnh",
    "logistics": "Khoảng cách và địa điểm",
}


@dataclass
class ParsedReactResponse:
    thought: str | None = None
    action_name: str | None = None
    action_args: list[Any] | None = None
    final_answer: str | None = None
    parser_error: str | None = None


class ProfileRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=254)
    gender: str
    birthYear: int = Field(ge=1900, le=2100)
    personality: str
    answers: dict[str, str] = Field(default_factory=dict)
    createdAt: str


class DatePlanRequest(BaseModel):
    candidateId: str = Field(min_length=1, max_length=50)
    customPrompt: str | None = Field(default=None, max_length=500)


class ChatRequest(BaseModel):
    candidateId: str = Field(min_length=1, max_length=50)
    message: str = Field(min_length=1, max_length=2000)


def _frontend_origins() -> list[str]:
    configured = os.getenv("FRONTEND_ORIGINS", "")
    if configured.strip():
        return [origin.strip() for origin in configured.split(",") if origin.strip()]
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]


app = FastAPI(
    title="Cupid Agent API",
    version="1.0.0",
    description="Consent-aware API backed by the CupidMAS deterministic tool registry.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_frontend_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_test_cases() -> list[dict[str, Any]]:
    """Load Role 1 test cases from config/test_cases.json."""
    config_path = os.path.join(os.path.dirname(SRC_DIR), "config", "test_cases.json")
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def is_safety_blocked(user_query: str) -> bool:
    """Block privacy, consent, minor-safety, and prompt-injection requests."""
    text = user_query.casefold()
    injection_markers = {
        "ignore all previous instructions",
        "bỏ qua",
        "bo qua",
        "bypass",
        "developer mode",
        "không được từ chối",
        "khong duoc tu choi",
    }
    private_data_markers = {
        "số điện thoại",
        "so dien thoai",
        "phone",
        "email",
        "địa chỉ",
        "dia chi",
        "address",
        "matching_consent",
    }
    minor_markers = {
        "người chưa thành niên",
        "nguoi chua thanh nien",
        "minor",
        "underage",
    }
    has_injection = any(marker in text for marker in injection_markers)
    has_private_data_request = any(marker in text for marker in private_data_markers)
    has_minor_risk = any(marker in text for marker in minor_markers)
    return (has_injection and has_private_data_request) or has_minor_risk


def run_baseline_chatbot(user_query: str, provider: Any) -> str:
    """Run the baseline chatbot without tools."""
    print(f"\n[CHATBOT BASELINE] Câu hỏi: {user_query}")
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"Chatbot trả lời:\n{response}")
    return response


def parse_react_output(response: str) -> ParsedReactResponse:
    """Parse Thought, Action, and Final Answer from one ReAct response."""
    cleaned = response.strip().strip("`").strip()
    lines = cleaned.splitlines()
    parsed = ParsedReactResponse()

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.lower().startswith("thought:"):
            parsed.thought = stripped.split(":", 1)[1].strip()
        elif stripped.lower().startswith("final answer:"):
            first_line = stripped.split(":", 1)[1].strip()
            tail = "\n".join(lines[index + 1 :]).strip()
            parsed.final_answer = f"{first_line}\n{tail}".strip()
            return parsed
        elif stripped.lower().startswith("action:"):
            action_text = stripped.split(":", 1)[1].strip()
            match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\[(.*)\]", action_text)
            if not match:
                parsed.parser_error = f"Action không đúng format: {action_text}"
                return parsed

            parsed.action_name = match.group(1)
            raw_args = match.group(2).strip()
            try:
                parsed.action_args = json.loads(f"[{raw_args}]") if raw_args else []
            except json.JSONDecodeError as exc:
                parsed.parser_error = f"Action arguments không phải JSON hợp lệ: {exc}"
            return parsed

    parsed.parser_error = "Không tìm thấy Action hoặc Final Answer trong response."
    return parsed


def _normalize_user_id(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    match = re.fullmatch(r"U(\d{3})", value.strip(), flags=re.IGNORECASE)
    return f"USR{match.group(1)}" if match else value


def _normalize_city(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    aliases = {
        "hanoi": "Ha Noi",
        "hà nội": "Ha Noi",
        "ho chi minh": "Ho Chi Minh City",
        "tp.hcm": "Ho Chi Minh City",
        "hồ chí minh": "Ho Chi Minh City",
    }
    return aliases.get(value.strip().casefold(), value)


def _normalize_tool_arguments(
    tool_name: str,
    arguments: list[Any] | dict[str, Any],
) -> list[Any] | dict[str, Any]:
    user_keys = {"user_id", "candidate_id", "user_a_id", "user_b_id", "requester_id"}

    if isinstance(arguments, dict):
        normalized = dict(arguments)
        for key in user_keys:
            if key in normalized:
                normalized[key] = _normalize_user_id(normalized[key])
        if "city" in normalized:
            normalized["city"] = _normalize_city(normalized["city"])
        return normalized

    normalized_list = list(arguments)
    user_positions = {
        "get_match_profile": {0, 1},
        "check_profile_completeness": {0},
        "check_matching_eligibility": {0, 1},
        "search_candidates": {0},
        "calculate_compatibility": {0, 1},
        "get_compatibility_breakdown": {0, 1},
        "get_shared_interests": {0, 1},
    }
    for index in user_positions.get(tool_name, set()):
        if index < len(normalized_list):
            normalized_list[index] = _normalize_user_id(normalized_list[index])
    if tool_name == "search_date_activities" and normalized_list:
        normalized_list[0] = _normalize_city(normalized_list[0])
    return normalized_list


def execute_tool(
    tool_name: str,
    arguments: list[Any] | dict[str, Any],
) -> dict[str, Any]:
    """Dispatch one registered tool and preserve its structured result."""
    tool = AVAILABLE_TOOLS.get(tool_name)
    if tool is None:
        return {
            "ok": False,
            "error_type": "unknown_tool",
            "message": f"Tool '{tool_name}' không tồn tại trong AVAILABLE_TOOLS.",
        }

    normalized = _normalize_tool_arguments(tool_name, arguments)
    try:
        output = tool(**normalized) if isinstance(normalized, dict) else tool(*normalized)
    except (TypeError, ValueError) as exc:
        return {
            "ok": False,
            "error_type": "invalid_arguments",
            "tool": tool_name,
            "message": str(exc),
        }
    except Exception as exc:
        return {
            "ok": False,
            "error_type": "tool_exception",
            "tool": tool_name,
            "message": str(exc),
        }

    status = output.get("status") if isinstance(output, dict) else None
    ok = status not in TOOL_FAILURE_STATUSES
    observation = {
        "ok": ok,
        "tool": tool_name,
        "arguments": normalized,
        "output": output,
    }
    if not ok and isinstance(output, dict):
        error = output.get("error") or {}
        observation["error_type"] = str(error.get("code", status or "tool_error"))
        observation["message"] = str(error.get("message", "Tool execution failed."))
    return observation


def render_observation(observation: dict[str, Any]) -> str:
    """Serialize an Observation for the console and the next LLM call."""
    return json.dumps(observation, ensure_ascii=False, indent=2)


def run_react_agent(user_query: str, provider: Any) -> str:
    """Run a guarded Thought -> Action -> Observation -> Final Answer loop."""
    print(f"\n[REACT AGENT] Câu hỏi: {user_query}")

    if is_safety_blocked(user_query):
        print("GUARDRAIL: blocked before tool use.")
        print(f"Final Answer: {SAFE_FALLBACK_MESSAGE}")
        return SAFE_FALLBACK_MESSAGE

    conversation = f"User request: {user_query}"
    action_history: dict[str, int] = {}

    for step in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- ReAct Step {step}/{MAX_ITERATIONS} ---")
        response = provider.generate(conversation, system_prompt=REACT_SYSTEM_PROMPT)
        print(response)

        parsed = parse_react_output(response)
        if parsed.parser_error:
            print(f"Parser Error: {parsed.parser_error}")
            return SAFE_FALLBACK_MESSAGE
        if parsed.final_answer:
            return parsed.final_answer
        if not parsed.action_name or parsed.action_args is None:
            return SAFE_FALLBACK_MESSAGE

        normalized_args = _normalize_tool_arguments(parsed.action_name, parsed.action_args)
        action_key = json.dumps(
            {"tool": parsed.action_name, "args": normalized_args},
            ensure_ascii=False,
            sort_keys=True,
        )
        action_history[action_key] = action_history.get(action_key, 0) + 1
        if action_history[action_key] > MAX_REPEATED_ACTIONS:
            print("GUARDRAIL: repeated action detected.")
            return SAFE_FALLBACK_MESSAGE

        observation = execute_tool(parsed.action_name, parsed.action_args)
        observation_text = render_observation(observation)
        print(f"Observation:\n{observation_text}")

        if not observation.get("ok"):
            print("GUARDRAIL: tool denied or failed.")
            return SAFE_FALLBACK_MESSAGE

        conversation = (
            f"{conversation}\n\n"
            f"Assistant response:\n{response}\n\n"
            f"Observation:\n{observation_text}\n\n"
            "Continue the ReAct protocol. Use Final Answer if you have enough evidence."
        )

    print(f"GUARDRAIL: max iterations reached ({MAX_ITERATIONS}).")
    return SAFE_FALLBACK_MESSAGE


def should_use_react(test_case: dict[str, Any]) -> bool:
    """Route test cases based on Role 1 metadata."""
    expected_path = str(test_case.get("expected_path", "")).lower()
    return bool(test_case.get("requires_tools")) or expected_path in {
        "react_agent",
        "safety_guardrail",
    }


def _tool_data(tool_name: str, arguments: dict[str, Any]) -> Any:
    observation = execute_tool(tool_name, arguments)
    if not observation.get("ok"):
        status_code = 403 if observation.get("error_type") in {
            "CONSENT_NOT_FOUND",
            "CONSENT_REVOKED",
            "PERMISSION_DENIED",
            "PROFILE_ACCESS_DENIED",
        } else 400
        raise HTTPException(
            status_code=status_code,
            detail={
                "tool": tool_name,
                "code": observation.get("error_type", "TOOL_ERROR"),
                "message": observation.get("message", "Tool execution failed."),
            },
        )
    output = observation.get("output")
    if not isinstance(output, dict) or "data" not in output:
        raise HTTPException(status_code=500, detail=f"{tool_name} returned an invalid envelope.")
    return output["data"]


def _candidate_personality(profile: dict[str, Any]) -> str:
    interests = set(profile.get("interests") or [])
    communication = profile.get("communication_style")
    if interests & {"art", "music", "cinema", "photography"}:
        return "creative"
    if interests & {"travel", "cycling", "walking"}:
        return "adventurous"
    if communication == "direct":
        return "analytical"
    if communication == "gentle":
        return "introvert"
    return "ambivert"


def _candidate_api_model(candidate_id: str) -> dict[str, Any] | None:
    score = _tool_data(
        "calculate_compatibility",
        {"user_id": DEFAULT_REQUESTER_ID, "candidate_id": candidate_id},
    )
    if not score.get("eligible") or not score.get("score_available"):
        return None

    profile_data = _tool_data(
        "get_match_profile",
        {"user_id": candidate_id, "requester_id": DEFAULT_REQUESTER_ID},
    )
    breakdown = _tool_data(
        "get_compatibility_breakdown",
        {"user_id": DEFAULT_REQUESTER_ID, "candidate_id": candidate_id},
    )
    profile = profile_data["profile"]

    reasons = [
        f"{DIMENSION_LABELS.get(item.get('dimension'), item.get('dimension', 'Tiêu chí'))} phù hợp"
        for item in breakdown.get("strengths", [])
    ]
    if not reasons:
        reasons = ["Điểm được tính từ dữ liệu hai bên đã đồng ý chia sẻ"]
    reasons.append("Điểm tương thích chỉ là ước lượng, không bảo đảm kết quả mối quan hệ")

    display_name = profile.get("display_name") or candidate_id
    city = profile.get("city") or "Chưa chia sẻ"
    goal = profile.get("relationship_goal")
    bio = f"{display_name} sống tại {city}."
    if goal:
        bio += f" Mục tiêu mối quan hệ đã chia sẻ: {goal}."

    return {
        "id": candidate_id,
        "name": display_name,
        "age": profile.get("age") or 18,
        "city": city,
        "careerField": "",
        "loveLanguage": "",
        "personality": _candidate_personality(profile),
        "photo": "",
        "bio": bio,
        "interests": profile.get("interests") or [],
        "compatibility": score["score"],
        "reasons": reasons[:3],
    }


@app.get("/api/health")
def api_health() -> dict[str, Any]:
    return {
        "status": "ok",
        "provider": get_llm_provider().__class__.__name__,
        "toolCount": len(AVAILABLE_TOOLS),
        "demoUserId": DEFAULT_REQUESTER_ID,
    }


@app.get("/api/tools")
def api_tools() -> dict[str, Any]:
    return {"tools": sorted(AVAILABLE_TOOLS), "count": len(AVAILABLE_TOOLS)}


@app.post("/api/profile")
def api_submit_profile(profile: ProfileRequest) -> dict[str, Any]:
    PROFILE_STORE[profile.email.casefold()] = profile.model_dump()
    return {
        "success": True,
        "profileId": DEFAULT_REQUESTER_ID,
        "mode": "demo_fixture",
    }


@app.get("/api/matches")
def api_matches(
    email: str = Query(default="", max_length=254),
) -> list[dict[str, Any]]:
    del email  # The lab maps signed-in frontend users to the consented demo fixture.
    search = _tool_data(
        "search_candidates",
        {"user_id": DEFAULT_REQUESTER_ID, "max_results": 10},
    )
    candidates: list[dict[str, Any]] = []
    for row in search.get("candidates", []):
        candidate = _candidate_api_model(row["candidate_id"])
        if candidate is not None:
            candidates.append(candidate)
    return sorted(candidates, key=lambda item: item["compatibility"], reverse=True)


def _date_plan_indoor_preference(custom_prompt: str | None) -> bool | None:
    text = (custom_prompt or "").casefold()
    if any(marker in text for marker in {"ngoài trời", "ngoai troi", "outdoor"}):
        return False
    if any(marker in text for marker in {"trong nhà", "trong nha", "indoor"}):
        return True
    return None


@app.post("/api/date-plan")
def api_date_plan(request: DatePlanRequest) -> dict[str, Any]:
    candidate_id = _normalize_user_id(request.candidateId)
    profile_data = _tool_data(
        "get_match_profile",
        {"user_id": candidate_id, "requester_id": DEFAULT_REQUESTER_ID},
    )
    shared = _tool_data(
        "get_shared_interests",
        {"user_a_id": DEFAULT_REQUESTER_ID, "user_b_id": candidate_id},
    )
    requester = _tool_data(
        "get_match_profile",
        {"user_id": DEFAULT_REQUESTER_ID},
    )

    candidate_profile = profile_data["profile"]
    requester_profile = requester["profile"]
    city = candidate_profile.get("city") or requester_profile.get("city") or "Ha Noi"
    max_budget = (
        requester_profile.get("date_preferences", {}).get("max_budget")
        or 500000
    )
    activities = _tool_data(
        "search_date_activities",
        {
            "city": city,
            "interests": shared.get("shared_interests", []),
            "max_budget": max_budget,
            "indoor": _date_plan_indoor_preference(request.customPrompt),
            "max_results": 3,
        },
    )

    rows = activities.get("activities", [])
    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Không có hoạt động phù hợp với bộ lọc hiện tại.",
        )

    times = ["17:30 - 18:45", "19:00 - 20:30", "20:45 - 21:45"]
    items = []
    for index, activity in enumerate(rows):
        cost = activity["estimated_pair_cost"]
        items.append(
            {
                "step": index + 1,
                "time": times[index],
                "title": activity["name"],
                "location": activity["city"],
                "description": (
                    f"Chi phí ước tính {cost:,} VND cho hai người, "
                    f"thời lượng khoảng {activity['duration_minutes']} phút. "
                    "Đây là đề xuất, hệ thống chưa đặt chỗ."
                ),
                "tag": "Trong nhà" if activity["indoor"] else "Ngoài trời",
            }
        )

    shared_interests = shared.get("shared_interests", [])
    topics = shared_interests[:3] or ["một ngày lý tưởng", "sở thích cuối tuần", "ẩm thực"]
    questions = [f"Bạn thích điều gì nhất ở chủ đề {topic}?" for topic in topics]

    return {
        "candidateName": candidate_profile.get("display_name") or candidate_id,
        "theme": f"Kế hoạch hẹn hò an toàn tại {city}",
        "items": items,
        "icebreakerQuestions": questions,
    }


@app.post("/api/chat")
def api_chat(request: ChatRequest) -> dict[str, Any]:
    if is_safety_blocked(request.message):
        return {
            "reply": SAFE_FALLBACK_MESSAGE,
            "suggestedTopics": ["Gửi lời mời kết nối trong ứng dụng"],
            "safetyApproved": False,
        }

    candidate_id = _normalize_user_id(request.candidateId)
    _tool_data(
        "get_match_profile",
        {"user_id": candidate_id, "requester_id": DEFAULT_REQUESTER_ID},
    )
    reply = run_baseline_chatbot(request.message, get_llm_provider())
    return {
        "reply": reply,
        "suggestedTopics": ["Sở thích chung", "Ranh giới cá nhân", "Kế hoạch cuối tuần"],
        "safetyApproved": True,
    }


def run_cli_demo() -> None:
    print("==================================================")
    print("VINUNI LAB 3: CHATBOT VS REACT AGENT - CUPID AGENT")
    print("==================================================")

    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"LLM Provider: {provider.__class__.__name__} (Model: {model_name})")

    tests = load_test_cases()
    print(f"Loaded {len(tests)} test cases from config/test_cases.json")
    for test_case in tests:
        print("\n==================================================")
        print(f"Test Case: {test_case.get('id')} - {test_case.get('name')}")
        query = test_case["question"]
        if should_use_react(test_case):
            run_react_agent(query, provider)
        else:
            run_baseline_chatbot(query, provider)


def main() -> None:
    parser = argparse.ArgumentParser(description="Cupid Agent runtime")
    parser.add_argument("--serve", action="store_true", help="Run the FastAPI server")
    parser.add_argument("--host", default=os.getenv("API_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("API_PORT", "8000")))
    args = parser.parse_args()

    if args.serve:
        import uvicorn

        uvicorn.run(app, host=args.host, port=args.port)
        return
    run_cli_demo()


if __name__ == "__main__":
    main()
