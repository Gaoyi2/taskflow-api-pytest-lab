"""Parametrized negative HTTP tests: 400 and 404 are expected results."""

import pytest


@pytest.mark.integration
@pytest.mark.negative
@pytest.mark.parametrize(
    "payload",
    [
        {"title": ""},
        {"title": "   "},
        {"title": "X" * 51},
        {"title": "Valid", "priority": "urgent"},
        {"title": "Valid", "completed": "yes"},
        {"title": 123},
        ["not", "a", "dict"],
    ],
    ids=["empty", "spaces", "too-long", "bad-priority", "bad-boolean", "bad-type", "not-object"],
)
def test_post_invalid_data_returns_400(api_client, payload):
    response = api_client.create_task(payload)
    assert response.status_code == 400
    error = response.json()
    assert isinstance(error["error"], str)
    assert error["error"].strip() != ""


@pytest.mark.integration
@pytest.mark.negative
@pytest.mark.parametrize("task_id", [999999, 888888])
def test_missing_task_returns_404(api_client, task_id):
    response = api_client.get_task(task_id)
    assert response.status_code == 404
    assert response.json()["error"] == "task not found"


@pytest.mark.integration
@pytest.mark.negative
def test_put_missing_task_returns_404(api_client, sample_task):
    response = api_client.update_task(999999, sample_task)
    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.negative
def test_delete_missing_task_returns_404(api_client):
    response = api_client.delete_task(999999)
    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.negative
def test_update_invalid_title_returns_400(api_client, created_task):
    response = api_client.update_task(created_task["id"], {"title": "  "})
    assert response.status_code == 400
    # Fixture still deletes created_task during teardown.
