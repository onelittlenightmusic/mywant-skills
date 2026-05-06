#!/usr/bin/env python3
"""save-as-want: check skill machine-readability and create want type YAML.

Actions:
  check        -- verify a skill is machine-readable (has valid agent.yaml + script)
  create-type  -- given skill + LLM-generated type_definition JSON, write want type
                  YAML and optionally install via POST /api/v1/want-types
"""
import json
import os
import sys
from typing import Optional, Tuple
import yaml


SEARCH_DIRS = [
    os.path.expanduser("~/.claude/skills"),
    os.path.expanduser("~/.mywant/custom-types"),
]


def progress(p: int, msg: str = "") -> None:
    print(json.dumps({"_progress": p, "_message": msg}, ensure_ascii=False), flush=True)


def out(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False), flush=True)


def err(msg: str, **kw) -> None:
    out({"ok": False, "error": msg, **kw})
    sys.exit(1)


# ── skill discovery ───────────────────────────────────────────────────────────

def find_skill_dir(name: str) -> Optional[str]:
    for base in SEARCH_DIRS:
        candidate = os.path.join(base, name)
        if os.path.isdir(candidate):
            return candidate
        # also search one level deeper (e.g. mywant-skills/mywant-deploy)
        for sub in os.listdir(base) if os.path.isdir(base) else []:
            deep = os.path.join(base, sub, name)
            if os.path.isdir(deep):
                return deep
    return None


# ── check ────────────────────────────────────────────────────────────────────

def do_check(skill_name: str) -> dict:
    """
    Verify whether a skill qualifies as a mywant machine-readable skill.

    Criteria:
      1. Skill directory found in known locations
      2. agent.yaml exists and contains required fields
         - agent.name   (string)
         - agent.type   ("do" | "monitor")
         - agent.script (file that exists relative to skill dir)
         - agent.state_updates (list, at least one entry)
      3. Referenced script exists and is executable

    Returns a structured result so the calling LLM can understand what's missing.
    """
    skill_dir = find_skill_dir(skill_name)
    checks: dict = {}
    issues: list[str] = []

    # 1. Directory
    checks["skill_found"] = skill_dir is not None
    if not skill_dir:
        issues.append(f"skill directory '{skill_name}' not found in {SEARCH_DIRS}")
        return _check_result(False, skill_name, None, checks, issues)

    # 2. agent.yaml
    agent_yaml_path = os.path.join(skill_dir, "agent.yaml")
    checks["has_agent_yaml"] = os.path.isfile(agent_yaml_path)
    if not checks["has_agent_yaml"]:
        issues.append("agent.yaml not found — required for mywant agent registration")
        return _check_result(False, skill_name, skill_dir, checks, issues)

    try:
        with open(agent_yaml_path) as f:
            agent_def = yaml.safe_load(f)
    except Exception as e:
        checks["agent_yaml_parseable"] = False
        issues.append(f"agent.yaml parse error: {e}")
        return _check_result(False, skill_name, skill_dir, checks, issues)

    checks["agent_yaml_parseable"] = True
    agent = agent_def.get("agent", {})
    meta = agent.get("metadata", {})

    # 2a. agent.name — supports both agent.name and agent.metadata.name
    agent_name = agent.get("name") or meta.get("name", "")
    checks["has_agent_name"] = bool(agent_name)
    if not checks["has_agent_name"]:
        issues.append("agent.yaml missing agent.name (or agent.metadata.name)")

    # 2b. agent.type — supports both agent.type and agent.metadata.type
    agent_type = agent.get("type") or meta.get("type", "")
    checks["agent_type_valid"] = agent_type in ("do", "monitor")
    if not checks["agent_type_valid"]:
        issues.append(f"agent.type must be 'do' or 'monitor', got: {agent_type!r}")

    # 2c. agent.script — supports agent.script (string) or agent.script.path (dict)
    script_field = agent.get("script", "")
    if isinstance(script_field, dict):
        script_rel = script_field.get("path", "")
    else:
        script_rel = script_field
    script_path = os.path.join(skill_dir, script_rel) if script_rel else ""
    checks["has_script_field"] = bool(script_rel)
    checks["script_exists"] = os.path.isfile(script_path) if script_path else False
    checks["script_executable"] = os.access(script_path, os.X_OK) if checks["script_exists"] else False
    if not checks["has_script_field"]:
        issues.append("agent.yaml missing agent.script")
    elif not checks["script_exists"]:
        issues.append(f"script '{script_rel}' referenced in agent.yaml does not exist")
    elif not checks["script_executable"]:
        issues.append(f"script '{script_rel}' is not executable (chmod +x)")

    # 2d. agent.state_updates
    state_updates = agent.get("state_updates", [])
    checks["has_state_updates"] = isinstance(state_updates, list) and len(state_updates) > 0
    checks["state_updates_count"] = len(state_updates) if isinstance(state_updates, list) else 0
    if not checks["has_state_updates"]:
        issues.append("agent.state_updates is empty — define output field mappings")

    # Check if want type already registered
    type_name = _infer_type_name(skill_dir, agent_name)
    already_registered = _is_type_registered(type_name) if type_name else False

    machine_readable = not issues
    return _check_result(machine_readable, skill_name, skill_dir, checks, issues,
                         agent_name=agent_name, agent_type=agent_type,
                         type_name=type_name, already_registered=already_registered)


def _check_result(ok: bool, skill: str, skill_dir, checks: dict, issues: list, **extra) -> dict:
    return {
        "ok": ok,
        "machine_readable": ok,
        "skill": skill,
        "skill_dir": skill_dir,
        "checks": checks,
        "issues": issues,
        **extra,
    }


def _infer_type_name(skill_dir: str, agent_name: str) -> Optional[str]:
    # Look for an existing wantType YAML in the skill dir
    for fname in os.listdir(skill_dir):
        if not fname.endswith(".yaml") or fname == "agent.yaml":
            continue
        try:
            with open(os.path.join(skill_dir, fname)) as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict) and "wantType" in data:
                return data["wantType"].get("metadata", {}).get("name")
        except Exception:
            pass
    # Fall back: strip "_agent" suffix from agent name
    if agent_name.endswith("_agent"):
        return agent_name[:-6]
    return None


def _is_type_registered(type_name: str) -> bool:
    try:
        import urllib.request
        base = os.environ.get("MYWANT_URL", "http://localhost:8080")
        url = f"{base}/api/v1/want-types/{type_name}"
        req = urllib.request.urlopen(url, timeout=3)
        return req.status == 200
    except Exception:
        return False


# ── create-type ───────────────────────────────────────────────────────────────

def do_create_type(skill_name: str, type_definition: dict, install: bool, output_path: Optional[str]) -> dict:
    """
    Convert LLM-generated type_definition JSON → wantType YAML,
    write to skill dir, and optionally POST to /api/v1/want-types.

    type_definition is the content INSIDE wantType: (metadata, parameters, state, ...).
    The caller (LLM) generates this by reading the skill's SKILL.md and main.py.
    """
    if not type_definition:
        err("type_definition is required and must be non-empty")

    type_name = type_definition.get("metadata", {}).get("name", "")
    if not type_name:
        err("type_definition.metadata.name is required")

    # Wrap in wantType: envelope
    wrapped = {"wantType": type_definition}
    yaml_str = yaml.dump(wrapped, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # Determine output path
    if output_path:
        dest = os.path.expanduser(output_path)
    else:
        skill_dir = find_skill_dir(skill_name)
        if not skill_dir:
            err(f"skill directory '{skill_name}' not found")
        dest = os.path.join(skill_dir, f"{type_name}.yaml")

    progress(30, f"writing {dest}")
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    with open(dest, "w") as f:
        f.write(yaml_str)

    installed = False
    install_error = None
    if install:
        progress(60, f"installing {type_name} via API")
        installed, install_error = _install_type(yaml_str)

    progress(100, "done")
    result: dict = {
        "ok": True,
        "type_name": type_name,
        "yaml_path": dest,
        "installed": installed,
    }
    if install_error:
        result["install_error"] = install_error
        result["ok"] = False
    return result


def _install_type(yaml_str: str) -> Tuple[bool, Optional[str]]:
    try:
        import urllib.request
        base = os.environ.get("MYWANT_URL", "http://localhost:8080")
        data = yaml_str.encode()
        req = urllib.request.Request(
            f"{base}/api/v1/want-types",
            data=data,
            headers={"Content-Type": "application/yaml"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            result = json.loads(body)
            return result.get("name") is not None, None
    except Exception as e:
        return False, str(e)


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    raw = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    try:
        arg = json.loads(raw or "{}")
    except json.JSONDecodeError as e:
        err(f"invalid JSON input: {e}")
        return

    action = arg.get("action", "check")

    if action == "check":
        skill = arg.get("skill", "")
        if not skill:
            err("'skill' field is required for action=check")
        out(do_check(skill))

    elif action == "create-type":
        skill = arg.get("skill", "")
        type_def = arg.get("type_definition", {})
        install = arg.get("install", False)
        output_path = arg.get("output_path")
        if not skill:
            err("'skill' field is required for action=create-type")
        out(do_create_type(skill, type_def, install, output_path))

    else:
        err(f"unknown action: {action!r}. Use: check | create-type")


if __name__ == "__main__":
    main()
