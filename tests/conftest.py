"""Fixture practice: setup/teardown, server isolation, and clean data."""

import logging
from threading import Thread

import pytest

from taskflow.app import create_server
from taskflow.client import TaskApiClient

logger = logging.getLogger(__name__)


@pytest.fixture
def sample_task():
    """Fresh dict for each test (default fixture scope=function)."""
    return {"title": "Learn pytest", "priority": "medium", "completed": False}


@pytest.fixture
def live_server():
    """Start a real local HTTP server automatically; no Docker needed."""
    server = create_server(port=0)  # operating system chooses an unused port
    thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}/api"
    logger.info("SETUP local test server %s", base_url)
    try:
        yield base_url
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        logger.info("TEARDOWN local test server")


@pytest.fixture
def api_client(live_server):
    """API client for a brand-new test server per test function."""
    client = TaskApiClient(live_server)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def created_task(api_client, sample_task):
    """Create task before test, and DELETE it after test (even on assert failure)."""
    response = api_client.create_task(sample_task)
    assert response.status_code == 201, response.text
    task = response.json()
    logger.info("SETUP created task id=%s", task["id"])
    try:
        yield task
    finally:
        response = api_client.delete_task(task["id"])
        logger.info("TEARDOWN delete task id=%s HTTP %s", task["id"], response.status_code)
        assert response.status_code == 204, response.text
