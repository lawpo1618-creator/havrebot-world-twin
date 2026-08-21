#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
havreBOT 世界分身收集器 v3 (2026-08-21) — 雲端版
GitHub Actions 每日運行，零 token
類別: 建造業/機械人 | 世界要聞 | 香港要聞 | 新科技新技術
用法: python havrebot_world_collector.py
"""
import urllib.request, urllib.parse, xml.etree.ElementTree as ET
import datetime, os, re, html

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"}

# ---- 類別定義 ----
BUILD_RE = re.compile(
    r"機械人|機器人|拆卸|打拆|建造|建築|裝修|工程|樓宇|地盤|結構|"
    r"robot|demolition|construction|building|renovation|concrete|crane|"
    r"CITF|科技園|創新科技|BUD|資助|brokk|husqvarna|dxr|拆", re.I)

TECH_RE = re.compile(
    r"科技|技術|突破|創新|AI|人工智能|芯片|晶片|量子|太空|航天|新能源|電池|"
    r"核聚變|自動駕駛|機械人|機器人|robot|AI|chip|quantum|space|fusion|"
    r"battery|nuclear|semiconductor|breakthrough|innovation", re.I)

CATEGORIES = [
    {"name": "🤖 建造業・機械人", "queries": [
        "建造業 機械人 香港", "拆卸 機械人 建築", "建築科技 香港 創新",
        "裝修 行業 香港", "Brokk demolition robot", "CITF 建造業創新"],
     "re": BUILD_RE, "max": 8, "lang": "zh-HK"},
    {"name": "🌍 世界要聞", "queries": ["world news today", "breaking news world"],
     "re": None, "max": 5, "lang": "en-US"},
    {"name": "🇭🇰 香港要聞", "queries": ["香港 新聞", "Hong Kong news"],
     "re": None, "max": 5, "lang": "zh-HK"},
    {"name": "💡 新科技・新技術", "queries": [
        "科技 突破 創新 2026", "new technology breakthrough robot AI",
        "人工智能 最新 進展", "量子 芯片 太空 突破"],
     "re": TECH_RE, "max": 5, "lang": "zh-HK"},
]

def fetch_rss(query, lang="zh-HK", days=2):
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({
        "q": f"{query} when:{days}d", "hl": lang, "gl": "HK", "ceid": "HK:zh-Hant"})
    try:
        req = urllib.request.Request(url, headers=UA)
        data = urllib.request.urlopen(req, timeout=20).read()
        root = ET.fromstring(data)
        items = []
        for it in root.iter("item"):
            title = it.findtext("title") or ""
            link = it.findtext("link") or ""
            pub = it.findtext("pubDate") or ""
            src = it.findtext("source") or ""
            items.append({"t": html.unescape(title), "l": link, "d": pub, "s": src})
        return items
    except Exception:
        return []

def main():
    today = datetime.date.today().isoformat()
    out_lines = [f"# 🌍 世界分身日報 {today}", ""]

    for cat in CATEGORIES:
        seen, results = set(), []
        for q in cat["queries"]:
            for it in fetch_rss(q, cat["lang"]):
                key = it["t"][:50]
                if key in seen:
                    continue
                seen.add(key)
                if cat["re"] and not cat["re"].search(it["t"] + " " + it["s"]):
                    continue
                results.append(it)
        results.sort(key=lambda x: x["d"], reverse=True)

        out_lines.append(f"## {cat['name']}")
        if not results:
            out_lines.append("（今日冇捕捉到）")
        else:
            for it in results[:cat["max"]]:
                out_lines.append(f"- 📰 **{it['t'][:120]}**")
                out_lines.append(f"  {it['s']} | {it['d'][:16]}")
                out_lines.append(f"  {it['l'][:120]}")
        out_lines.append("")

    report = "\n".join(out_lines)

    # 存檔（跨平台）
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"world-report-{today}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report + "\n")

    # 清理 30 日前
    for fn in os.listdir(folder):
        if fn.startswith("world-report-") and fn.endswith(".md"):
            try:
                d = datetime.date.fromisoformat(fn.replace("world-report-", "").replace(".md", ""))
                if (datetime.date.today() - d).days > 30:
                    os.remove(os.path.join(folder, fn))
            except Exception:
                pass

    print(report)

if __name__ == "__main__":
    main()
