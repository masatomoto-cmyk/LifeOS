#!/bin/bash
# 無料の AI（Groq）を使う ds を Mac に入れる（何度実行してもよい）
# 使い方: bash bin/install-ds.sh        Groq のキーを入れ直すとき: bash bin/install-ds.sh --add groq
# 予備の AI を足す:  bash bin/install-ds.sh --add groq|openrouter|gemini|cerebras
# 予備の状態を見る:  bash bin/install-ds.sh --list
set -e
umask 077   # キーのファイルが一瞬でも他人に読める権限で作られないようにする

DS_CONF="$HOME/.config/ds"

if [ "$1" = "--list" ]; then
  for n in groq openrouter gemini cerebras; do
    if [ -s "$DS_CONF/$n.key" ]; then echo "$n: キーあり（モデル: $(cat "$DS_CONF/$n.model" 2>/dev/null || echo 既定)）"; else echo "$n: 未設定"; fi
  done
  exit 0
fi

if [ "$1" = "--add" ]; then
  NAME="$2"
  case "$NAME" in
    groq)       BASE="https://api.groq.com/openai/v1";                        PAGE="https://console.groq.com/keys";        PREFER="openai/gpt-oss-120b openai/gpt-oss-20b" ;;
    openrouter) BASE="https://openrouter.ai/api/v1";                          PAGE="https://openrouter.ai/settings/keys";  PREFER="openrouter/free" ;;
    gemini)     BASE="https://generativelanguage.googleapis.com/v1beta/openai"; PAGE="https://aistudio.google.com/apikey"; PREFER="gemini-2.5-flash gemini-3.1-flash-lite gemini-flash-latest" ;;
    cerebras)   BASE="https://api.cerebras.ai/v1";                            PAGE="https://cloud.cerebras.ai";            PREFER="gpt-oss-120b qwen-3.8-27b" ;;
    *) echo "使い方: bash bin/install-ds.sh --add groq|openrouter|gemini|cerebras" >&2; exit 1 ;;
  esac
  echo "キーは $PAGE で作れます（課金の設定はしないでください。無料の範囲だけで使います）"
  [ "$NAME" = "gemini" ] && echo "注意: Gemini の無料枠は、送った内容が Google の改善に使われ、人が読むこともあります"
  [ "$NAME" = "cerebras" ] && echo "注意: Cerebras はカード登録が必要で、無料は登録後30日の \$5 分だけです"
  read -rs -p "$NAME の API キーを貼り付けて Enter（画面には出ません）: " KEY
  echo
  if [ -z "$KEY" ]; then echo "キーが空です。もう一度実行してください" >&2; exit 1; fi
  mkdir -p "$DS_CONF"; chmod 700 "$DS_CONF"
  printf '%s' "$KEY" > "$DS_CONF/$NAME.key"; chmod 600 "$DS_CONF/$NAME.key"
  # 使えるモデルの一覧から、好みの順に1つ選ぶ（見つからなければ ds の既定を使う）
  MODELS=$(curl -s -H "Authorization: Bearer $KEY" "$BASE/models" | python3 -c "import json,sys
try: print('\n'.join(m['id'].removeprefix('models/') for m in json.load(sys.stdin).get('data',[])))
except Exception: pass")
  unset KEY
  rm -f "$DS_CONF/$NAME.model"
  for m in $PREFER; do
    if printf '%s\n' "$MODELS" | grep -qx "$m"; then printf '%s' "$m" > "$DS_CONF/$NAME.model"; break; fi
  done
  echo "キーを保存しました（モデル: $(cat "$DS_CONF/$NAME.model" 2>/dev/null || echo ds の既定)）"
  echo "動作確認中..."
  echo テスト | DS_ORDER="$NAME" "$(cd "$(dirname "$0")" && pwd)/ds" --max 300 "一言で返事して" && echo "完了しました。$NAME を使います"
  exit 0
fi

DIR="$(cd "$(dirname "$0")" && pwd)"
BIN="$HOME/.local/bin"

chmod +x "$DIR/ds"
mkdir -p "$BIN"
ln -sf "$DIR/ds" "$BIN/ds"
echo "ds をつなぎました: $BIN/ds -> $DIR/ds"

if [ ! -s "$DS_CONF/groq.key" ]; then
  echo "Groq のキーがありません。bash bin/install-ds.sh --add groq で入れてください（なければ ds は使えず、Claude が自分で行います）"
fi

echo "動作確認中..."
echo テスト | "$BIN/ds" "一言で返事して" && echo "完了しました"
