# マシンライブ連携（Roland S-1 × P-6 × TouchDesigner）まとめ（2026-10-31 復元）

2026-10-27〜29 に作った連携を、残っていたファイルと作業記録から1つにまとめ直したもの。
元の会話（セッション）はサイドバーの「マシンライブ」区切りと一緒に消えたが、作ったファイルはすべて残っている。

## 全体のつながり

```
Logic「claude project」（128BPM）
 ├─ トラック 9  P-6 11（ドラム, ch11）  ─┐
 ├─ トラック 11 P-6 15（ベース, ch15）  ─┼─→ 送り先は今 S-1（P-6 をつないだら P-6 に直す）
 ├─ トラック 15 S-1（ch12, リージョン「S-1 with P-6」1〜121小節）→ S-1
 ├─ MIDI クロック → P-6 MIDI IN だけ
 └─ IAC ドライバ バス1 → TouchDesigner の midi_in（セクション切り替え・フラッシュ）

P-6 の音（USB オーディオ）→ TouchDesigner の audio_in（キック・ハイハットの反応）
TouchDesigner /project1/reel_av → record_reel で ProRes 録画 → reel_out/
```

## 置き場所

| もの | 場所 |
|---|---|
| TouchDesigner 一式 | `~/Dev/22_DTM・音楽/2026_リール自動投稿/touchdesigner/`（reels-autopost リポジトリ。README.md・使い方_reel.txt あり。`~/Downloads/TouchDesigner_AV` はここへのリンク） |
| 本番のプロジェクト | `masa_cc_scenes.toe`（バックアップは `Backup/` に 1〜4） |
| できた動画 | `reel_out/reel_final_60s.mp4`（インスタ用）・`reel_final_4min.mp4`・`run6_final.mov`（ProRes） |
| S-1 操作コマンド | `bin/s1`（本体 `bin/s1ctl.py`、Python 環境 `~/.venvs/s1`） |
| S-1 のフレーズ作り | `bin/s1jam.py`（その場で演奏）・`bin/s1bassmid.py`（ベース MIDI）・`bin/s1p6phrase.py`（P-6 ベースに合わせる） |
| S-1 の音の測定 | `bin/s1measure.sh`・`bin/s1silence.sh`・`bin/midispy.py`・`bin/midireplay.py` |
| MIDI ファイル | `~/Music/S-1/S-1_with_P-6_128.mid` ほか、`~/Downloads/p6_dnb_kit/`（P-6 のドラム・ベース） |
| 詳しい記録 | `docs/2026-10-29_作業記録_S-1操作.md`、`docs/2026-10-29_引き継ぎ_S-1*.md` |

## 動かし方

### 1. S-1 のフレーズを作って Logic に入れる
```bash
~/.venvs/s1/bin/python bin/s1p6phrase.py ~/Downloads/p6_dnb_kit/p6_bass_8th_octave_low_128.mid ~/Music/S-1/S-1_with_P-6_128.mid
```
- P-6 ベースの各小節の一番低い音を根音にして、S-1 のアシッドフレーズ（ch12、FREQ=CC74・RESO=CC71 の動きつき）を書き出す
- Logic のトラック 15「S-1」に置く。Logic は読み込み時に頭の空白を詰めるので、1小節目の頭に CC を入れておく（入れてある）

### 2. TouchDesigner で録画する
1. `masa_cc_scenes.toe` を開く
2. Textport（Dialogs > Textport）で次を実行
   ```
   RUN_=lambda n: exec(open('/Users/tokunagatadashitomoe/Dev/22_DTM・音楽/2026_リール自動投稿/touchdesigner/'+n+'.py', encoding='utf-8').read(), globals())
   REC_NAME='my_take.mov'; RUN_('rec_start')
   ```
3. Logic を1小節目から再生
4. 終わったら `op('/project1/reel_av/record_reel').par.record=0`

### 3. TouchDesigner 側の入力の設定（作り直すとき）
- `audio_in` の Device を P-6（`AppleUSBAudioEngine:Roland:P-6…`）に → `link_logic.py`
- `midi_in` を「IACドライバ バス1」に → `td_iac.py`
- フラッシュに使うノートは `ch1n61 ch1n85 ch1n62 ch1n95`（スネア・クラップ・インパクト）→ `td_iac_fix.py`
- 一から作るときは `build_reel_av.py`（`/project1/reel_av` に一式ができる）

## 映像の流れ
IAC の impact ノートが来るたびに `scene_count` が進み、`scenemap.py` の対応でシーンが変わる。

| 番号 | 区間 | 映像 |
|---|---|---|
| 1 | イントロ | ASCII＋タイトル「MASA」 |
| 2 | ヴァース | 赤紫ネオンのドット |
| 3 | ビルド | 線の地形 |
| 4 | ドロップ | ドット＋左右ミラー（7.5秒ごとに上下ミラーも） |
| 5 | ブレイク | Strudel のコード画面＋カメラが寄る、残像を短く |
| 6〜8 | ヴァース2・ビルド2・ドロップ2 | 線の地形 → ASCII → ドット＋ミラー |
| 9 | アウトロ | タイトル |

共通: ワイヤーフレーム（ザップごとに 球→ドーナツ→箱→筒）、点の雲、キックでズーム、ザップで横スライスのグリッチ、フラッシュで大きい文字の反転、上下に HUD 文字。
調整: 反応の強さ `kick`・`hat` の Gain、残像 `fb_fade`、粒子の量 `grain` の Threshold。

## 気をつけること（S-1）
- S-1 の受信チャンネルは **12**
- S-1 は ch12 のノートを USB MIDI で送り返す。Logic が受けるとループして鳴りっぱなしになる → Logic の 設定 → MIDI → 入力 で「S-1 MIDI OUT」のチェックを外してある。S-1 の鍵盤を録音するときだけ戻し、そのときは送り先を S-1 以外にする
- S-1 トラックには S-1 Control の後ろに Scripter（ピッチベンドを捨て、3ms 以内の同じ命令を1つにする）
- Logic は停止中、MIDI FX の出力を止める。つまみを動かしたら一瞬再生するか、IAC から CC64=0 を入れて送る
- 鳴りっぱなしになったら、全音停止は効かない。電源を入れ直す
- S-1 は止まっていてもクロックを出し続ける。本体のシーケンサーが動いていたら本体で止める
- CC 29 前後より上を総当たりで送ると無音になったことがある。送らない

## 未対応
- P-6 本体をつないで、S-1 と一緒に鳴らす確認
- P-6 11・15・12 トラックの送り先を S-1 から P-6 に変える（ユーザーが決める）
- 録画した動画（`touchdesigner/reel_out/`、約24GB）と `p6_kit_src/` は Git の管理外。消えると戻せないので、外付けディスクなどへの控えを検討

## 置き場所の変更（2026-10-31）
- `~/Downloads/TouchDesigner_AV` を reels-autopost リポジトリ（非公開）の `touchdesigner/` に移した。.toe の中に古い場所が書かれていても動くよう、元の場所にはリンクを残した
- スクリプト・README の中の場所は新しい場所に書き換えた
- Git に入れたのはプロジェクト（.toe、番号つきの控えを除く）・スクリプト・説明・記録の txt だけ（約 0.6MB）。`reel_out/`・`p6_kit_src/`・`Backup/` は `.gitignore` で外した
