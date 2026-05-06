---
name: save-as-want
description: スキルが mywant の machine-readable skill として成立しているか検証し、want type YAML を生成・登録する。
compatibility:
  python: ">=3.9"
metadata:
  type-name: save_as_want
  category: mywant
  final-result-field: summary
---

`${CLAUDE_SKILL_DIR}/main.py` に JSON 引数を渡す。

```bash
python3 "${CLAUDE_SKILL_DIR}/main.py" $ARGUMENTS
```

---

## アクション一覧

### `check` — machine-readable 判定

スキルが mywant agent として成立しているか検証する。

**判定基準（すべて満たすこと）**:
1. スキルディレクトリが `~/.claude/skills/` または `~/.mywant/custom-types/` 以下に存在する
2. `agent.yaml` が存在し、以下のフィールドを含む:
   - `agent.name` — エージェント名
   - `agent.type` — `do` または `monitor`
   - `agent.script` — 実在する実行可能スクリプト
   - `agent.state_updates` — 出力フィールドのマッピング（1件以上）
3. 参照スクリプトが実行可能（`chmod +x`）

```json
{"action": "check", "skill": "rpg-try-keys"}
```

**出力**:
```json
{
  "ok": true,
  "machine_readable": true,
  "skill": "rpg-try-keys",
  "skill_dir": "/path/to/skill",
  "checks": {
    "skill_found": true,
    "has_agent_yaml": true,
    "agent_yaml_parseable": true,
    "has_agent_name": true,
    "agent_type_valid": true,
    "has_script_field": true,
    "script_exists": true,
    "script_executable": true,
    "has_state_updates": true,
    "state_updates_count": 5
  },
  "issues": [],
  "agent_name": "rpg_try_keys_agent",
  "agent_type": "do",
  "type_name": "rpg_try_keys",
  "already_registered": false
}
```

---

### `create-type` — want type YAML 生成・登録

`check` が通ったスキルに対して want type YAML を作成し、オプションで mywant に登録する。

**重要**: `type_definition` は**呼び出し元 LLM が生成する**。
スキルの `SKILL.md`・`main.py`・`agent.yaml` を読んで JSON で渡すこと。

```json
{
  "action": "create-type",
  "skill": "my-skill",
  "install": true,
  "type_definition": {
    "metadata": {
      "name": "my_skill",
      "title": "My Skill",
      "description": "何をするスキルか",
      "version": "1.0",
      "category": "...",
      "pattern": "independent"
    },
    "finalResultField": "summary",
    "parameters": [
      {"name": "target", "type": "string", "required": true, "description": "対象"}
    ],
    "state": [
      {"name": "skill_json_arg", "type": "string", "label": "current", "persistent": false, "initialValue": ""},
      {"name": "ok",             "type": "bool",   "label": "current", "persistent": true,  "initialValue": false},
      {"name": "error",          "type": "string", "label": "current", "persistent": true,  "initialValue": ""},
      {"name": "summary",        "type": "string", "label": "current", "persistent": true,  "initialValue": ""}
    ],
    "finalizeWhen": {
      "achieved": {"field": "ok",    "operator": "==", "value": true},
      "failed":   {"field": "error", "operator": "!=", "value": ""}
    },
    "onInitialize": {
      "current": {
        "skill_json_arg": "{\"target\":\"${target}\"}"
      }
    },
    "requires": ["my_skill"]
  }
}
```

**Python がやること**:
- `type_definition` を `wantType:` でラップして YAML 変換
- `<skill_dir>/<type_name>.yaml` に書き込み
- `install: true` なら `POST /api/v1/want-types` で即時登録（ホットリロード）

**LLM がやること**:
- スキルの `SKILL.md`・`main.py` を読んでパラメータ・出力フィールドを理解
- `state`・`parameters`・`finalizeWhen`・`onInitialize` を設計して渡す

**出力**:
```json
{
  "ok": true,
  "type_name": "my_skill",
  "yaml_path": "/path/to/skill/my_skill.yaml",
  "installed": true
}
```

---

## 典型的な使い方（LLM 向け手順）

1. `check` でスキルが machine-readable か確認する
2. `issues` が空でなければ `agent.yaml` を修正してから再実行
3. `check` が通ったら、スキルの `SKILL.md` と `main.py` を読む
4. want type 定義 JSON を設計し、`create-type` に渡す
5. `already_registered: false` なら `install: true` で即時登録

---

## `type_definition` 設計ガイド（LLM 向け）

| フィールド | 参照元 | 注意 |
|---|---|---|
| `metadata.name` | `agent.yaml` の `agent.name` から `_agent` を除いたもの | スネークケース |
| `parameters` | `SKILL.md` のパラメータ表 / `main.py` の引数処理 | |
| `state` | `agent.yaml` の `state_updates` + 必要な中間フィールド | `skill_json_arg` は必須 |
| `finalizeWhen.achieved` | `ok == true` が多い | スキルの成功条件による |
| `onInitialize.skill_json_arg` | `main.py` が受け取る JSON を `${param}` で組み立て | |
| `requires` | `[type_name]` — mywant がエージェントを探す際のキー | |
