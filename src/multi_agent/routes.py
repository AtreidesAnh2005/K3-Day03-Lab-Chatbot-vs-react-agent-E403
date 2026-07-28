"""Route names used by the multi-agent supervisor."""

from typing import Literal


RouteName = Literal[
    "profile",
    "matching",
    "date_planning",
    "safety_critic",
    "response",
]
