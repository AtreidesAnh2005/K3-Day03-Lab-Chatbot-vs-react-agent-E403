"""Core runtime and HTTP API for the Cupid Agent lab.

Run the CLI demo:
    python src/app.py

Run the frontend API:
    python src/app.py --serve
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
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
    from .multi_agent.builder import run_multi_agent_workflow
    from .observability.langfuse_config import build_trace_summary
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
    from multi_agent.builder import run_multi_agent_workflow  # type: ignore[no-redef]
    from observability.langfuse_config import build_trace_summary  # type: ignore[no-redef]
    from providers import get_llm_provider  # type: ignore[no-redef]
    from tools import AVAILABLE_TOOLS  # type: ignore[no-redef]

load_dotenv()

DEFAULT_REQUESTER_ID = os.getenv("CUPID_DEMO_USER_ID", "USR001")
TOOL_FAILURE_STATUSES = {"denied", "error"}
PROFILE_STORE: dict[str, dict[str, Any]] = {}
AGENT_RUNS: dict[str, dict[str, Any]] = {}

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
    return value.strip()


def _normalize_city(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    aliases = {
        "hanoi": "Hanoi",
        "ha noi": "Hanoi",
        "hà nội": "Hanoi",
        "ho chi minh": "Ho Chi Minh City",
        "ho chi minh city": "Ho Chi Minh City",
        "tp.hcm": "Ho Chi Minh City",
        "hồ chí minh": "Ho Chi Minh City",
    }
    return aliases.get(value.strip().casefold(), value.strip())


def _fold_text(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value.casefold())
    return "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )


def _is_date_planning_chat(message: str) -> bool:
    text = _fold_text(message)
    direct_markers = {
        "date plan",
        "date planning",
        "lap ke hoach hen",
        "ke hoach hen",
        "lich trinh hen",
        "goi y buoi hen",
        "buoi hen",
        "hen ho",
        "itinerary",
    }
    context_markers = {
        "ngoai troi",
        "trong nha",
        "cuoi tuan",
        "toi nay",
        "ngan sach",
        "budget",
        "dia diem",
        "cafe",
        "ca phe",
        "an toi",
        "workshop",
        "trien lam",
        "bao tang",
    }
    return any(marker in text for marker in direct_markers) or (
        "hen" in text and any(marker in text for marker in context_markers)
    )


def _extract_chat_city(message: str) -> str | None:
    text = _fold_text(message)
    if "ha noi" in text or "hanoi" in text:
        return "Hanoi"
    if any(marker in text for marker in {"ho chi minh", "tp hcm", "tphcm", "sai gon", "saigon"}):
        return "Ho Chi Minh City"
    if "da nang" in text:
        return "Da Nang"
    return None


def _extract_chat_budget(message: str) -> int | None:
    text = _fold_text(message).replace("đ", "d")
    million_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:trieu|tr|m)\b", text)
    if million_match:
        return int(float(million_match.group(1).replace(",", ".")) * 1_000_000)

    thousand_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:k|nghin|ngan)\b", text)
    if thousand_match:
        return int(float(thousand_match.group(1).replace(",", ".")) * 1_000)

    amount_match = re.search(r"\b(\d{1,3}(?:[.,]\d{3})+|\d{5,})\s*(?:vnd|dong|d)?\b", text)
    if amount_match:
        return int(re.sub(r"[.,]", "", amount_match.group(1)))
    return None


def _format_date_plan_chat_reply(output: dict[str, Any]) -> str:
    items = output.get("items") or []
    questions = output.get("icebreakerQuestions") or []
    if not items:
        return (
            "Date Planning Agent chưa tìm được lịch trình đủ dữ liệu đã consent. "
            "Bạn có thể thử lại với ngân sách, thành phố hoặc kiểu không gian cụ thể hơn."
        )

    lines = [
        f"Date Planning Agent đề xuất: {output.get('theme') or 'kế hoạch hẹn hò an toàn'}",
        "",
    ]
    for item in items:
        lines.append(
            (
                f"{item.get('step')}. {item.get('time')} - {item.get('title')} "
                f"({item.get('location')}): {item.get('description')}"
            )
        )
    if questions:
        lines.extend(["", "Câu hỏi phá băng:"])
        lines.extend(f"- {question}" for question in questions)
    return "\n".join(lines)


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


def _finalize_safe_fallback(*, safety_verdict: str | None = None) -> str:
    print(f"Final Answer: {SAFE_FALLBACK_MESSAGE}")
    if safety_verdict:
        print(f"Safety Verdict: {safety_verdict}")
    return SAFE_FALLBACK_MESSAGE


def run_react_agent(user_query: str, provider: Any) -> str:
    """Run a guarded Thought -> Action -> Observation -> Final Answer loop."""
    print(f"\n[REACT AGENT] Câu hỏi: {user_query}")

    if is_safety_blocked(user_query):
        print("GUARDRAIL: blocked before tool use.")
        return _finalize_safe_fallback(safety_verdict="BLOCK")

    conversation = f"User request: {user_query}"
    action_history: dict[str, int] = {}

    for step in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- ReAct Step {step}/{MAX_ITERATIONS} ---")
        response = provider.generate(conversation, system_prompt=REACT_SYSTEM_PROMPT)
        print(response)

        parsed = parse_react_output(response)
        if parsed.parser_error:
            print(f"Parser Error: {parsed.parser_error}")
            return _finalize_safe_fallback()
        if parsed.final_answer:
            return parsed.final_answer
        if not parsed.action_name or parsed.action_args is None:
            print("GUARDRAIL: response did not contain a valid action.")
            return _finalize_safe_fallback()

        normalized_args = _normalize_tool_arguments(parsed.action_name, parsed.action_args)
        action_key = json.dumps(
            {"tool": parsed.action_name, "args": normalized_args},
            ensure_ascii=False,
            sort_keys=True,
        )
        action_history[action_key] = action_history.get(action_key, 0) + 1
        if action_history[action_key] > MAX_REPEATED_ACTIONS:
            print("GUARDRAIL: repeated action detected.")
            return _finalize_safe_fallback()

        observation = execute_tool(parsed.action_name, parsed.action_args)
        observation_text = render_observation(observation)
        print(f"Observation:\n{observation_text}")

        if not observation.get("ok"):
            print("GUARDRAIL: tool denied or failed.")
            return _finalize_safe_fallback()

        conversation = (
            f"{conversation}\n\n"
            f"Assistant response:\n{response}\n\n"
            f"Observation:\n{observation_text}\n\n"
            "Continue the ReAct protocol. Use Final Answer if you have enough evidence."
        )

    print(f"GUARDRAIL: max iterations reached ({MAX_ITERATIONS}).")
    return _finalize_safe_fallback()


def should_use_react(test_case: dict[str, Any]) -> bool:
    """Route test cases based on Role 1 metadata."""
    expected_path = str(test_case.get("expected_path", "")).lower()
    return bool(test_case.get("requires_tools")) or expected_path in {
        "react_agent",
        "safety_guardrail",
    }


@app.get("/api/health")
def api_health() -> dict[str, Any]:
    return {
        "status": "ok",
        "provider": get_llm_provider().__class__.__name__,
        "toolCount": len(AVAILABLE_TOOLS),
        "demoUserId": DEFAULT_REQUESTER_ID,
        "multiAgent": True,
    }


@app.get("/api/tools")
def api_tools() -> dict[str, Any]:
    return {"tools": sorted(AVAILABLE_TOOLS), "count": len(AVAILABLE_TOOLS)}


def _run_api_workflow(**kwargs: Any) -> Any:
    state = run_multi_agent_workflow(user_id=DEFAULT_REQUESTER_ID, **kwargs)
    AGENT_RUNS[state.request_id] = build_trace_summary(state.to_dict())
    while len(AGENT_RUNS) > 20:
        AGENT_RUNS.pop(next(iter(AGENT_RUNS)))
    return state


def _raise_workflow_error(state: Any) -> None:
    if not state.errors:
        return
    error = state.errors[0]
    denied_codes = {
        "CONSENT_NOT_FOUND",
        "CONSENT_REVOKED",
        "PERMISSION_DENIED",
        "PROFILE_ACCESS_DENIED",
    }
    status_code = 403 if error.get("code") in denied_codes else 400
    raise HTTPException(
        status_code=status_code,
        detail={
            "code": error.get("code", "WORKFLOW_ERROR"),
            "message": error.get("message", "Workflow failed."),
            "requestId": state.request_id,
        },
    )


@app.get("/api/agent/traces")
def api_agent_traces() -> dict[str, Any]:
    return {"runs": list(AGENT_RUNS.values()), "count": len(AGENT_RUNS)}


@app.post("/api/profile")
def api_submit_profile(profile: ProfileRequest) -> dict[str, Any]:
    PROFILE_STORE[profile.email.casefold()] = profile.model_dump()
    state = _run_api_workflow(
        user_query="Validate the submitted matching profile.",
        intent="profile",
        request_data=profile.model_dump(),
    )
    _raise_workflow_error(state)
    return {**state.output, "requestId": state.request_id}


@app.get("/api/profile")
def api_profile_analysis(
    email: str = Query(default="", max_length=254),
) -> dict[str, Any]:
    state = _run_api_workflow(
        user_query="Read profile completeness from consented data.",
        intent="profile",
        request_data={"email": email} if email else {},
    )
    _raise_workflow_error(state)
    return {**state.output, "requestId": state.request_id}


@app.get("/api/matches")
def api_matches(
    email: str = Query(default="", max_length=254),
) -> list[dict[str, Any]]:
    state = _run_api_workflow(
        user_query="Find consented and eligible matching candidates.",
        intent="matching",
        request_data={"email": email} if email else {},
    )
    _raise_workflow_error(state)
    return state.output.get("candidates", [])


@app.post("/api/date-plan")
def api_date_plan(request: DatePlanRequest) -> dict[str, Any]:
    candidate_id = _normalize_user_id(request.candidateId)
    state = _run_api_workflow(
        user_query=request.customPrompt or "Create a grounded date plan.",
        intent="date_planning",
        candidate_id=candidate_id,
        request_data=request.model_dump(),
    )
    if state.safety_verdict == "BLOCK":
        raise HTTPException(
            status_code=400,
            detail={
                "code": "SAFETY_BLOCKED",
                "message": state.output.get("message", SAFE_FALLBACK_MESSAGE),
                "requestId": state.request_id,
            },
        )
    _raise_workflow_error(state)
    return {**state.output, "requestId": state.request_id}


@app.post("/api/chat")
def api_chat(request: ChatRequest) -> dict[str, Any]:
    candidate_id = _normalize_user_id(request.candidateId)
    if _is_date_planning_chat(request.message):
        state = _run_api_workflow(
            user_query=request.message,
            intent="date_planning",
            candidate_id=candidate_id,
            city=_extract_chat_city(request.message),
            max_budget=_extract_chat_budget(request.message),
            request_data={
                "candidateId": candidate_id,
                "customPrompt": request.message,
                "source": "chat",
            },
        )
        if state.safety_verdict != "BLOCK":
            _raise_workflow_error(state)
        return {
            "reply": (
                state.output.get("message", SAFE_FALLBACK_MESSAGE)
                if state.safety_verdict == "BLOCK"
                else _format_date_plan_chat_reply(state.output)
            ),
            "suggestedTopics": [
                "Đổi ngân sách",
                "Không gian ngoài trời",
                "Câu hỏi phá băng",
            ],
            "safetyApproved": state.safety_verdict != "BLOCK",
            "requestId": state.request_id,
            "datePlan": state.output if state.safety_verdict != "BLOCK" else None,
        }

    state = _run_api_workflow(
        user_query=request.message,
        intent="chat",
        candidate_id=candidate_id,
    )
    if state.safety_verdict != "BLOCK":
        _raise_workflow_error(state)
    return {**state.output, "requestId": state.request_id}


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
