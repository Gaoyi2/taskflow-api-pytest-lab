"""Requests API Client: one place for GET/POST/PUT/DELETE and logging."""

import logging
import time

import requests

logger = logging.getLogger(__name__)


class TaskApiClient:
    def __init__(self, base_url, timeout=5):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def close(self):
        self.session.close()

    def _request(self, method, path, **kwargs):
        url = f"{self.base_url}/{path.lstrip('/')}"
        logger.info("Request started: %s %s", method, url)
        start = time.perf_counter()
        try:
            response = self.session.request(
                method, url, timeout=self.timeout, **kwargs
            )
        except requests.RequestException:
            logger.exception("Network error: %s %s", method, url)
            raise
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Request finished: %s %s status=%s elapsed_ms=%.1f",
            method, url, response.status_code, elapsed_ms
        )
        if response.status_code >= 500:
            logger.error("Server error: HTTP %s", response.status_code)
        return response

    def health(self):
        return self._request("GET", "health")

    def list_tasks(self):
        return self._request("GET", "tasks")

    def get_task(self, task_id):
        return self._request("GET", f"tasks/{task_id}")

    def create_task(self, payload):
        return self._request("POST", "tasks", json=payload)

    def update_task(self, task_id, payload):
        return self._request("PUT", f"tasks/{task_id}", json=payload)

    def delete_task(self, task_id):
        return self._request("DELETE", f"tasks/{task_id}")
