---
name: mywant-agents
description: MyWantエージェント・ケイパビリティ・Wantタイプの一覧取得と詳細確認。登録済みエージェントや利用可能なケイパビリティを確認するときに使用する。
metadata:
  output-format: text
---

$ARGUMENTS

引数に応じて以下のコマンドを実行し、出力をそのまま表示してください。コマンドには `2>&1 | grep -v "^\[" | grep -v "^Reading config"` を付けてログ行を除去すること。

作業ディレクトリ: `/Users/hiroyukiosaki/work/golang/mywant`

## コマンド一覧

| 操作 | コマンド |
|---|---|
| エージェント一覧 | `./bin/mywant agents list` |
| エージェント詳細 | `./bin/mywant agents get <NAME>` |
| ケイパビリティ一覧 | `./bin/mywant capabilities list` |
| Wantタイプ一覧 | `./bin/mywant types list` |

引数が不足している場合は「操作を指定してください（例: agents list / capabilities list / types list）」と伝えてください。

## 使用例

- `/mywant-agents agents list` — 全エージェント一覧を表示
- `/mywant-agents capabilities list` — 全ケイパビリティ一覧を表示
- `/mywant-agents types list` — 登録済みWantタイプ一覧を表示
- `/mywant-agents agents get flight_agent` — エージェント詳細を表示
