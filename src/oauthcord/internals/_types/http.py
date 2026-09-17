from typing import NotRequired, TypedDict

RateLimitResponse = TypedDict(
    "RateLimitResponse",
    {
        "message": str,
        "retry_after": float,
        "global": bool,
        "code": NotRequired[int],
    },
)
