# 週報（Qiita 投稿）

1週間の活動を自動で集めて、Qiita に週報として投稿します。下書きは `drafts/YYYY-MM-DD_週報.md`、投稿済みの記録は `posted.csv` に残ります。

## 集める活動

- `~/Dev` 以下の Git リポジトリのコミット
- 各プロジェクト `docs/README.md` の「メモ・ログ」（`- YYYY-MM-DD: 内容` の行）
- `~/Dev` で更新したファイル（DTM の曲、記事下書きなど Git 管理外のもの）
- `30_Learning` で更新した学習メモ

勤怠や家計など `10_Life` の内容は載せません。

## 準備（最初に1回）

1. Qiita の [アクセストークン設定](https://qiita.com/settings/applications) で、スコープ `read_qiita` と `write_qiita` にチェックしてトークンを発行
2. ターミナルで保存（貼り付けたトークンは画面に表示されません）:

```bash
mkdir -p ~/.config/qiita && read -s "t?Qiitaトークン: " && print -r -- "$t" > ~/.config/qiita/token && chmod 600 ~/.config/qiita/token
```

3. `qiita` だけで動かすには `~/.zshrc` に追加:

```bash
alias qiita="$HOME/Documents/LifeOS/30_Learning/35_週報/qiita"
```

## 使い方

```bash
qiita draft              # 今日までの7日分の下書きを作る
qiita draft 2026-10-25   # 指定日までの7日分
qiita post --dry-run     # 送信内容を確認するだけ
qiita post               # 最新の下書きを投稿（投稿済みなら記事を更新）
qiita status             # 下書きと投稿状況の一覧
```

「今週のまとめ」が空のままだと投稿されません。

## 自動投稿

毎週日曜 21:00 頃、Claude の定期タスク「【毎週日曜】活動週報をQiitaに投稿」が下書きを作り、まとめと来週の予定を書き足して投稿します。

- 先に自分で `qiita draft` して編集しておけば、その内容が優先されます
- Claude アプリが閉じていると、次に開いたときに実行されます

## 設定（任意）

`config.json` を作ると初期値を変えられます。

```json
{
  "tags": ["週報", "個人開発"],
  "private": true,
  "exclude": ["21_Web開発/2026_ひみつのアプリ"]
}
```

- `private`: `true` = 限定共有（URL を知っている人だけ）、`false` = 全体公開
- `exclude`: 週報に載せないフォルダ（`~/Dev` からの相対パス）
- 1回だけ変えたいときは下書き先頭の `private:` や `tags:` を直接書き換える
