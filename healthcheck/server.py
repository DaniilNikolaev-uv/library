from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import socket
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
HOST = os.getenv("HEALTHCHECK_BIND_HOST", "0.0.0.0")
PORT = int(os.getenv("HEALTHCHECK_PORT", "8085"))
TIMEOUT_SECONDS = int(os.getenv("HEALTHCHECK_TIMEOUT_SECONDS", "3"))
SESSION_COOKIE_NAME = "healthcheck_session"
SESSION_TTL_SECONDS = int(os.getenv("HEALTHCHECK_SESSION_TTL_SECONDS", "43200"))
SESSION_SECRET = os.getenv("HEALTHCHECK_SESSION_SECRET", "change-me-in-production")
BACKEND_BASE_URL = os.getenv("HEALTHCHECK_BACKEND_URL", "http://localhost:8000").rstrip("/")
SECURE_COOKIES = os.getenv("HEALTHCHECK_SECURE_COOKIES", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
FRONTEND_URL = os.getenv("HEALTHCHECK_FRONTEND_URL", "http://localhost:3000/").rstrip("/") + "/"
BACKEND_HEALTH_URL = os.getenv("HEALTHCHECK_BACKEND_HEALTH_URL", "http://localhost:8000/swagger/").rstrip("/") + "/"
MINIO_API_URL = os.getenv("HEALTHCHECK_MINIO_API_URL", "http://localhost:9000/minio/health/live")
MINIO_CONSOLE_URL = os.getenv("HEALTHCHECK_MINIO_CONSOLE_URL", "http://localhost:9001/").rstrip("/") + "/"
PGADMIN_URL = os.getenv("HEALTHCHECK_PGADMIN_URL", "http://localhost:5050/").rstrip("/") + "/"
POSTGRES_HOST = os.getenv("HEALTHCHECK_POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("HEALTHCHECK_POSTGRES_PORT", "5432"))
LOG_TAIL_LINES = int(os.getenv("HEALTHCHECK_LOG_TAIL_LINES", "80"))


@dataclass
class ServiceCheck:
    key: str
    name: str
    type: str
    target: str
    container: str | None
    status: str
    details: str
    checked_at: str
    response_time_ms: int | None


HTTP_SERVICES = (
    {
        "key": "frontend",
        "name": "Frontend",
        "type": "http",
        "target": FRONTEND_URL,
        "container": "archerion_frontend",
    },
    {
        "key": "backend",
        "name": "Backend",
        "type": "http",
        "target": BACKEND_HEALTH_URL,
        "container": "archerion_backend",
    },
    {
        "key": "minio_api",
        "name": "MinIO API",
        "type": "http",
        "target": MINIO_API_URL,
        "container": "archerion_minio",
    },
    {
        "key": "minio_console",
        "name": "MinIO Console",
        "type": "http",
        "target": MINIO_CONSOLE_URL,
        "container": "archerion_minio",
    },
    {
        "key": "pgadmin",
        "name": "pgAdmin",
        "type": "http",
        "target": PGADMIN_URL,
        "container": "pgadmin_archerion",
    },
)

TCP_SERVICES = (
    {
        "key": "postgres",
        "name": "PostgreSQL",
        "type": "tcp",
        "target": (POSTGRES_HOST, POSTGRES_PORT),
        "container": "archerion_db",
    },
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def json_request(url: str, method: str = "GET", payload: dict | None = None, token: str | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"User-Agent": "archerion-healthcheck/1.0"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, data=data, method=method, headers=headers)
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def is_admin_user(user_data: dict) -> bool:
    return bool(user_data.get("is_staff")) or user_data.get("role") == "admin"


def make_signature(payload: bytes) -> str:
    digest = hmac.new(SESSION_SECRET.encode("utf-8"), payload, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def encode_session(email: str) -> str:
    expires_at = int(time.time()) + SESSION_TTL_SECONDS
    payload = f"{email}|{expires_at}".encode("utf-8")
    token = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
    return f"{token}.{make_signature(payload)}"


def decode_session(token: str | None) -> str | None:
    if not token or "." not in token:
        return None

    encoded_payload, signature = token.split(".", 1)
    try:
        padding = "=" * (-len(encoded_payload) % 4)
        payload = base64.urlsafe_b64decode(encoded_payload + padding)
    except (ValueError, TypeError):
        return None

    expected_signature = make_signature(payload)
    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        email, expires_at_raw = payload.decode("utf-8").split("|", 1)
        expires_at = int(expires_at_raw)
    except (ValueError, UnicodeDecodeError):
        return None

    if expires_at < int(time.time()):
        return None

    return email


def parse_session_cookie(cookie_header: str | None) -> str | None:
    if not cookie_header:
        return None

    cookie = SimpleCookie()
    cookie.load(cookie_header)
    morsel = cookie.get(SESSION_COOKIE_NAME)
    if not morsel:
        return None

    return decode_session(morsel.value)


def auth_with_backend(email: str, password: str) -> tuple[bool, str]:
    try:
        token_data = json_request(
            f"{BACKEND_BASE_URL}/api/auth/login/",
            method="POST",
            payload={"email": email, "password": password},
        )
        access_token = token_data.get("access")
        if not access_token:
            return False, "Backend auth failed"

        me_data = json_request(f"{BACKEND_BASE_URL}/api/auth/me/", token=access_token)
        if not is_admin_user(me_data):
            return False, "Admin access required"
        return True, me_data.get("email", email)
    except HTTPError as error:
        if error.code in {HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN, HTTPStatus.BAD_REQUEST}:
            return False, "Invalid credentials"
        return False, f"Backend returned HTTP {error.code}"
    except (URLError, TimeoutError, ConnectionResetError, OSError):
        return False, "Backend auth unavailable"


def check_http(key: str, name: str, target: str, container: str | None) -> ServiceCheck:
    started = time.perf_counter()
    checked_at = utc_now()
    request = Request(target, headers={"User-Agent": "archerion-healthcheck/1.0"})

    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            elapsed = int((time.perf_counter() - started) * 1000)
            status_code = response.getcode()
            if 200 <= status_code < 400:
                status = "up"
            else:
                status = "degraded"
            return ServiceCheck(
                key, name, "http", target, container, status, f"HTTP {status_code}", checked_at, elapsed
            )
    except HTTPError as error:
        elapsed = int((time.perf_counter() - started) * 1000)
        status = "degraded" if error.code < 500 else "down"
        return ServiceCheck(
            key, name, "http", target, container, status, f"HTTP {error.code}", checked_at, elapsed
        )
    except URLError as error:
        return ServiceCheck(
            key, name, "http", target, container, "down", f"Network error: {error.reason}", checked_at, None
        )
    except ConnectionResetError:
        return ServiceCheck(
            key, name, "http", target, container, "down", "Connection reset by peer", checked_at, None
        )
    except OSError as error:
        return ServiceCheck(
            key, name, "http", target, container, "down", f"Socket error: {error.strerror or error}", checked_at, None
        )
    except TimeoutError:
        return ServiceCheck(key, name, "http", target, container, "down", "Timeout", checked_at, None)


def check_tcp(key: str, name: str, host: str, port: int, container: str | None) -> ServiceCheck:
    started = time.perf_counter()
    checked_at = utc_now()
    try:
        with socket.create_connection((host, port), timeout=TIMEOUT_SECONDS):
            elapsed = int((time.perf_counter() - started) * 1000)
            return ServiceCheck(
                key,
                name,
                "tcp",
                f"{host}:{port}",
                container,
                "up",
                "TCP connection established",
                checked_at,
                elapsed,
            )
    except TimeoutError:
        return ServiceCheck(
            key, name, "tcp", f"{host}:{port}", container, "down", "Connection timeout", checked_at, None
        )
    except OSError as error:
        return ServiceCheck(
            key, name, "tcp", f"{host}:{port}", container, "down", f"Socket error: {error.strerror or error}", checked_at, None
        )


def get_service_logs(service_key: str) -> dict[str, str | int | bool]:
    service = next(
        (
            item
            for item in (*HTTP_SERVICES, *TCP_SERVICES)
            if item["key"] == service_key
        ),
        None,
    )
    if not service:
        raise KeyError("Unknown service")

    container = service.get("container")
    if not container:
        return {"service": service_key, "container": "", "logs": "Logs are not configured for this service.", "available": False}

    try:
        completed = subprocess.run(
            ["docker", "logs", "--tail", str(LOG_TAIL_LINES), container],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except FileNotFoundError:
        return {"service": service_key, "container": container, "logs": "Docker CLI is not available in healthcheck container.", "available": False}
    except subprocess.TimeoutExpired:
        return {"service": service_key, "container": container, "logs": "Timed out while reading container logs.", "available": False}

    output = completed.stdout.strip()
    error_output = completed.stderr.strip()
    logs = output or error_output or "Container has no recent logs."
    return {
        "service": service_key,
        "container": container,
        "logs": logs,
        "available": completed.returncode == 0,
        "exit_code": completed.returncode,
    }


def run_checks() -> list[ServiceCheck]:
    results: list[ServiceCheck] = []
    for service in HTTP_SERVICES:
        results.append(
            check_http(service["key"], service["name"], service["target"], service["container"])
        )
    for service in TCP_SERVICES:
        host, port = service["target"]
        results.append(
            check_tcp(service["key"], service["name"], host, port, service["container"])
        )
    return results


class HealthcheckHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self.respond_health()
            return
        if self.path.startswith("/api/logs"):
            self.respond_logs()
            return
        if self.path == "/api/session":
            self.respond_session()
            return
        if self.path == "/api/logout":
            self.respond_logout()
            return
        if self.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:
        if self.path == "/api/login":
            self.respond_login()
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:
        return

    def current_user(self) -> str | None:
        return parse_session_cookie(self.headers.get("Cookie"))

    def require_auth(self) -> str | None:
        user = self.current_user()
        if not user:
            self.respond_json(HTTPStatus.UNAUTHORIZED, {"detail": "Authentication required"})
            return None
        return user

    def respond_json(self, status: int, payload: dict, *, session_value: str | None = None, clear_session: bool = False) -> None:
        encoded = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        if session_value is not None:
            secure_part = "; Secure" if SECURE_COOKIES else ""
            self.send_header(
                "Set-Cookie",
                f"{SESSION_COOKIE_NAME}={session_value}; HttpOnly; Path=/; SameSite=Lax; Max-Age={SESSION_TTL_SECONDS}{secure_part}",
            )
        elif clear_session:
            secure_part = "; Secure" if SECURE_COOKIES else ""
            self.send_header(
                "Set-Cookie",
                f"{SESSION_COOKIE_NAME}=; HttpOnly; Path=/; SameSite=Lax; Max-Age=0{secure_part}",
            )
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def respond_login(self) -> None:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0
        raw_body = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.respond_json(HTTPStatus.BAD_REQUEST, {"detail": "Invalid request body"})
            return

        email = str(payload.get("email", "")).strip()
        password = str(payload.get("password", ""))
        if not email or not password:
            self.respond_json(HTTPStatus.BAD_REQUEST, {"detail": "Email and password are required"})
            return

        ok, result = auth_with_backend(email, password)
        if not ok:
            self.respond_json(HTTPStatus.UNAUTHORIZED, {"detail": result})
            return

        self.respond_json(
            HTTPStatus.OK,
            {"email": result, "authenticated": True},
            session_value=encode_session(result),
        )

    def respond_session(self) -> None:
        user = self.current_user()
        if not user:
            self.respond_json(HTTPStatus.UNAUTHORIZED, {"authenticated": False})
            return
        self.respond_json(HTTPStatus.OK, {"authenticated": True, "email": user})

    def respond_logout(self) -> None:
        self.respond_json(HTTPStatus.OK, {"authenticated": False}, clear_session=True)

    def respond_health(self) -> None:
        user = self.require_auth()
        if not user:
            return
        services = run_checks()
        payload = {
            "generated_at": utc_now(),
            "user": user,
            "services": [asdict(service) for service in services],
        }
        self.respond_json(HTTPStatus.OK, payload)

    def respond_logs(self) -> None:
        user = self.require_auth()
        if not user:
            return

        service_key = ""
        try:
            from urllib.parse import parse_qs, urlparse

            parsed = urlparse(self.path)
            service_key = parse_qs(parsed.query).get("service", [""])[0]
        except Exception:
            service_key = ""

        if not service_key:
            self.respond_json(HTTPStatus.BAD_REQUEST, {"detail": "Query parameter 'service' is required"})
            return

        try:
            payload = get_service_logs(service_key)
        except KeyError:
            self.respond_json(HTTPStatus.NOT_FOUND, {"detail": "Unknown service"})
            return

        self.respond_json(HTTPStatus.OK, payload)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), HealthcheckHandler)
    print(f"Healthcheck server running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
