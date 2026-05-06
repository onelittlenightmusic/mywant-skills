#!/usr/bin/env python3
"""mywant-wants: manage want executions via the MyWant Python SDK.

Input JSON (sys.argv[1] or stdin):
  {"action": "list"}
  {"action": "get",     "id": "<want id>"}
  {"action": "status",  "id": "<want id>"}
  {"action": "results", "id": "<want id>"}
  {"action": "stop",    "id": "<want id>"}
  {"action": "start",   "id": "<want id>"}
  {"action": "suspend", "id": "<want id>"}
  {"action": "resume",  "id": "<want id>"}
  {"action": "delete",  "id": "<want id>"}
  {"action": "export"}
"""
import json
import os
import sys


def progress(p: int, msg: str = "") -> None:
    print(json.dumps({"_progress": p, "_message": msg}, ensure_ascii=False), flush=True)


def out(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False), flush=True)


def err(msg: str, **kw) -> None:
    out({"ok": False, "error": msg, **kw})
    sys.exit(1)


def main() -> None:
    raw = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    try:
        arg = json.loads(raw or "{}")
    except json.JSONDecodeError as e:
        err(f"invalid JSON: {e}")
        return

    try:
        from mywant import MyWantClient
        from mywant.exceptions import APIError
    except ImportError:
        err("mywant SDK not installed — run: pip install mywant")
        return

    base = os.environ.get("MYWANT_URL", "http://localhost:8080")
    action = arg.get("action", "list")
    want_id = arg.get("id", "")

    def require_id() -> None:
        if not want_id:
            err(f"'id' is required for action={action}")

    with MyWantClient(base_url=base) as c:
        try:
            if action == "list":
                progress(20, "fetching wants...")
                wants = c.wants.list()
                progress(100, f"{len(wants)} wants")
                summaries = [{"id": w.get("metadata", {}).get("id", "?"),
                              "name": w.get("metadata", {}).get("name", "?"),
                              "type": w.get("metadata", {}).get("type", "?"),
                              "status": w.get("status", "?")} for w in wants]
                out({"ok": True, "wants": summaries, "count": len(wants)})

            elif action == "get":
                require_id()
                progress(20, f"fetching {want_id}...")
                state = c.wants.get(want_id)
                want_names = list(state.wants.keys())
                progress(100, "done")
                out({"ok": True, "id": state.id, "execution_status": state.execution_status,
                     "want_names": want_names, "results": state.results})

            elif action == "status":
                require_id()
                progress(20, f"fetching status of {want_id}...")
                st = c.wants.get_status(want_id)
                progress(100, st.status)
                out({"ok": True, "id": st.id, "status": st.status})

            elif action == "results":
                require_id()
                progress(20, f"fetching results of {want_id}...")
                res = c.wants.get_results(want_id)
                progress(100, "done")
                out({"ok": True, "id": want_id, "results": res})

            elif action in ("stop", "start", "suspend", "resume"):
                require_id()
                progress(20, f"{action} {want_id}...")
                getattr(c.wants, action)(want_id)
                progress(100, "queued")
                out({"ok": True, "id": want_id, "action": action})

            elif action == "delete":
                require_id()
                progress(20, f"deleting {want_id}...")
                c.wants.delete(want_id)
                progress(100, "deleted")
                out({"ok": True, "id": want_id})

            elif action == "export":
                progress(20, "exporting...")
                yaml_str = c.wants.export()
                progress(100, "done")
                out({"ok": True, "yaml": yaml_str})

            else:
                err(f"unknown action '{action}'. Valid: list, get, status, results, stop, start, suspend, resume, delete, export")

        except APIError as e:
            err(str(e), status_code=e.status_code)


if __name__ == "__main__":
    main()
