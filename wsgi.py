"""WSGI entry point for hosted deployments (PythonAnywhere, Render, Railwayâ€¦).

PythonAnywhere does not run ``server.py``; it imports a WSGI callable from this
file instead. Development still uses ``server.py`` unchanged â€” both entry points
share the same routing, storage and templates.

Configuration
-------------
On the **Web** tab of PythonAnywhere set:

* Source code   ``/home/<you>/angel-studios``
* Working dir   ``/home/<you>/angel-studios``
* WSGI file     replace its contents with this file (see ``deploy/``)

Environment variables (optional, set them in the WSGI file itself):

* ``ANGEL_DB``             path to the SQLite file
* ``ANGEL_ADMIN_EMAIL``    administrator login created on first run
* ``ANGEL_ADMIN_PASSWORD`` administrator password created on first run
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.parse import parse_qs

# Make the project importable no matter which directory the host runs us from.
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# On hosts with a read-only code directory, keep the database somewhere writable
# by pointing ANGEL_DB at a persistent path before importing the app package.
os.environ.setdefault("ANGEL_DB", str(BASE_DIR / "data" / "angel_studios.sqlite3"))

from app import api  # noqa: E402
from app.db import BASE_DIR as APP_BASE_DIR, init_db  # noqa: E402
from app.web import PUBLIC_DIR, SECURITY_HEADERS, MIME_OVERRIDES  # noqa: E402

import mimetypes  # noqa: E402

# Create tables and seed content once, at import time. Idempotent, so a reload
# or a second worker is harmless.
init_db()

#: Requests larger than this are rejected outright.
MAX_BODY_BYTES = 512 * 1024


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def _json_error(status: int, code: str, message: str, fields: dict | None = None):
    payload = json.dumps(
        {"error": {"code": code, "message": message, "fields": fields or {}}},
        ensure_ascii=False,
    ).encode("utf-8")
    return status, [("Content-Type", "application/json; charset=utf-8")], payload


def _read_body(environ) -> tuple[bytes, bool, bool]:
    """Read the request body.

    Returns ``(bytes, exceeded_limit, malformed)``. A body that claims a length
    but cannot be read is reported as malformed rather than silently treated as
    an empty request, which would produce a confusing 422 instead of a 400.
    """
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except (TypeError, ValueError):
        return b"", False, True
    if length < 0:
        return b"", False, True
    if length == 0:
        # Some clients declare no length but still send a body (chunked).
        stream = environ.get("wsgi.input")
        if stream is not None:
            try:
                extra = stream.read()
            except Exception:  # pragma: no cover - defensive
                return b"", False, True
            if extra:
                return extra, False, False
        return b"", False, False
    if length > MAX_BODY_BYTES:
        stream = environ.get("wsgi.input")
        if stream is not None:
            try:
                stream.read(min(length, MAX_BODY_BYTES))
            except Exception:  # pragma: no cover - defensive
                pass
        return b"", True, False

    stream = environ.get("wsgi.input")
    if stream is None:
        return b"", False, True
    try:
        raw = stream.read(length)
    except Exception:  # pragma: no cover - defensive
        return b"", False, True
    if len(raw) < length:
        return raw, False, True
    return raw, False, False


def _make_headers(environ) -> dict:
    """Adapt WSGI's ``HTTP_*`` variables to the keys ``api.dispatch`` expects."""
    headers = {}
    for key, value in environ.items():
        if key == "CONTENT_TYPE":
            headers["Content-Type"] = value
        elif key == "CONTENT_LENGTH":
            headers["Content-Length"] = value
        elif key.startswith("HTTP_"):
            name = key[5:].replace("_", "-").title()
            headers[name] = value
    return headers


def _serve_static(path: str):
    """Serve a file from ``public/``; return ``None`` to fall through to the SPA."""
    relative = path.lstrip("/") or "index.html"
    candidate = (PUBLIC_DIR / relative).resolve()

    # Never allow traversal outside the public directory.
    if PUBLIC_DIR not in candidate.parents and candidate != PUBLIC_DIR:
        return _json_error(403, "forbidden", "That path is not available.")

    if not candidate.is_file():
        if "." in Path(relative).name:
            return _json_error(404, "not_found", "That file does not exist.")
        return None  # extensionless route â†’ serve the app shell

    try:
        data = candidate.read_bytes()
    except OSError:
        return _json_error(404, "not_found", "That file could not be read.")

    suffix = candidate.suffix.lower()
    content_type = (
        MIME_OVERRIDES.get(suffix)
        or mimetypes.guess_type(str(candidate))[0]
        or "application/octet-stream"
    )
    return 200, [("Content-Type", content_type), ("Cache-Control", "no-cache")], data


# --------------------------------------------------------------------------
# WSGI application
# --------------------------------------------------------------------------
def application(environ, start_response):
    method = (environ.get("REQUEST_METHOD") or "GET").upper()
    path = environ.get("PATH_INFO") or "/"
    query_string = environ.get("QUERY_STRING") or ""

    # --- API -----------------------------------------------------------------
    if path.startswith("/api"):
        raw, too_large, malformed = _read_body(environ)
        if too_large:
            status, headers, body = _json_error(
                413, "payload_too_large", "That request was too large. Please shorten it and try again."
            )
        elif malformed:
            status, headers, body = _json_error(
                400, "invalid_json", "Request body must be valid JSON."
            )
        else:
            body_dict = {}
            if raw:
                try:
                    body_dict = json.loads(raw.decode("utf-8") or "{}")
                except (UnicodeDecodeError, json.JSONDecodeError):
                    status, headers, body = _json_error(
                        400, "invalid_json", "Request body must be valid JSON."
                    )
                    start_response(f"{status} {_reason(status)}", _finalise(headers, body))
                    return [body]
                if not isinstance(body_dict, dict):
                    body_dict = {"value": body_dict}

            query = parse_qs(query_string, keep_blank_values=True)
            try:
                status, headers, body = api.dispatch(
                    method, path, query, body_dict, _make_headers(environ)
                )
            except api.ApiError as exc:
                status, headers, body = api.err(exc.status, exc.code, exc.message, exc.fields)
            except Exception:  # pragma: no cover - defensive
                import traceback

                traceback.print_exc()
                status, headers, body = api.err(
                    500, "internal_error", "Something went wrong on our side. Please try again."
                )

        # `api.dispatch` returns headers as a dict; normalise to a list of pairs.
        header_list = list(headers.items()) if isinstance(headers, dict) else list(headers)
        present = {key.lower() for key, _ in header_list}
        if body and "content-type" not in present:
            header_list.append(("Content-Type", "application/json; charset=utf-8"))
        if "cache-control" not in present:
            header_list.append(("Cache-Control", "no-store"))

        start_response(f"{status} {_reason(status)}", _finalise(header_list, body))
        return [body]

    # --- Static files --------------------------------------------------------
    if method not in ("GET", "HEAD"):
        status, headers, body = _json_error(
            405, "method_not_allowed", f"{method} is not supported for this resource."
        )
        start_response(f"{status} {_reason(status)}", _finalise(headers, body))
        return [body]

    served = _serve_static(path)
    if served is None:
        served = _serve_static("index.html")  # single-page-app fallback
    if served is None:  # pragma: no cover - index.html is always shipped
        status, headers, body = _json_error(500, "internal_error", "The site shell is missing.")
        start_response(f"{status} {_reason(status)}", _finalise(headers, body))
        return [body]

    status, headers, body = served
    # A HEAD response advertises the real length but sends no payload. Returning
    # an empty list here would leave the connection open, so send a zero-length
    # body with the true Content-Length already recorded in the headers.
    start_response(f"{status} {_reason(status)}", _finalise(headers, body))
    return [] if method == "HEAD" else [body]


def _finalise(headers, body: bytes = b"") -> list:
    """Add the standard security headers and a correct content length."""
    present = {k.lower() for k, _ in headers}
    final = list(headers)
    for key, value in SECURITY_HEADERS.items():
        if key.lower() not in present:
            final.append((key, value))
    if "content-length" not in present:
        final.append(("Content-Length", str(len(body))))
    return final


def _reason(status: int) -> str:
    return {
        200: "OK", 201: "Created", 204: "No Content", 400: "Bad Request",
        401: "Unauthorized", 403: "Forbidden", 404: "Not Found",
        405: "Method Not Allowed", 409: "Conflict", 413: "Payload Too Large",
        422: "Unprocessable Entity", 500: "Internal Server Error",
    }.get(status, "OK")
