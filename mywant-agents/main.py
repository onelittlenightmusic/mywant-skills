#!/usr/bin/env python3
"""mywant-agents: list agents, capabilities, and want-types via the Python SDK.

Input JSON (sys.argv[1] or stdin):
  {"action": "agents-list"}
  {"action": "agents-get",        "name": "<agent name>"}
  {"action": "capabilities-list"}
  {"action": "capabilities-get",  "name": "<capability name>"}
  {"action": "types-list"}
  {"action": "types-get",         "name": "<type name>"}
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
    action = arg.get("action", "agents-list")
    name = arg.get("name", "")

    with MyWantClient(base_url=base) as c:
        try:
            if action == "agents-list":
                progress(20, "fetching agents...")
                items = c.agents.list()
                progress(100, f"{len(items)} agents")
                out({"ok": True, "agents": items, "count": len(items)})

            elif action == "agents-get":
                if not name:
                    err("'name' is required for action=agents-get")
                    return
                progress(20, f"fetching agent {name}...")
                agent = c.agents.get(name)
                progress(100, "done")
                out({"ok": True, "agent": {"name": agent.name, "type": agent.type, "capabilities": agent.capabilities}})

            elif action == "capabilities-list":
                progress(20, "fetching capabilities...")
                items = c.capabilities.list()
                progress(100, f"{len(items)} capabilities")
                out({"ok": True, "capabilities": items, "count": len(items)})

            elif action == "capabilities-get":
                if not name:
                    err("'name' is required for action=capabilities-get")
                    return
                progress(20, f"fetching capability {name}...")
                cap = c.capabilities.get(name)
                progress(100, "done")
                out({"ok": True, "capability": {"name": cap.name, "gives": cap.gives}})

            elif action == "types-list":
                progress(20, "fetching want types...")
                items = c.want_types.list()
                progress(100, f"{len(items)} types")
                out({"ok": True, "types": items, "count": len(items)})

            elif action == "types-get":
                if not name:
                    err("'name' is required for action=types-get")
                    return
                progress(20, f"fetching type {name}...")
                t = c.want_types.get(name)
                progress(100, "done")
                out({"ok": True, "type": t})

            else:
                err(f"unknown action '{action}'. Valid: agents-list, agents-get, capabilities-list, capabilities-get, types-list, types-get")

        except APIError as e:
            err(str(e), status_code=e.status_code)


if __name__ == "__main__":
    main()
