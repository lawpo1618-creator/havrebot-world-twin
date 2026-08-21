# 🌍 havreBOT 世界分身 (World Twin)

每日自動收集香港建造業／機械人／競品／政策新聞，**零成本、零 token**（GitHub Actions 免費運行）。

## 運作原理

```
GitHub Actions（微軟免費雲端）
  ↓ 每日香港時間 08:00 自動觸發
Python 收集器（Google News RSS，免費）
  ↓ 過濾相關新聞（機械人/建造/拆卸/CITF/Brokk…）
存檔至 reports/ 並自動 commit
  ↓
你幾時開機，都有最新日報可睇
```

## 點樣睇日報

1. 打開本 repo → `reports/` 資料夾
2. 揀最新日期嘅 `world-report-YYYY-MM-DD.md`
3. 或者睇 `Actions` 分頁 → 最新 run → 日報輸出

## 本機版

`havrebot_world_collector.py` 亦可以喺本機直接跑（Windows 都得）：

```bash
python havrebot_world_collector.py
```

## 自訂

編輯 `QUERIES`（搜尋關鍵字）或 `RELEVANT`（相關性過濾）即可改收集範圍。

---
© havreBOT · 2026
