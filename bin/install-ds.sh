#!/bin/bash
# 無料の GLM を使う ds を Mac に入れる（何度実行してもよい）
# 使い方: bash bin/install-ds.sh        キーを入れ直すとき: bash bin/install-ds.sh --key
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
BIN="$HOME/.local/bin"
CONF="$HOME/.config/glm"

chmod +x "$DIR/ds"
mkdir -p "$BIN"

# 元の ds（DeepSeek 用）は念のため ds-deepseek として残す
if [ -e "$BIN/ds" ] && [ ! -L "$BIN/ds" ]; then
  mv "$BIN/ds" "$BIN/ds-deepseek"
fi
ln -sf "$DIR/ds" "$BIN/ds"
echo "ds をつなぎました: $BIN/ds -> $DIR/ds"

mkdir -p "$CONF"
chmod 700 "$CONF"
# 名前を間違えて作ったキーのファイル（api_key の後ろに文字が付いたもの）を消す
rm -f "$CONF"/api_key?*

if [ "$1" = "--key" ] || [ ! -s "$CONF/api_key" ]; then
  read -rs -p "Z.ai の API キーを貼り付けて Enter（画面には出ません）: " KEY
  echo
  if [ -z "$KEY" ]; then
    echo "キーが空です。もう一度実行してください" >&2
    exit 1
  fi
  printf '%s' "$KEY" > "$CONF/api_key"
  unset KEY
  chmod 600 "$CONF/api_key"
  echo "キーを保存しました"
fi

echo "動作確認中..."
echo テスト | "$BIN/ds" "一言で返事して" && echo "完了しました"
