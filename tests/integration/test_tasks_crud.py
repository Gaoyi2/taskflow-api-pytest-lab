"""Integration tests: real Requests/HTTP, all CRUD methods, fixture cleanup."""

import pytest


@pytest.mark.integration
@pytest.mark.smoke
def test_health(api_client):
    response = api_client.health()
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.integration
@pytest.mark.smoke
def test_list_empty_on_new_server(api_client):
    response = api_client.list_tasks()
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0


@pytest.mark.integration
@pytest.mark.smoke
def test_post_get_put_get_and_fixture_delete(api_client, created_task):
    task_id = created_task["id"]
    assert isinstance(task_id, int)

    response = api_client.get_task(task_id)
    assert response.status_code == 200
    assert response.json()["title"] == "Learn pytest"

    payload = {"title": "Learn GitHub Actions", "priority": "high", "completed": True}
    updated = api_client.update_task(task_id, payload)
    assert updated.status_code == 200
    assert updated.json()["title"] == payload["title"]

    response = api_client.get_task(task_id)
    assert response.status_code == 200
    assert response.json()["completed"] is True

    listed = api_client.list_tasks().json()
    assert len(listed) == 1
    assert listed[0]["id"] == task_id
    # Fixture automatically calls DELETE after this test function.


@pytest.mark.integration
def test_delete_then_get_404(api_client, sample_task):
    created = api_client.create_task(sample_task)
    assert created.status_code == 201
    task_id = created.json()["id"]
    deleted = api_client.delete_task(task_id)
    assert deleted.status_code == 204
    assert deleted.text == ""
    missing = api_client.get_task(task_id)
    assert missing.status_code == 404
    assert missing.json()["error"] == "task not found"
