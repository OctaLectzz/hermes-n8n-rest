"""REST API client and Hermes tool handlers for n8n."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_TIMEOUT = 20
MAX_RESPONSE_BYTES = 2_000_000


class N8NRestError(Exception):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


def _configuration() -> tuple[str, str]:
    base_url = os.environ.get("N8N_BASE_URL", "").strip().rstrip("/")
    api_key = os.environ.get("N8N_API_KEY", "").strip()
    if not base_url or not api_key:
        raise N8NRestError(
            "N8N_BASE_URL and N8N_API_KEY must be configured in the Hermes environment."
        )
    parsed = urllib.parse.urlparse(base_url)
    if parsed.scheme != "https" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise N8NRestError("N8N_BASE_URL must use HTTPS except for localhost testing.")
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or not parsed.hostname:
        raise N8NRestError("N8N_BASE_URL is not a valid HTTP(S) URL.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise N8NRestError(
            "N8N_BASE_URL must not contain URL credentials, a query string, or a fragment."
        )
    return base_url, api_key


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Never forward the API-key header to a redirect destination."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _request(method: str, path: str, payload: dict | None = None) -> dict:
    base_url, api_key = _configuration()
    url = base_url + "/api/v1/" + path.lstrip("/")
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": "application/json",
        "X-N8N-API-KEY": api_key,
        "User-Agent": "hermes-n8n-rest/0.1.0",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    opener = urllib.request.build_opener(_NoRedirectHandler)
    try:
        with opener.open(request, timeout=DEFAULT_TIMEOUT) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise N8NRestError("n8n response exceeded the 2 MB safety limit.")
            if not raw:
                return {"status": response.status, "data": None}
            try:
                return json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise N8NRestError("n8n returned a response that was not valid JSON.")
    except urllib.error.HTTPError as exc:
        # Do not include request headers or credentials in returned errors.
        detail = ""
        try:
            raw = exc.read(4096).decode("utf-8", errors="replace")
            parsed = json.loads(raw)
            detail = str(parsed.get("message") or parsed.get("error") or "")
        except Exception:
            pass
        safe_detail = detail[:300] if detail else "n8n rejected the request."
        raise N8NRestError(f"n8n REST API returned HTTP {exc.code}: {safe_detail}", exc.code) from None
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", "connection error")
        raise N8NRestError(f"Could not reach n8n REST API: {reason}") from None
    except TimeoutError:
        raise N8NRestError("n8n REST API request timed out.") from None


def _workflow_id(args: dict) -> str:
    value = args.get("workflow_id")
    if not isinstance(value, str) or not value.strip():
        raise N8NRestError("workflow_id must be a non-empty string.")
    return urllib.parse.quote(value.strip(), safe="")


def _run(fn):
    def handler(args: dict | None = None, **kwargs: Any) -> str:
        try:
            result = fn(dict(args or {}))
            return json.dumps({"ok": True, "result": result}, ensure_ascii=False)
        except N8NRestError as exc:
            return json.dumps(
                {"ok": False, "error": str(exc), "status": exc.status},
                ensure_ascii=False,
            )
        except Exception:
            # Keep unexpected internals out of the model-visible response.
            return json.dumps(
                {"ok": False, "error": "Unexpected plugin error. Check Hermes logs."},
                ensure_ascii=False,
            )
    return handler


def list_workflows(args: dict) -> dict:
    limit = args.get("limit", 50)
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
        raise N8NRestError("limit must be an integer between 1 and 100.")
    query = {"limit": limit}
    cursor = args.get("cursor")
    if cursor is not None:
        if not isinstance(cursor, str) or not cursor.strip():
            raise N8NRestError("cursor must be a non-empty string when provided.")
        query["cursor"] = cursor
    return _request("GET", "workflows?" + urllib.parse.urlencode(query))


def get_workflow(args: dict) -> dict:
    return _request("GET", "workflows/" + _workflow_id(args))


def create_workflow(args: dict) -> dict:
    workflow = args.get("workflow")
    if not isinstance(workflow, dict):
        raise N8NRestError("workflow must be a JSON object.")
    if not isinstance(workflow.get("name"), str) or not isinstance(workflow.get("nodes"), list) or not isinstance(workflow.get("connections"), dict):
        raise N8NRestError("workflow must include name (string), nodes (array), and connections (object).")
    return _request("POST", "workflows", workflow)


def update_workflow(args: dict) -> dict:
    workflow_id = _workflow_id(args)
    workflow = args.get("workflow")
    if not isinstance(workflow, dict):
        raise N8NRestError("workflow must be a JSON object.")
    if "name" in workflow and not isinstance(workflow["name"], str):
        raise N8NRestError("workflow.name must be a string.")
    if "nodes" in workflow and not isinstance(workflow["nodes"], list):
        raise N8NRestError("workflow.nodes must be an array.")
    if "connections" in workflow and not isinstance(workflow["connections"], dict):
        raise N8NRestError("workflow.connections must be an object.")
    return _request("PUT", "workflows/" + workflow_id, workflow)


def set_workflow_active(args: dict) -> dict:
    workflow_id = _workflow_id(args)
    active = args.get("active")
    if not isinstance(active, bool):
        raise N8NRestError("active must be a boolean.")
    action = "activate" if active else "deactivate"
    return _request("POST", "workflows/" + workflow_id + "/" + action)


HANDLERS = {
    "n8n_rest_list_workflows": _run(list_workflows),
    "n8n_rest_get_workflow": _run(get_workflow),
    "n8n_rest_create_workflow": _run(create_workflow),
    "n8n_rest_update_workflow": _run(update_workflow),
    "n8n_rest_set_workflow_active": _run(set_workflow_active),
}
