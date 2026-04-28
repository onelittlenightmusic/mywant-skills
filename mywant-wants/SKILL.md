---
name: mywant-wants
description: MyWantのWant一覧取得・詳細確認・停止・再開・削除など管理操作を行う。want一覧の確認、特定wantの詳細取得・状態変更が必要なときに使用する。
metadata:
  output-format: text
---

$ARGUMENTS

引数に応じて以下のコマンドを実行し、出力をそのまま表示してください。コマンドには `2>&1 | grep -v "^\[" | grep -v "^Reading config"` を付けてログ行を除去すること。

作業ディレクトリ: `/Users/hiroyukiosaki/work/golang/mywant`

## コマンド一覧

| 操作 | コマンド |
|---|---|
| 一覧 | `./bin/mywant wants list` |
| 詳細 | `./bin/mywant wants get <ID>` |
| 履歴付き詳細 | `./bin/mywant wants get <ID> --history` |
| 停止 | `./bin/mywant wants stop <ID>` |
| 一時停止 | `./bin/mywant wants suspend <ID>` |
| 再開 | `./bin/mywant wants resume <ID>` |
| 再起動 | `./bin/mywant wants restart <ID>` |
| 削除 | `./bin/mywant wants delete <ID>` |
| エクスポート | `./bin/mywant wants export` |

引数が不足している場合は「操作を指定してください（例: list / get <ID> / stop <ID>）」と伝えてください。

## 使用例

- `/mywant-wants list` — 全want一覧を表示
- `/mywant-wants get abc123` — want詳細を表示
- `/mywant-wants stop abc123` — wantを停止
