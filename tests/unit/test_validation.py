"""Unit tests: parametrize, boundary values, errors, assert, fixture."""

import pytest

from taskflow.validation import MAX_TITLE_LENGTH, validate_task


@pytest.mark.unit
@pytest.mark.parametrize("title", ["A", "Learn Pytest", "X" * MAX_TITLE_LENGTH])
def test_valid_title_boundaries(title):
    result = validate_task({"title": title})
    assert result["title"] == title
    assert result["priority"] == "medium"
    assert result["completed"] is False


@pytest.mark.unit
@pytest.mark.parametrize("priority", ["low", "medium", "high"])
def test_valid_priorities(priority):
    result = validate_task({"title": "Learn CI", "priority": priority})
    assert result["priority"] == priority


@pytest.mark.unit
@pytest.mark.negative
@pytest.mark.parametrize(
    "title, expected_error",
    [
        ("", "title must not be blank"),
        ("   ", "title must not be blank"),
        ("X" * (MAX_TITLE_LENGTH + 1), "title must be at most 50 characters"),
    ],
)
def test_rejects_invalid_title_values(title, expected_error):
    with pytest.raises(ValueError, match=expected_error):
        validate_task({"title": title})


@pytest.mark.unit
@pytest.mark.negative
@pytest.mark.parametrize("title", [None, 123, ["abc"]])
def test_rejects_wrong_title_types(title):
    with pytest.raises(TypeError, match="title must be a string"):
        validate_task({"title": title})


@pytest.mark.unit
@pytest.mark.negative
@pytest.mark.parametrize("payload", [None, [], "hello", 42])
def test_rejects_non_dict_payload(payload):
    with pytest.raises(TypeError, match="request body must be a JSON object"):
        validate_task(payload)


@pytest.mark.unit
@pytest.mark.negative
def test_rejects_invalid_priority():
    with pytest.raises(ValueError, match="priority must be"):
        validate_task({"title": "A", "priority": "urgent"})


@pytest.mark.unit
@pytest.mark.negative
def test_rejects_wrong_completed_type():
    with pytest.raises(TypeError, match="completed must be a boolean"):
        validate_task({"title": "A", "completed": "yes"})


@pytest.mark.unit
def test_strip_title_without_changing_input(sample_task):
    sample_task["title"] = "   Learn pytest   "
    result = validate_task(sample_task)
    assert result["title"] == "Learn pytest"
    assert sample_task["title"] == "   Learn pytest   "
