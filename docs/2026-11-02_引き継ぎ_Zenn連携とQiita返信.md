# 引き継ぎ：Zenn 連携・note 自動投稿・Qiita のコメント返信（2026-11-02）

クラウドのセッションから、Mac（ローカル）の Claude Code への引き継ぎ。
クラウドではユーザーのブラウザを操作できず、Zenn の連携が終わらなかった。ローカルでは Claude in Chrome（ユーザーの Chrome。Zenn・GitHub にログイン済み）を使って続ける。

## 1. いまの状態

### Qiita のコメント（未返信）
- 記事: https://qiita.com/masatomoto-cmyk/items/ecb177727003af2b6332 （個人開発のSNSを「チームで運営できる状態」にする最初の3手）
- コメント: @umitdogan さん（2026-10-30）「画像の削除が失敗した場合は、アカウント削除を止めて再試行できますか？DBだけ消えて画像が残るケースも確認対象か気になりました。」
- 事実（OTOMO の `supabase/functions/delete-account/index.ts` で確認済み）:
  - `storage.from('avatars').list()` / `remove()` のエラーを見ていない。画像の削除に失敗しても `auth.admin.deleteUser()` に進むので、DB が消えて画像だけ残ることがある。avatars は公開バケット
  - 記事のロールバックテストは DB（SQL）だけが対象で、Storage の削除失敗は確かめていない
- 返信の下書き: `docs/2026-11-02_Qiita返信下書き.md`（このブランチにある）
- Qiita のトークンがクラウドになかったので投稿していない。ローカルでは `~/.config/qiita/token` があれば API で投稿できる

### Zenn（未連携）
- 転載先のリポジトリ: `masatomoto-cmyk/qiita-weekly`（非公開）の `main`。`articles/` に3本入れてある（push 済み）
  - `qiita-ecb177727003af2b6332.md`（退会機能の記事。コメントで分かった漏れを末尾に追記済み）
  - `qiita-78eb51a224a8df8b7a45.md`（手で書いて覚える個人開発 #01）
  - `qiita-e85d40b956ab6e136295.md`（同 #02）
- 毎日 22:17 (JST) に `.github/workflows/zenn.yml` が、2026-10-31 以降に一般公開した Qiita 記事を `articles/` と `note/` に追加する（`scripts/qiita_to_zenn.py`）
- **詰まっているところ**: https://zenn.dev/dashboard/deploys が「GitHubリポジトリと連携」「リポジトリを連携する」の画面のまま。ユーザーが連携をやり直しても変わらなかった。そのため記事は1本も公開されていない（`https://zenn.dev/api/articles/qiita-ecb177727003af2b6332` が見つからない）

### note（Secrets 未登録）
- `.github/workflows/note.yml`（毎日 22:43 JST、1回1本）と `scripts/note_post.py`（非公式 API。ログインは Playwright）を追加済み
- まだ一度も動かしていない。qiita-weekly の Secrets に `NOTE_EMAIL`・`NOTE_PASSWORD` がない（ユーザーが登録する。Claude は入力しない）
- `NOTE_MODE`（Variables）が未設定なら下書きまで。見た目を確かめてから `publish` にする

### その他
- qiita-weekly の「Publish articles」（Qiita CLI）は 10/23 から失敗している。`public/2026-10-23-qiita-weekly.md` が Qiita 上で直されていて、手元の方が古いため。Zenn・note の変更とは関係ない。直すときは Qiita 側の内容を `qiita pull` などで取り込んでから。`--force` で上書きしない

## 2. ローカルでしてほしいこと（順番に）

1. **Zenn の連携を終わらせる**（Claude in Chrome）
   - https://github.com/settings/installations で「Zenn Connect」がどのリポジトリに入っているか見る。`qiita-weekly` が入っていなければ、Configure から足す（Only select repositories → `qiita-weekly` → Save）
   - それでも Zenn が連携前の画面のままなら、Zenn Connect を Uninstall し、Zenn の画面の「リポジトリを連携する」からやり直す
   - Zenn のログインが GitHub アカウントでないと結びつかないことがある。そのときは GitHub でログインし直す（ログイン操作とパスワードはユーザーが行う）
   - 連携後、https://zenn.dev/dashboard/deploys でリポジトリ `qiita-weekly`・ブランチ `main` になっているか確かめる
2. **Zenn に取り込ませる**: 連携後の push で取り込まれる。`articles/` のどれかを実際に直して push する（空のコミットは使わない）。デプロイ一覧が「成功」になり、`https://zenn.dev/api/articles/qiita-ecb177727003af2b6332` で記事が返ることを確かめる。エラーなら内容に合わせて `articles/` を直す
3. **Qiita に返信する**: 下書きをユーザーに見せて OK をもらってから投稿する（他人へのメッセージなので、送る前に必ず聞く）。投稿は `POST https://qiita.com/api/v2/items/ecb177727003af2b6332/comments`（`{"body": "..."}`、トークンは `~/.config/qiita/token`）
4. **Qiita の記事にも追記する**: Zenn 版の末尾と同じ「追記（2026-11-02）」を Qiita の記事にも入れる（`PATCH /api/v2/items/ecb177727003af2b6332`。本文・タイトル・タグは今のものを取得してから、追記だけ足す）
5. **note**: ユーザーに qiita-weekly の Secrets（`NOTE_EMAIL`・`NOTE_PASSWORD`）を登録してもらい、Actions の「Post to note」を手動で実行する。note の下書きを Chrome で開いて見た目を確かめる。よければ Variables に `NOTE_MODE=publish`
6. **OTOMO の退会処理を直す**（ユーザーの OK のあと）: `delete-account` で画像の list / remove のエラーを見て、失敗したら 500 を返し `deleteUser` に進まない。画面は再試行を促す。直したら返信・記事の「直す予定です」を「直しました」に変える

## 3. 守ること
- パスワード・トークン・認証コードは Claude が入力しない。ログインはユーザーが行う
- Qiita の返信・他人へのメッセージは、送る前にユーザーに見せる
- 作業が終わったら `docs/YYYY-MM-DD_作業記録.md` に記録する

## 4. このブランチ
LifeOS の `claude/magical-mccarthy-8asggd`（まだ main に入っていない）。ローカルでは:

```bash
git fetch origin claude/magical-mccarthy-8asggd && git checkout claude/magical-mccarthy-8asggd
```
