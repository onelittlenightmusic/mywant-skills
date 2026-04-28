# mywant-skills

Claude Code skills for the [mywant](https://github.com/onelittlenightmusic/mywant) declarative workflow system.

## Skills

| Skill | Description |
|---|---|
| `mywant-wants` | List, inspect, stop, resume, restart, delete, and export wants |
| `mywant-agents` | List agents, capabilities, and want types |
| `mywant-deploy` | Deploy wants from YAML config files or recipes |
| `mywant-status` | Check server, worker, GUI, and mock flight server status |

## Installation

Link each skill directory into your project's `.claude/skills/` directory:

```bash
MYWANT_SKILLS=~/.mywant/custom-types/mywant-skills
PROJECT=~/work/golang/mywant  # your mywant project root

mkdir -p "$PROJECT/.claude/skills"
for skill in mywant-wants mywant-agents mywant-deploy mywant-status; do
  ln -s "$MYWANT_SKILLS/$skill" "$PROJECT/.claude/skills/$skill"
done
```

## Usage in Claude Code

Invoke skills with `/` prefix inside a Claude Code session:

```
/mywant-wants list
/mywant-wants get <id>
/mywant-wants stop <id>
/mywant-wants restart <id>

/mywant-agents

/mywant-deploy

/mywant-status
```

## Requirements

- [mywant](https://github.com/onelittlenightmusic/mywant) server running (`./bin/mywant start -D`)
- `mywant` CLI available in PATH or as `./bin/mywant` in the project root
- [Claude Code](https://claude.ai/code) CLI
