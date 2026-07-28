# CupidMAS Tools

## Scope

- Tool deterministic dung du lieu mock.
- Khong goi API ngoai.
- Khong goi LLM.
- Khong gui tin, dat lich, thanh toan, hoac thay nguoi dung quyet dinh.
- Dung duoc cho ReAct V1 va Supervisor-based Multi-Agent V2.

## Tool groups

| Group | Specialist | Tools |
|---|---|---|
| Profile | Profile Agent | get_match_profile, check_profile_completeness, check_matching_eligibility |
| Matching | Matching Agent | search_candidates, calculate_compatibility, get_compatibility_breakdown |
| Date | Date Planning Agent | get_shared_interests, search_date_activities, estimate_date_cost |

## Public tools

| Tool | Khi dung | Input chinh | Output chinh |
|---|---|---|---|
| get_match_profile | Doc self/candidate profile | user_id, requester_id | profile consented view |
| check_profile_completeness | Kiem tra du lieu profile | user_id, purpose | missing fields, recommended_action |
| check_matching_eligibility | Kiem tra eligibility gate | user_id, candidate_id | eligible, failed_gates, evidence |
| search_candidates | Tao candidate pool | user_id, city, age filters | candidates, filtered_out_counts |
| calculate_compatibility | Tinh score deterministic | user_id, candidate_id | score, coverage, conflicts |
| get_compatibility_breakdown | Giai thich score | user_id, candidate_id | breakdown, strengths, conflicts, unknowns |
| get_shared_interests | Tim so thich chung | user_a_id, user_b_id | shared_interests |
| search_date_activities | Tim hoat dong hen ho | city, interests, budget | activity list |
| estimate_date_cost | Uoc tinh chi phi | activity_id, people, extras | total_estimated_cost |

## Data files

| File | Noi dung |
|---|---|
| data/cupid_profiles.json | Ho so hu cau cua nguoi truong thanh |
| data/cupid_preferences.json | Preference da khai bao |
| data/cupid_consents.json | Consent hai chieu va field scope |
| data/cupid_safety.json | Safety va eligibility records |
| data/cupid_date_activities.json | Hoat dong hen ho mock |

## Typical matching flow

```text
get_match_profile
-> check_profile_completeness
-> check_matching_eligibility
-> search_candidates
-> calculate_compatibility
-> get_compatibility_breakdown
```

## Typical date flow

```text
get_shared_interests
-> search_date_activities
-> estimate_date_cost
```

## Key safety rules

- Candidate data is limited by active consent.
- Hard constraints are checked in both directions.
- Safety gate runs before scoring.
- Required user-confirmed constraints are not relaxed.
- Raw candidate preferences are not returned.
- Missing data becomes `unknown` or `insufficient_data`.
- Compatibility score does not guarantee relationship success.
- Date tools only suggest and estimate.

## Response envelope

All public tools return:

```json
{
  "status": "success",
  "tool": "tool_name",
  "data": {},
  "error": null,
  "metadata": {}
}
```

Error responses use the same shape with `status="error"` or `status="denied"` and an `error.code`.

## Run tests

```bash
python scripts/smoke_test_tools.py
```

## Integration note

Role 4 can import:

```python
from src.tools import PROFILE_TOOLS, MATCHING_TOOLS, DATE_TOOLS, AVAILABLE_TOOLS
```

The functions are plain Python callables and can later be wrapped by LangChain or LangGraph outside Role 2.
