"""Business validation: easy to practice unit tests and pytest.raises."""

VALID_PRIORITIES = {"low", "medium", "high"}
MAX_TITLE_LENGTH = 50


def validate_task(payload: object) -> dict:
    """Return sanitized task fields. Raise TypeError/ValueError on invalid input."""
    if not isinstance(payload, dict):
        raise TypeError("request body must be a JSON object")

    title = payload.get("title")
    if not isinstance(title, str):
        raise TypeError("title must be a string")
    title = title.strip()
    if not title:
        raise ValueError("title must not be blank")
    if len(title) > MAX_TITLE_LENGTH:
        raise ValueError("title must be at most 50 characters")

    priority = payload.get("priority", "medium")
    if not isinstance(priority, str) or priority not in VALID_PRIORITIES:
        raise ValueError("priority must be low, medium or high")

    completed = payload.get("completed", False)
    if not isinstance(completed, bool):
        raise TypeError("completed must be a boolean")

    return {"title": title, "priority": priority, "completed": completed}
