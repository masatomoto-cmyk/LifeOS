# 勤怠記録

ターミナルから出退勤を記録します。データは `data/YYYY-MM.csv` に月ごとに保存され、Excel や Numbers でも開けます。

## 使い方

```bash
kintai in            # 出勤（今の時刻）
kintai in 9:00       # 時刻を指定して出勤
kintai break 60      # 休憩60分
kintai out           # 退勤
kintai note 在宅      # メモ
kintai today         # 今日の記録
kintai report        # 今月の一覧と合計時間
kintai report 2026-09
kintai edit          # CSVを直接修正（打刻忘れの日など）
```

`kintai` だけで動かすには、`~/.zshrc` に次の1行を追加します。

```bash
alias kintai="$HOME/Documents/LifeOS/10_Life/17_勤怠/kintai"
```

## Googleカレンダー自動連携

毎晩 23:30 頃、Claude の定期タスク「【毎晩】勤怠をGoogleカレンダーに反映」が、出勤・退勤がそろった日を 自分の Google カレンダーにグレーの「勤務 (実働 H:MM)」予定として登録します。

- 後から `kintai edit` などで時刻を直すと、次の同期でカレンダーの予定も更新されます
- 反映状況は `data/calendar-sync.csv` に記録されます（手で編集しない）
- `kintai pending` で未反映の日を確認できます
- Claude アプリが閉じていると、次に開いたときに実行されます

## 運用のコツ

- 打刻を忘れた日は `kintai edit` で後から追記する
- 月末に `kintai report` を見て、給与明細や会社の記録と照合する
- 年が変わったら前年のCSVを `90_Archive/Life/勤怠/` に移す
