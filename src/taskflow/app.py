"""Self-contained REST API. Uses only the Python standard library.

The task database lives in RAM. This is a teaching app, not a production server.
"""

import argparse
import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from urllib.parse import urlsplit

from taskflow.validation import validate_task

logger = logging.getLogger(__name__)


class TaskStore:
    """Small in-memory store, isolated per test-server instance."""

    def __init__(self):
        self._tasks = {}
        self._next_id = 1
        self._lock = Lock()

    def list_all(self):
        with self._lock:
            return [dict(x) for x in self._tasks.values()]

    def get(self, task_id):
        with self._lock:
            task = self._tasks.get(task_id)
            return dict(task) if task is not None else None

    def create(self, fields):
        with self._lock:
            task = {"id": self._next_id, **fields}
            self._next_id += 1
            self._tasks[task["id"]] = task
            return dict(task)

    def update(self, task_id, fields):
        with self._lock:
            if task_id not in self._tasks:
                return None
            task = {"id": task_id, **fields}
            self._tasks[task_id] = task
            return dict(task)

    def delete(self, task_id):
        with self._lock:
            return self._tasks.pop(task_id, None) is not None


def make_handler(store):
    """Create an HTTP handler bound to one store (no test state leakage)."""

    class TaskHandler(BaseHTTPRequestHandler):
        server_version = "TaskFlowPractice/1.0"

        def log_message(self, fmt, *args):
            logger.debug("HTTP server: " + fmt, *args)

        def send_json(self, code, data):
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def send_empty(self, code):
            self.send_response(code)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def get_path_parts(self):
            return urlsplit(self.path).path.rstrip("/").split("/")

        def task_id(self, parts):
            if len(parts) != 4 or parts[:3] != ["", "api", "tasks"]:
                return None
            try:
                value = int(parts[3])
                return value if value > 0 else None
            except ValueError:
                return None

        def read_payload(self):
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 1 or length > 65536:
                    raise ValueError("request body is empty or too large")
                raw = self.rfile.read(length)
                return json.loads(raw.decode("utf-8"))
            except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
                raise ValueError("invalid JSON body") from None

        def do_GET(self):
            parts = self.get_path_parts()
            if parts == ["", "api", "health"]:
                return self.send_json(200, {"status": "ok"})
            if parts == ["", "api", "tasks"]:
                return self.send_json(200, store.list_all())
            task_id = self.task_id(parts)
            if task_id is None:
                return self.send_json(404, {"error": "route not found"})
            task = store.get(task_id)
            if task is None:
                return self.send_json(404, {"error": "task not found"})
            return self.send_json(200, task)

        def do_POST(self):
            if self.get_path_parts() != ["", "api", "tasks"]:
                return self.send_json(404, {"error": "route not found"})
            try:
                fields = validate_task(self.read_payload())
            except (ValueError, TypeError) as exc:
                return self.send_json(400, {"error": str(exc)})
            return self.send_json(201, store.create(fields))

        def do_PUT(self):
            task_id = self.task_id(self.get_path_parts())
            if task_id is None:
                return self.send_json(404, {"error": "route not found"})
            if store.get(task_id) is None:
                return self.send_json(404, {"error": "task not found"})
            try:
                fields = validate_task(self.read_payload())
            except (ValueError, TypeError) as exc:
                return self.send_json(400, {"error": str(exc)})
            updated = store.update(task_id, fields)
            if updated is None:
                return self.send_json(404, {"error": "task not found"})
            return self.send_json(200, updated)

        def do_DELETE(self):
            task_id = self.task_id(self.get_path_parts())
            if task_id is None:
                return self.send_json(404, {"error": "route not found"})
            if not store.delete(task_id):
                return self.send_json(404, {"error": "task not found"})
            return self.send_empty(204)

    return TaskHandler


def create_server(host="127.0.0.1", port=0):
    """Bind to a real HTTP port (0 = choose an unused random port)."""
    return ThreadingHTTPServer((host, port), make_handler(TaskStore()))


def main():
    parser = argparse.ArgumentParser(description="Run TaskFlow practice REST server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = create_server(args.host, args.port)
    print(f"TaskFlow API: http://{args.host}:{server.server_port}/api/health")
    print("Press Ctrl+C to stop; data is kept only in memory.")
    try:
        server.serve_forever(poll_interval=0.05)
    except KeyboardInterrupt:
        print("Stopping API server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
