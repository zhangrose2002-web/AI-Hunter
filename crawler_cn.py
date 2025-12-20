# -*- coding: utf-8 -*-
"""
AI Hunter - 创业者加强版 (全球猎捕)
目标：为创业者精选 降本、增效、看趋势 的核心工具
"""

import json
import requests
from bs4 import BeautifulSoup
import sys
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- 关键词库：深度适配创业场景 ---
COST_KEYWORDS = [
    '免费', '开源', '降本', '替代', '自动化', '人力', '节省', '客服', '外包', '平替',
    'free', 'open source', 'save cost', 'replace', 'automate', 'outsourcing', 'low code'
]

EFFICIENCY_KEYWORDS = [
    '效率', '提效', '一键', '生成', '批量', '智能', '办公', '营销', '剪辑', '写作', 'PPT',
    'efficiency', 'productivity', 'boost', 'workflow', 'marketing', 'content creation'
]

TREND_KEYWORDS = [
    '突破', '发布', '融资', '趋势', '报告', '首发', '重磅', 'OpenAI', 'Sora', 'Claude',
    'breakthrough', 'funding', 'trend', 'report', 'unveiled', 'investment'
]

def clean_text(text):
    return ''.join(c for c in str(text) if ord(c) >= 32).strip() if text else ""

def classify_tool(desc, title):
    text = (title + " " + desc).lower()
    cost_score = sum(2 if kw in text else 0 for kw in COST_KEYWORDS)
    eff_score = sum(1 if kw in text else 0 for kw in EFFICIENCY_KEYWORDS)
    # 创业者更看重降本，权重稍高
    return "cost" if cost_score >= eff_score and cost_score > 0 else "efficiency"

# ========================
# 捕猎源 1：AI工具集 (国内优质源)
# ========================
def fetch_aibot(max_items=20):
    print("🔍 猎捕中：AI工具集 (国内)...")
    tools = []
    try:
        res = requests.get("https://ai-bot.cn/", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        cards = soup.select('.url-card')[:max_items]
        for card in cards:
            title = card.select_one('strong').get_text(strip=True)
            desc = card.select_one('.url-info p').get_text(strip=True)
            link = card.select_one('a')['href']
            tools.append({"title": title, "desc": desc, "source": link})
    except Exception as e: print(f"⚠️ AI工具集捕获跳过: {e}")
    return tools

# ========================
# 捕猎源 2：发现AI (国内优质源)
# ========================
def fetch_faxianai(max_items=15):
    print("🔍 猎捕中：发现AI (国内)...")
    tools = []
    try:
        res = requests.get("https://faxianai.com", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        cards = soup.select('a[href^="/tool/"]')[:max_items]
        for card in cards:
            title = card.select_one('h3').get_text(strip=True)
            desc = card.select_one('p').get_text(strip=True)
            source = "https://faxianai.com" + card['href']
            tools.append({"title": title, "desc": desc, "source": source})
    except Exception as e: print(f"⚠️ 发现AI捕获跳过: {e}")
    return tools

# ========================
# 捕猎源 3：FutureTools (全球视野)
# ========================
def fetch_futuretools(max_items=20):
    print("🔍 猎捕中：FutureTools (全球)...")
    tools = []
    try:
        # 抓取按日期排序的最新工具
        res = requests.get("https://www.futuretools.io/?sort=date-added", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        cards = soup.select('div[role="article"]')[:max_items]
        for card in cards:
            title_elem = card.select_one('h2 a')
            desc_elem = card.select_one('p')
            if title_elem:
                tools.append({
                    "title": title_elem.get_text(strip=True),
                    "desc": desc_elem.get_text(strip=True) if desc_elem else "",
                    "source": title_elem['href'] if title_elem.has_attr('href') else "#"
                })
    except Exception as e: print(f"⚠️ FutureTools捕获跳过: {e}")
    return tools

# ========================
# 趋势源：36Kr AI 专栏
# ========================
def fetch_36kr_trends(max_items=5):
    print("📡 监测中：36Kr 趋势雷达...")
    trends = []
    try:
        res = requests.get("https://36kr.com/newsflashes", headers=HEADERS, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        for item in soup.select('div.newsflash-item')[:15]: # 扩大筛选范围
            title_elem = item.select_one('a.article-title')
            if not title_elem: continue
            title = title_elem.get_text(strip=True)
            # 仅筛选与创业/AI 强相关的趋势
            if any(kw in title.lower() for kw in TREND_KEYWORDS + ['ai', '人工智能', '机器人']):
                trends.append({
                    "title": title,
                    "desc": "创业趋势快报",
                    "source": "https://36kr.com" + title_elem['href']
                })
            if len(trends) >= max_items: break
    except Exception as e: print(f"⚠️ 趋势捕获失败: {e}")
    return trends

def main():
    print("🚀 AI Hunter 启动，正在为创业者猎捕全球商机...")
    
    # 汇总所有工具
    raw_tools = []
    raw_tools.extend(fetch_aibot(25))
    raw_tools.extend(fetch_faxianai(20))
    raw_tools.extend(fetch_futuretools(25))

    # 去重处理
    unique_tools = []
    seen_titles = set()
    for t in raw_tools:
        name = t['title'].lower().strip()
        if name not in seen_titles:
            seen_titles.add(name)
            unique_tools.append(t)

    # 分类逻辑
    data = {"cost": [], "efficiency": [], "trend": []}
    for t in unique_tools:
        cat = classify_tool(t['desc'], t['title'])
        data[cat].append(t)

    # 猎捕趋势
    data["trend"] = fetch_36kr_trends(6)

    # 兜底：如果某项太少，保持之前的展示
    if len(data["cost"]) < 3:
        data["cost"].append({"title": "Claude 3.5 Sonnet", "desc": "高性价比的智能模型，替代初级分析师", "source": "https://claude.ai"})
    
    # 写入 JSON
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 猎捕完成！")
    print(f"💰 发现 {len(data['cost'])} 个降本工具")
    print(f"⚡ 发现 {len(data['efficiency'])} 个增效工具")
    print(f"📡 捕获 {len(data['trend'])} 条行业趋势")

if __name__ == "__main__":
    main()
