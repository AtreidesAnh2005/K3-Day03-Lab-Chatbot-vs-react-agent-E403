"""
Core Agent App for Role 4.

This file integrates prompts, tools, test cases, providers, and runtime
guardrails for the Cupid Chatbot vs ReAct Agent lab.
"""

import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from prompts import (  # noqa: E402
    CHATBOT_BASELINE_PROMPT,
    MAX_ITERATIONS,
    MAX_REPEATED_ACTIONS,
    REACT_SYSTEM_PROMPT,
    SAFE_FALLBACK_MESSAGE,
)
from providers import get_llm_provider  # noqa: E402
from tools import AVAILABLE_TOOLS  # noqa: E402

load_dotenv()


@dataclass
class ParsedReactResponse:
    thought: str | None = None
    action_name: str | None = None
    action_args: list[Any] | None = None
    final_answer: str | None = None
    parser_error: str | None = None


SENSITIVE_PATTERNS = [
    "ignore all previous instructions",
    "bỏ qua",
    "bo qua",
    "bypass",
    "developer mode",
    "matching_consent",
    "số điện thoại",
    "so dien thoai",
    "phone",
    "email",
    "địa chỉ",
    "dia chi",
    "address",
    "người chưa thành niên",
    "nguoi chua thanh nien",
    "minor",
]


def load_test_cases() -> list[dict[str, Any]]:
    """Load Role 1 test cases from config/test_cases.json."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_safety_blocked(user_query: str) -> bool:
    """Block obvious privacy, consent, minor-safety, and prompt-injection cases."""
    text = user_query.lower()
    has_injection = any(
        marker in text
        for marker in [
            "ignore all previous instructions",
            "bypass",
            "developer mode",
            "không được từ chối",
            "khong duoc tu choi",
        ]
    )
    has_private_data_request = any(
        marker in text
        for marker in [
            "số điện thoại",
            "so dien thoai",
            "phone",
            "email",
            "địa chỉ",
            "dia chi",
            "address",
            "matching_consent",
        ]
    )
    has_minor_risk = "người chưa thành niên" in text or "minor" in text
    return (has_injection and has_private_data_request) or has_minor_risk


def run_baseline_chatbot(user_query: str, provider) -> str:
    """Run the baseline chatbot without tools."""
    print(f"\n[CHATBOT BASELINE] Cau hoi: {user_query}")
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"Chatbot tra loi:\n{response}")
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
                parsed.parser_error = f"Action khong dung format: {action_text}"
                return parsed

            parsed.action_name = match.group(1)
            raw_args = match.group(2).strip()
            try:
                parsed.action_args = json.loads(f"[{raw_args}]") if raw_args else []
            except json.JSONDecodeError as exc:
                parsed.parser_error = f"Action arguments khong phai JSON hop le: {exc}"
            return parsed

    parsed.parser_error = "Khong tim thay Action hoac Final Answer trong response."
    return parsed


def execute_tool(tool_name: str, args: list[Any]) -> dict[str, Any]:
    """Execute a registered tool safely and return a structured observation."""
    tool = AVAILABLE_TOOLS.get(tool_name)
    if tool is None:
        return {
            "ok": False,
            "error_type": "unknown_tool",
            "message": f"Tool '{tool_name}' khong ton tai trong AVAILABLE_TOOLS.",
        }

    try:
        return {
            "ok": True,
            "tool": tool_name,
            "output": tool(*args),
        }
    except Exception as exc:
        return {
            "ok": False,
            "error_type": "tool_exception",
            "tool": tool_name,
            "message": str(exc),
        }


def render_observation(observation: dict[str, Any]) -> str:
    """Serialize Observation for both console trace and next LLM call."""
    return json.dumps(observation, ensure_ascii=False, indent=2)


def run_react_agent(user_query: str, provider) -> str:
    """Run a guarded ReAct loop: Thought -> Action -> Observation -> Final Answer."""
    print(f"\n[REACT AGENT] Cau hoi: {user_query}")

    if is_safety_blocked(user_query):
        print("GUARDRAIL: Privacy/consent/prompt-injection request blocked before tool use.")
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
            print(f"Final Answer: {SAFE_FALLBACK_MESSAGE}")
            return SAFE_FALLBACK_MESSAGE

        if parsed.final_answer:
            return parsed.final_answer

        if not parsed.action_name or parsed.action_args is None:
            print("Parser Error: Response khong co action hop le.")
            print(f"Final Answer: {SAFE_FALLBACK_MESSAGE}")
            return SAFE_FALLBACK_MESSAGE

        action_key = json.dumps(
            {"tool": parsed.action_name, "args": parsed.action_args},
            ensure_ascii=False,
            sort_keys=True,
        )
        action_history[action_key] = action_history.get(action_key, 0) + 1
        if action_history[action_key] > MAX_REPEATED_ACTIONS:
            print("GUARDRAIL: Repeated action detected.")
            print(f"Final Answer: {SAFE_FALLBACK_MESSAGE}")
            return SAFE_FALLBACK_MESSAGE

        observation = execute_tool(parsed.action_name, parsed.action_args)
        observation_text = render_observation(observation)
        print(f"Observation:\n{observation_text}")

        conversation = (
            f"{conversation}\n\n"
            f"Assistant response:\n{response}\n\n"
            f"Observation:\n{observation_text}\n\n"
            "Continue the ReAct protocol. Use Final Answer if you have enough evidence."
        )

        if not observation.get("ok"):
            print("GUARDRAIL: Tool failed; returning safe fallback.")
            print(f"Final Answer: {SAFE_FALLBACK_MESSAGE}")
            return SAFE_FALLBACK_MESSAGE

    print(f"GUARDRAIL: Max iterations reached ({MAX_ITERATIONS}).")
    print(f"Final Answer: {SAFE_FALLBACK_MESSAGE}")
    return SAFE_FALLBACK_MESSAGE


def should_use_react(test_case: dict[str, Any]) -> bool:
    """Route test cases based on Role 1 metadata."""
    expected_path = str(test_case.get("expected_path", "")).lower()
    return bool(test_case.get("requires_tools")) or expected_path in {
        "react_agent",
        "safety_guardrail",
    }


if __name__ == "__main__":
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
