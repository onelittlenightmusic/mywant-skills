---
name: mywant-agents
description: MyWantのエージェント・ケイパビリティ・Wantタイプの一覧取得と詳細確認。登録済みエージェントや利用可能なケイパビリティを確認するときに使用する。**wantをデプロイする前に、そのタイプが登録済みか必ずここで確認すること。**
metadata:
  output-format: json
---

$ARGUMENTS

引数は JSON 形式で `main.py` に渡します。引数省略時は `{"action":"agents-list"}` とみなします。

## アクション一覧

| action | 追加フィールド | 説明 |
|---|---|---|
| `agents-list` | — | 登録済みエージェント一覧 |
| `agents-get` | `name` | エージェント詳細 |
| `capabilities-list` | — | 全ケイパビリティ一覧 |
| `capabilities-get` | `name` | ケイパビリティ詳細 |
| `types-list` | — | **登録済み want type 一覧**（デプロイ前の確認に使う） |
| `types-get` | `name` | want type の詳細定義 |

## want type の存在確認（重要）

want をデプロイする前に、そのタイプがサーバーに登録されているか確認してください。
登録されていないタイプを使うとデプロイは失敗します。

```json
{"action": "types-list"}
```

出力例（`types` 配列に登録済みタイプ名が並ぶ）:
```json
{"ok": true, "types": [{"name": "rpg_try_keys"}, {"name": "rpg_control"}, ...], "count": 70}
```

特定タイプの存在を確認:
```json
{"action": "types-get", "name": "rpg_try_keys"}
```

## 使用例

- `{"action":"types-list"}` — 全 want type を一覧（デプロイ前確認）
- `{"action":"types-get","name":"rpg_observe"}` — want type の定義を確認
- `{"action":"agents-list"}` — 全エージェント一覧を表示
- `{"action":"capabilities-list"}` — 全ケイパビリティ一覧を表示
- `{"action":"agents-get","name":"rpg_control_agent"}` — エージェント詳細を表示
