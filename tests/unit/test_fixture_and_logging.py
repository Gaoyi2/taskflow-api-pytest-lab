"""Review fixture isolation, for loop, len, logging/caplog."""

import logging

import pytest

from taskflow.validation import validate_task

logger = logging.getLogger(__name__)


@pytest.mark.unit
def test_first_mutates_own_copy(sample_task):
    sample_task["title"] = "Changed"
    assert sample_task["title"] == "Changed"


@pytest.mark.unit
def test_second_sees_fresh_data(sample_task):
    assert sample_task["title"] == "Learn pytest"


@pytest.mark.unit
def test_list_and_for_assertions():
    tasks = [{"title": "Task A"}, {"title": "Task B"}]
    assert isinstance(tasks, list)
    assert len(tasks) > 0
    for task in tasks:
        assert "title" in task
        assert isinstance(task["title"], str)
        assert task["title"].strip() != ""


@pytest.mark.unit
def test_logging_with_caplog(caplog):
    with caplog.at_level(logging.INFO):
        logger.info("Validate a task title")
        validate_task({"title": "Test reports"})
    assert "Validate a task title" in caplog.text
