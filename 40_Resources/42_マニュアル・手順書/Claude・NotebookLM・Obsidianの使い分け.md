---
tags: [手順書, 運用]
---

# Claude・NotebookLM・Obsidian の使い分け

| 道具 | 役目 | 置き場 |
|---|---|---|
| Obsidian | 自分が書く・読む知識（学習ノート、読書メモ、手順書）。リンクと検索で引く | `30_Learning`・`40_Resources`（Vault） |
| NotebookLM | 資料と作業記録をためて、あとから質問する。経緯の「記憶」 | 「LifeOS 作業記録」など（ID は `~/.claude/CLAUDE.md` の表） |
| Claude | 作業の実行。作業記録を書き、NotebookLM に入れ、Obsidian のノートを前提として読む | リポジトリの `docs/`（作業記録の原本） |

## 流れ
1. **始め**: Claude は NotebookLM に「決定事項と未対応」を聞く（クラウドでは `docs/` の最新の作業記録を読む）。学習内容が関わるときは Obsidian のノートも読む
2. **作業**: Claude が実行する。分かったことのうち、あとで自分が見返す知識は `30_Learning`・`40_Resources` に新しいノートとして足す（`[[ ]]` で既存のノートにつなぐ）
3. **終わり**: `docs/YYYY-MM-DD_作業記録.md` を書き（テンプレート: `41_テンプレート/作業記録.md`）、NotebookLM に資料として追加する

## 決まり
- Claude は Obsidian の既存ノートの本文を書き換えない。足すのは新しいノートか、末尾の追記だけ
- `10_Life` は Vault にも NotebookLM にも入れない。`ds` にも渡さない
- `30_Learning`・`40_Resources` は GitHub に上がる。秘密情報・第三者の個人情報は書かない
- NotebookLM（`nlm`）と Obsidian は Mac で動く。クラウドのセッションでは使えないので、`docs/` とリポジトリのノートを読み書きし、NotebookLM への追加は次に Mac で行う
