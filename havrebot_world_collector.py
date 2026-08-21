#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
havreBOT 世界分身收集器 v2 (2026-08-21) — 雲端版
GitHub Actions 每日運行，零 token，輸出日報到 reports/
用法: python havrebot_world_collector.py
"""
import urllib.request, urllib.parse, xml.etree.ElementTree as ET
import datetime, os, re, html

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"}

QUERIES = [
    "建造業 機械人 香港",
    "拆卸 機械人 建築",
    "建築科技 香港 創新",
    "裝修 行業 香港",
    "Brokk demolition robot",
    "CITF 建造業創新",
]

RELEVANT = re.compile(
    r"機械人|機器人|拆卸|打拆|建造|建築|裝修|工程|樓宇|地盤|結構|"
    r"robot|demolition|construction|building|renovation|concrete|crane|"
    r"CITF|科技園|創新科技|BUD|資助|brokk|husqvarna|dxr|拆", re.I)

def fetch_rss(query, days=3):
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({
        "q": f"{query} when:{days}d", "hl": "zh-HK", "gl": "HK", "ceid": "HK:zh-Hant"})
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

def is_relevant(title, src=""):
    return bool(RELEVANT.search(title + " " + src))

def main():
    seen, results = set(), []
    for q in QUERIES:
        for it in fetch_rss(q):
            key = it["t"][:50]
            if key in seen:
                continue
            seen.add(key)
            if not is_relevant(it["t"], it["s"]):
                continue
            results.append(it)
    results.sort(key=lambda x: x["d"], reverse=True)

    today = datetime.date.today().isoformat()
    out_lines = [f"# 🌍 世界分身日報 {today}", ""]
    if not results:
        out_lines.append("今日冇捕捉到相關新聞（正常，機械人行業唔係日日有嘢）")
    else:
        for it in results[:12]:
            out_lines.append(f"- 📰 **{it['t'][:120]}**")
            out_lines.append(f"  {it['s']} | {it['d'][:16]}")
            out_lines.append(f"  {it['l'][:120]}")
            out_lines.append("")

    report = "\n".join(out_lines)

    # 存檔（GitHub Actions 環境用相對路徑）
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
    return len(results)

if __name__ == "__main__":
    main()
