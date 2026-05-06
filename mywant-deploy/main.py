#!/usr/bin/env python3
"""mywant-deploy: deploy wants via the MyWant Python SDK.

Input JSON (sys.argv[1] or stdin):
  {"action": "create",       "yaml": "<yaml string>", "name": "<optional>"}
  {"action": "validate",     "yaml": "<yaml string>"}
  {"action": "recipes-list"}
  {"action": "recipe-get",   "name": "<recipe id>"}
  {"action": "recipe-create-from-want", "want_id": "<id>", "name": "<name>"}
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
    action = arg.get("action", "create")

    with MyWantClient(base_url=base) as c:
        try:
            if action == "create":
                yaml_str = arg.get("yaml", "")
                if not yaml_str:
                    err("'yaml' field is required for action=create")
                    return
                progress(20, "deploying want...")
                ex = c.wants.create(yaml_str, name=arg.get("name"))
                progress(100, f"created {ex.id}")
                out({"ok": True, "id": ex.id, "status": ex.status})

            elif action == "validate":
                yaml_str = arg.get("yaml", "")
                if not yaml_str:
                    err("'yaml' field is required for action=validate")
                    return
                progress(20, "validating...")
                result = c.wants.validate(yaml_str)
                progress(100, "validated")
                out({"ok": result.valid, "valid": result.valid,
                     "fatal_errors": result.fatal_errors,
                     "warnings": result.warnings,
                     "want_count": result.want_count})

            elif action == "recipes-list":
                progress(20, "fetching recipes...")
                recipes = c.recipes.list()
                names = list(recipes.keys()) if isinstance(recipes, dict) else []
                progress(100, f"{len(names)} recipes")
                out({"ok": True, "recipes": recipes, "count": len(names)})

            elif action == "recipe-get":
                name = arg.get("name", "")
                if not name:
                    err("'name' is required for action=recipe-get")
                    return
                progress(20, f"fetching recipe {name}...")
                recipe = c.recipes.get(name)
                progress(100, "done")
                out({"ok": True, "recipe": recipe})

            elif action == "recipe-create-from-want":
                want_id = arg.get("want_id", "")
                name = arg.get("name", "")
                if not want_id or not name:
                    err("'want_id' and 'name' are required")
                    return
                progress(20, "saving recipe...")
                c.recipes.create_from_want(want_id, name,
                    description=arg.get("description", ""),
                    version=arg.get("version", "1.0.0"))
                progress(100, "done")
                out({"ok": True, "name": name})

            else:
                err(f"unknown action '{action}'. Valid: create, validate, recipes-list, recipe-get, recipe-create-from-want")

        except APIError as e:
            err(str(e), status_code=e.status_code)


if __name__ == "__main__":
    main()
