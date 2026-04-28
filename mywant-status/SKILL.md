---
name: mywant-status
description: MyWantサーバー・ワーカー・GUIプロセスの状態確認。サーバーが起動しているか確認するときに使用する。
metadata:
  output-format: text
---

$ARGUMENTS

MyWantの状態を確認します。以下のコマンドを実行し、出力をそのまま表示してください（`[REGISTRY]`・`[AchievementStore]` 行は除去）:

```bash
cd /Users/hiroyukiosaki/work/golang/mywant && ./bin/mywant ps 2>&1 | grep -v "^\[REGISTRY\]" | grep -v "^\[AchievementStore\]" | grep -v "^\[" | grep -v "^Reading config"
```

## 使用例

- `/mywant-status` — サーバー・ワーカー・GUIの状態を表示
