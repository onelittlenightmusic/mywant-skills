---
name: mywant-deploy
description: YAMLからMyWant wantをデプロイ・バリデーション、レシピ管理を行う。新しいwantの作成・レシピ一覧の確認・設定ファイルからのデプロイが必要なときに使用する。
metadata:
  output-format: json
---

$ARGUMENTS

引数は JSON 形式で `main.py` に渡します。

## 重要: デプロイ前に want type を確認すること

存在しない type を指定するとデプロイが失敗します。
デプロイ前に `/mywant-agents` で `{"action":"types-list"}` を実行して type 名を確認してください。

## アクション一覧

| action | 追加フィールド | 説明 |
|---|---|---|
| `create` | `yaml` (必須), `name` (任意) | YAML文字列からwantをデプロイ |
| `validate` | `yaml` (必須) | デプロイせずにYAMLを検証 |
| `recipes-list` | — | 登録済みレシピ一覧 |
| `recipe-get` | `name` | レシピ詳細を取得 |
| `recipe-create-from-want` | `want_id`, `name`, `description`, `version` | 実行中wantからレシピを保存 |

## 使用例

```json
{"action": "create", "yaml": "wants:\n  - metadata:\n      name: my-want\n      type: rpg_control\n    spec:\n      params: {}"}
```

```json
{"action": "validate", "yaml": "wants:\n  - metadata:\n      name: test\n      type: rpg_observe\n    spec:\n      params: {}"}
```

```json
{"action": "recipes-list"}
```

```json
{"action": "recipe-get", "name": "Queue System"}
```

## キャラクターの近くにデプロイする

want は既定では作成順に空きセルへ並べられるため、キャンバス上でプレイヤーから
遠く離れた場所に出ます。デプロイ先を「誰かの隣」にしたいときは
`mywant.io/canvas-near` ラベルを付けます。座標はサーバーが**デプロイ時点の**
位置から解決するので、YAML 側が座標を知っている必要はありません。

```yaml
wants:
  - metadata:
      name: door-03-keys
      type: rpg_try_keys
      labels:
        mywant.io/canvas-near: chr-9eca4b3d   # キャラクターID、または "cursor"
    spec:
      params: {}
```

- 値はキャラクターID。「今操作している人の隣」でよければ `cursor`（ライブカーソルの
  うち最後に動いたものを見ます。誰も操作していなければ CursorMan、それも盤面に
  出ていなければ通常配置）。
- 置かれるのは**隣接セル**で、本人が立っているセルではありません。
- 隣が埋まっていれば外側へ探索します。複数まとめてデプロイしても重なりません。
- `mywant.io/canvas-x` / `canvas-y` を明示した場合はそちらが優先されます。
- 該当キャラクターが見つからない場合はエラーにならず、通常の自動配置になります。

## インライン YAML デプロイのフロー

1. `/mywant-agents` で `{"action":"types-list"}` → 使いたい type が存在するか確認
2. `/mywant-deploy` で `{"action":"validate", "yaml": "..."}` → 文法エラーがないか確認
3. `/mywant-deploy` で `{"action":"create", "yaml": "..."}` → デプロイ実行

## スキルが利用できない場合

もし `mywant-deploy` スキルが見つからない場合は、MyWantが適切にインストールされているか確認してください。以下のコマンドでスキルのインストールが可能です:

```bash
mywant skills install gemini
# または
mywant skills install claude
```

これにより、必要なエージェント機能が環境にセットアップされます。
