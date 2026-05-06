---
name: mywant-deploy
description: YAMLファイルやレシピからMyWant wantをデプロイする。新しいwantの作成・レシピ一覧の確認・設定ファイルからのデプロイが必要なときに使用する。
metadata:
  output-format: text
---

$ARGUMENTS

引数に応じて以下のコマンドを実行し、出力をそのまま表示してください。コマンドには `2>&1 | grep -v "^\[" | grep -v "^Reading config"` を付けてログ行を除去すること。

作業ディレクトリ: `/Users/hiroyukiosaki/work/golang/mywant`

## コマンド一覧

| 操作 | コマンド |
|---|---|
| YAMLからデプロイ | `./bin/mywant wants create -f <YAML_PATH>` |
| 設定ファイル一覧 | `ls yaml/config/` |
| レシピ一覧 | `./bin/mywant recipes list` |
| レシピ詳細 | `./bin/mywant recipes get <NAME>` |
| インタラクティブ作成 | `./bin/mywant wants create -i` |

### 主要な設定ファイル

| ファイル | 内容 |
|---|---|
| `yaml/config/config-travel.yaml` | 旅行計画（フライト+ホテル） |
| `yaml/config/config-queue-system.yaml` | キューシステムデモ |
| `yaml/config/config-qnet.yaml` | マルチストリームデモ |

引数が不足している場合は「操作を指定してください（例: deploy yaml/config/config-travel.yaml / recipes list）」と伝えてください。

## インライン YAML デプロイ

引数にYAMLコンテンツが直接渡された場合（`wants:` で始まる文字列など）、`/tmp/mywant-deploy-<timestamp>.yaml` に書き出してからデプロイしてください。

```
# 例: このような呼び出し
/mywant-deploy
wants:
  - metadata:
      name: open-all-hall-doors
      type: batch
    spec:
      params:
        child_type: rpg_try_keys
        targets: [hall-door-03, hall-door-04]
```

手順:
1. `/tmp/mywant-deploy-<timestamp>.yaml` にYAMLを書き出す（Write ツール使用）
2. `./bin/mywant wants create -f /tmp/mywant-deploy-<timestamp>.yaml` を実行
3. 結果を表示

## 使用例

- `/mywant-deploy yaml/config/config-travel.yaml` — 旅行wantをデプロイ
- `/mywant-deploy recipes list` — 利用可能なレシピ一覧を表示
- `/mywant-deploy recipes get travel` — レシピ詳細を確認してからデプロイ
- `/mywant-deploy wants:\n  - metadata:\n      name: ...` — インラインYAMLでデプロイ
