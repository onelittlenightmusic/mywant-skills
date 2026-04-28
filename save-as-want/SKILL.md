---
name: save-as-want
description: 会話中に使用したskillの内容をMyWantにメモとして保存し、対応するwantタイプがあればwantとしてデプロイする。
metadata:
  output-format: text
---

$ARGUMENTS

## 目的

会話中に使用したskillの内容をMyWantに記録する。

1. **メモ保存**: `~/.mywant/skill-usage-log.md` に使用履歴を追記
2. **Want生成**: 対応するwantタイプがあればYAMLを生成してデプロイ

作業ディレクトリ: `/Users/hiroyukiosaki/work/MyWant`

---

## 処理手順

### Step 1: コンテキストの収集

引数 (`$ARGUMENTS`) から、または引数が空の場合は**直前の会話内容**から以下を推定してください:

| フィールド | 説明 | 例 |
|---|---|---|
| `skill_name` | 使用したskillの名前 | `mywant-deploy`, `mywant-wants` |
| `summary` | 何をしたか（1〜2行） | `config-travel.yamlからtravel wantをデプロイした` |
| `params` | 使用した主要パラメータ | `yaml: config-travel.yaml` |
| `result` | 実行結果の概要 | `成功: want ID abc123が生成された` |

引数形式の例:
- `skill=mywant-deploy context="travel wantをデプロイ" params="config-travel.yaml"` — 明示的指定
- `mywant-deploy travel yaml/config/config-travel.yaml` — 位置引数として解析
- (空) — 直前の会話から自動推定

---

### Step 2: メモの保存

以下のコマンドでメモを `~/.mywant/skill-usage-log.md` に追記してください:

```bash
LOGFILE=~/.mywant/skill-usage-log.md
[ -f "$LOGFILE" ] || printf "# MyWant Skill Usage Log\n\n" > "$LOGFILE"
cat >> "$LOGFILE" << 'ENTRY'

## {YYYY-MM-DD HH:MM} — {skill_name}

**Summary**: {summary}
**Params**: {params}
**Result**: {result}

ENTRY
```

`{YYYY-MM-DD HH:MM}` には `date '+%Y-%m-%d %H:%M'` の出力を使ってください。

---

### Step 3: 対応するWantタイプの確認

```bash
cd /Users/hiroyukiosaki/work/MyWant && ./bin/mywant types list 2>&1 | grep -v "^\[" | grep -v "^Reading config"
```

出力されたタイプ一覧と会話コンテキストを照合し、デプロイ可能なwantタイプを判定してください。

**マッピングの判定基準:**

| 会話内容・skill | 候補wantタイプ | デプロイ判断 |
|---|---|---|
| リマインダー設定・時間通知 | `reminder` | ○ デプロイ可能 |
| 情報収集・調査・ナレッジ | `knowledge` | ○ デプロイ可能 |
| Slack投稿・通知 | `slack_post` | ○ デプロイ可能 |
| Teams通知 | `teams_notify` | ○ デプロイ可能 |
| 天気確認 | `weather` | ○ デプロイ可能 |
| 交通経路確認 | `transit` | ○ デプロイ可能 |
| フライト予約確認 | `flight` | ○ デプロイ可能 |
| ホテル予約確認 | `hotel` | ○ デプロイ可能 |
| Gmail操作 | `gmail` | ○ デプロイ可能 |
| コマンド実行 | `execution_result` | ○ デプロイ可能 |
| wants管理操作のみ | なし | ✗ メモのみ |
| status確認のみ | なし | ✗ メモのみ |
| agents/capabilities確認 | なし | ✗ メモのみ |

---

### Step 4: YAMLの生成とデプロイ（対応タイプがある場合）

対応するwantタイプが見つかった場合のみ実行してください。

**YAMLテンプレート:**

```yaml
wants:
  - metadata:
      name: {skill-name}-{yyyymmdd}
      type: {want_type}
      labels:
        source: skill-usage
        skill: {skill_name}
    spec:
      params:
        {param_key}: "{param_value}"
        # ... 会話コンテキストから推定したパラメータを追加
```

**タイプ別パラメータ例:**

`reminder` タイプ:
```yaml
spec:
  params:
    message: "{リマインダーの内容}"
    duration_from_now: "{時間: 例 30m, 2h, 1d}"
    ahead: "5m"
    require_reaction: true
```

`knowledge` タイプ:
```yaml
spec:
  params:
    topic: "{調査対象トピック}"
    output_path: "notes/{topic_slug}.md"
    refresh_interval: "24h"
    depth: "comprehensive"
```

**デプロイコマンド:**
```bash
TMPFILE=/tmp/save-as-want-$(date +%Y%m%d%H%M%S).yaml
cat > "$TMPFILE" << 'YAML'
{生成したYAMLをここに}
YAML
cd /Users/hiroyukiosaki/work/MyWant && ./bin/mywant wants create -f "$TMPFILE" 2>&1 | grep -v "^\[" | grep -v "^Reading config"
```

---

### Step 5: 結果の報告

以下の形式で結果を表示してください:

```
✅ メモを保存しました: ~/.mywant/skill-usage-log.md

Skill: {skill_name}
内容: {summary}

{対応wantタイプがある場合のみ}
✅ Wantをデプロイしました: {want_id}
  タイプ: {want_type}
  パラメータ: {主要パラメータ}

{対応wantタイプがない場合のみ}
ℹ️ 対応するwantタイプが見つからなかったため、メモのみ保存しました。
```

---

## 使用例

- `/save-as-want` — 直前の操作を会話コンテキストから推定して保存
- `/save-as-want skill=mywant-deploy context="travel wantをデプロイ" params="config-travel.yaml"` — 明示指定
- `/save-as-want "remindert 明日の朝9時に健康診断リマインダー"` — reminderとして保存＋デプロイ
- `/save-as-want skill=mywant-wants context="abc123のwantを停止した"` — メモのみ保存
