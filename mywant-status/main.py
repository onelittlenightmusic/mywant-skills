#!/usr/bin/env python3
"""mywant-status: check MyWant server health via the Python SDK.

No required arguments. Returns health, want count, version.
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
    try:
        from mywant import MyWantClient
        from mywant.exceptions import APIError
    except ImportError:
        err("mywant SDK not installed — run: pip install mywant")
        return

    base = os.environ.get("MYWANT_URL", "http://localhost:8080")

    progress(20, "checking health...")
    try:
        with MyWantClient(base_url=base) as c:
            h = c.system.health()
        progress(100, h.status)
        out({"ok": True, "status": h.status, "wants": h.wants,
             "version": h.version, "server": h.server})
    except APIError as e:
        err(str(e), status_code=e.status_code)
    except Exception as e:
        err(f"cannot reach mywant server at {base}: {e}")


if __name__ == "__main__":
    main()
