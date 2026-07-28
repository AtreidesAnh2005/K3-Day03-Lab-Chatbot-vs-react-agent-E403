from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.tools import AVAILABLE_TOOLS  # noqa: E402


def assert_subset(expected: Any, actual: Any, path: str = "output") -> None:
    if isinstance(expected, dict):
        assert isinstance(actual, dict), f"{path} must be an object"
        for key, value in expected.items():
            assert key in actual, f"{path}.{key} is missing"
            assert_subset(value, actual[key], f"{path}.{key}")
        return

    if isinstance(expected, list):
        assert isinstance(actual, list), f"{path} must be a list"
        assert len(actual) >= len(expected), f"{path} has fewer items than expected"
        for index, value in enumerate(expected):
            assert_subset(value, actual[index], f"{path}[{index}]")
        return

    assert expected == actual, f"{path}: expected {expected!r}, got {actual!r}"


def main() -> None:
    config_path = ROOT_DIR / "config" / "test_cases.json"
    test_cases = json.loads(config_path.read_text(encoding="utf-8"))

    serialized = json.dumps(test_cases, ensure_ascii=False)
    for legacy_value in ['"U001"', '"U002"', '"U003"', '"Hanoi"', '"estimated_cost"']:
        assert legacy_value not in serialized, f"Legacy contract value remains: {legacy_value}"

    executed = 0
    for test_case in test_cases:
        expected_calls = test_case.get("expected_tool_calls", [])
        expected_tools = test_case.get("expected_tools", [])
        assert len(expected_calls) == test_case["expected_tool_call_count"]
        assert [call["tool"] for call in expected_calls] == expected_tools

        observations = {
            observation["order"]: observation
            for observation in test_case.get("mock_observations", [])
        }
        actual_data_by_order: dict[int, dict[str, Any]] = {}

        for call in expected_calls:
            order = call["order"]
            tool_name = call["tool"]
            assert tool_name in AVAILABLE_TOOLS, f"{tool_name} is not registered"

            arguments = call["arguments"]
            dependency_order = call.get("depends_on_observation")
            if dependency_order is not None:
                dependency = actual_data_by_order[dependency_order]
                if tool_name == "search_date_activities":
                    assert arguments["interests"] == dependency["shared_interests"]

            result = AVAILABLE_TOOLS[tool_name](**arguments)
            assert result["status"] in {"success", "warning", "insufficient_data"}
            assert result["error"] is None
            assert result["data"] is not None
            actual_data_by_order[order] = result["data"]

            expected_observation = observations[order]
            assert expected_observation["tool"] == tool_name
            assert_subset(expected_observation["output"], result["data"])
            executed += 1

    assert executed == 3
    print("PASS Role 1 identifiers and schemas")
    print("PASS Role 1 expected tool order")
    print("PASS Role 1 mock observations against Role 2 outputs")
    print("All Role 1 - Role 2 contract tests passed.")


if __name__ == "__main__":
    main()
