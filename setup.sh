#!/bin/zsh
# 日常生活〜個人活動 フォルダ構成セットアップ
# 使い方: ./setup.sh [作成先]   （省略時は ./LifeOS）
set -e

ROOT="${1:-./LifeOS}"
DEV="${DEV:-$HOME/Dev}"   # 個人開発の置き場所（20_Projects はここへのリンク）
YEAR=$(date +%Y)

dirs=(
  # 00 受け皿：とりあえず放り込む場所。週1で空にする
  "00_Inbox"

  # 10 日常生活
  "10_Life/11_お金/家計簿"
  "10_Life/11_お金/税金・確定申告/$YEAR"
  "10_Life/11_お金/保険"
  "10_Life/11_お金/契約・サブスク"
  "10_Life/12_健康/通院・検査"
  "10_Life/12_健康/運動・食事"
  "10_Life/13_住まい/賃貸・契約"
  "10_Life/13_住まい/家電・説明書"
  "10_Life/14_手続き・公的書類/身分証コピー"
  "10_Life/14_手続き・公的書類/役所・年金"
  "10_Life/15_買い物/欲しいもの"
  "10_Life/15_買い物/購入履歴・保証書"
  "10_Life/16_旅行・イベント"
  "10_Life/17_勤怠/data"


  # 30 学習
  "30_Learning/31_プログラミング"
  "30_Learning/32_音楽理論・DTM"
  "30_Learning/33_読書メモ"
  "30_Learning/34_講座・資格"

  # 40 資料・テンプレ（何度も使う参照物）
  "40_Resources/41_テンプレート"
  "40_Resources/42_マニュアル・手順書"
  "40_Resources/43_ブックマーク・リンク集"
  "40_Resources/44_フォント・素材"

  # 50 メディア
  "50_Media/51_写真/$YEAR"
  "50_Media/52_動画/$YEAR"
  "50_Media/53_スクリーンショット"

  # 90 アーカイブ：終わったもの・使わないもの
  "90_Archive/Projects"
  "90_Archive/Life"
)

# 20 個人活動（進行中のプロジェクト）— 実体は $DEV
dev_dirs=(
  "_template/docs"
  "21_Web開発"
  "22_DTM・音楽/曲"
  "22_DTM・音楽/音源・サンプル"
  "22_DTM・音楽/ミックス・マスター"
  "23_サイト運営/記事下書き"
  "23_サイト運営/画像素材"
  "23_サイト運営/アフィリエイト・広告"
  "23_サイト運営/アクセス解析"
  "24_アイデア"
)

for d in "${dev_dirs[@]}"; do
  mkdir -p "$DEV/$d"
done
mkdir -p "$ROOT"
[[ -e "$ROOT/20_Projects" ]] || ln -s "$DEV" "$ROOT/20_Projects"

for d in "${dirs[@]}"; do
  mkdir -p "$ROOT/$d"
done

cp "$(dirname "$0")/README.md" "$ROOT/README.md" 2>/dev/null || true
echo "作成しました: $ROOT"
