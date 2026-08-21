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

MARKET_RE = re.compile(
    r"股市|港股|恆指|恒指|恒生|A股|上證|深證|道指|納指|標普|"
    r"樓市|樓價|樓盤|物業|地產|住宅|寫字樓|商舖|中原|美聯|"
    r"stock|market|Hang Seng|Hong Kong property|housing|property|real estate|"
    r"加息|減息|利率|匯率|人民幣|美元|通脹", re.I)

# 競品及全球打拆行業
COMPETITOR_RE = re.compile(
    r"Brokk|Husqvarna|DXR|Sandvik|OSA|TopTec|Kinshofer|Conjet|Aquajet|"
    r"打拆機械|拆卸機械|demolition robot|demolition market|"
    r"收購|併購|acquisition|merger|新建廠|新產品|發佈|上市", re.I)

# 政府資助及建造業政策
GOV_RE = re.compile(
    r"CITF|建造業創新|科技基金|BUD|科技園|數碼港|資助|撥款|補貼|"
    r"屋宇署|發展局|DEVB|建造業議會|CIC|建築物條例|小型工程|"
    r"政府資助|funding|subsidy|grant|HKD\$|建造業 2.0|創科", re.I)

# 地盤/招標/重建
TENDER_RE = re.compile(
    r"招標|投標|重建|拆卸|清拆|活化|維修保養|工程合約|"
    r"tender|redevelopment|demolition contract|市建局|URBAN|"
    r"地盤|工程展開|動工|落成|屋苑|公屋|居屋", re.I)

# 人手/勞工政策
LABOUR_RE = re.compile(
    r"外勞|輸入勞工|人手不足|人手短缺|勞工|建造業工人|"
    r"labor|labour|worker shortage|skilled worker|師傅|學徒", re.I)

CATEGORIES = [
    {"name": "🤖 建造業・機械人", "queries": [
        "建造業 機械人 香港", "拆卸 機械人 建築", "建築科技 香港 創新",
        "裝修 行業 香港", "Brokk demolition robot", "CITF 建造業創新"],
     "re": BUILD_RE, "max": 8, "lang": "zh-HK"},
    {"name": "🏭 競品・全球行業", "queries": [
        "Brokk robot news", "demolition robot market", "Husqvarna DXR",
        "Sandvik demolition acquisition", "拆卸機械 市場"],
     "re": COMPETITOR_RE, "max": 5, "lang": "en-US"},
    {"name": "🏛️ 政府資助・政策", "queries": [
        "CITF 建造業 資助", "建造業創新科技基金 2026", "BUD 資助 申請",
        "科技園 初創 資助 香港", "屋宇署 政策 建造"],
     "re": GOV_RE, "max": 5, "lang": "zh-HK"},
    {"name": "🏗️ 地盤・招標・重建", "queries": [
        "香港 重建 項目 2026", "市建局 招標 重建", "拆卸 工程 招標 香港",
        "公屋 重建 拆卸"],
     "re": TENDER_RE, "max": 4, "lang": "zh-HK"},
    {"name": "👷 人手・勞工政策", "queries": [
        "建造業 外勞 輸入勞工", "香港 建造業 人手不足", "建造業 勞工 政策"],
     "re": LABOUR_RE, "max": 3, "lang": "zh-HK"},
    {"name": "📈 股市・樓市", "queries": [
        "恆指 港股 今日", "香港 樓市 樓價", "Hang Seng index", "Hong Kong property market"],
     "re": MARKET_RE, "max": 5, "lang": "zh-HK"},
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
