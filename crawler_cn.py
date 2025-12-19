# -*- coding: utf-8 -*-
"""
AI Hunter - 全球版
抓取国内外热门 AI 工具，并智能分类到 cost / efficiency
"""

import json
import requests
from bs4 import BeautifulSoup
import time
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# ========================
# 分类关键词（中英文）
# ========================

COST_KEYWORDS = [
    # 中文
    '客服', '人力', '节省', '降本', '替代', '自动化', '外包', '减少', '低成本',
    '免费', '开源', '计费', '预算', '财务', '报销', '合同', '法务', '招聘',
    # 英文
    'cost', 'save money', 'reduce cost', 'replace', 'automate', 'free', 'open source',
    'budget', 'cheaper', 'cut expenses', 'customer service', 'outsourcing'
]

EFFICIENCY_KEYWORDS = [
    # 中文
    '效率', '提升', '加速', '快速', '一键', '自动生成', '智能', '秒出', '批量',
    '设计', '剪辑', '写作', 'PPT', '周报', '会议', '翻译', '抠图', '排版', '绘图',
    # 英文
    'efficiency', 'boost', 'speed up', 'automate', 'generate', 'design', 'write',
    'edit', 'translate', 'create', 'productivity', 'workflow', 'fast', 'instant',
    'batch', 'summarize', 'analyze'
]

def classify_tool(desc, title):
    text = (str(title) + " " + str(desc)).lower()
    cost_score = sum(1 for kw in COST_KEYWORDS if kw in text)
    eff_score = sum(1 for kw in EFFICIENCY_KEYWORDS if kw in text)
    return "cost" if cost_score > eff_score else "efficiency"

def deduplicate(tools):
    """根据标题去重"""
    seen = set()
    unique = []
    for t in tools:
        key = t['title'].strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(t)
    return unique

# ========================
# 抓取国内：发现AI
# ========================

def fetch_faxianai(max_items=8):
    tools = []
    try:
        res = requests.get("https://faxianai.com", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        cards = soup.select('a[href^="/tool/"]')[:max_items]
        for card in cards:
            title = card.select_one('h3').get_text(strip=True) if card.select_one('h3') else ""
            desc = card.select_one('p').get_text(strip=True) if card.select_one('p') else ""
            tag = card.select_one('span.bg-blue-100').get_text(strip=True) if card.select_one('span.bg-blue-100') else ""
            source = "https://faxianai.com" + card['href']
            tools.append({"title": title, "desc": f"{desc} {tag}", "source": source})
    except Exception as e:
        print(f"⚠️ 发现AI抓取失败: {e}")
    return tools

# ========================
# 抓取国外：FutureTools.io（推荐！结构简单）
# ========================

def fetch_futuretools(max_items=10):
    tools = []
    try:
        res = requests.get("https://www.futuretools.io", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        # FutureTools 的工具卡片
        cards = soup.select('div[role="article"]')[:max_items]
        for card in cards:
            title_elem = card.select_one('h2 a')
            desc_elem = card.select_one('p')
            if not title_elem: continue
            title = title_elem.get_text(strip=True)
            desc = desc_elem.get_text(strip=True) if desc_elem else ""
            source = title_elem['href'] if title_elem.has_attr('href') else "#"
            tools.append({"title": title, "desc": desc, "source": source})
    except Exception as e:
        print(f"⚠️ FutureTools抓取失败: {e}")
    return tools

# ========================
# 手动兜底（确保不为空）
# ========================

def get_manual_tools():
    return {
        "cost": [
            {"title": "Doubao (豆包)", "desc": "Free AI assistant for customer service", "source": "https://www.doubao.com"},
            {"title": "WPS AI", "desc": "Automate office tasks, reduce software costs", "source": "https://www.wps.cn/ai"}
        ],
        "efficiency": [
            {"title": "Meitu (美图秀秀)", "desc": "AI photo editing in seconds", "source": "https://xiuxiu.meitu.com"},
            {"title": "Qwen (通义千问)", "desc": "Generate reports, emails, and summaries instantly", "source": "https://qwen.ai"},
            {"title": "Canva Magic Studio", "desc": "Create designs with text prompts", "source": "https://www.canva.com/magic-studio/"},
            {"title": "Notion AI", "desc": "Write, summarize, and organize your work", "source": "https://www.notion.so/product/ai"}
        ]
    }

# ========================
# 趋势新闻（保留）
# ========================

def get_trend_news(max_items=3):
    try:
        res = requests.get("https://36kr.com/newsflashes", headers=HEADERS, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        items = []
        for item in soup.select('div.newsflash-item')[:max_items]:
            title_elem = item.select_one('a.article-title')
            if not title_elem: continue
            title = title_elem.get_text(strip=True)
            link = "https://36kr.com" + title_elem['href'] if title_elem.has_attr('href') else "#"
            if any(kw in title for kw in ['AI', '人工智能', '大模型', 'AIGC']):
                items.append({"title": title, "desc": "Source: 36Kr", "source": link})
        return items or [{"title": "Global AI adoption accelerates", "desc": "Enterprise demand surges", "source": "https://36kr.com"}]
    except:
        return [{"title": "Trends loading...", "desc": "Check back later", "source": "#"}]

# ========================
# 主程序
# ========================

def main():
    print("🌍 开始抓取全球 AI 工具...")

    all_tools = []

    # 抓取国内外
    print("🇨🇳 抓取 发现AI...")
    all_tools.extend(fetch_faxianai())
    
    print("🌎 抓取 FutureTools...")
    all_tools.extend(fetch_futuretools())

    # 去重
    all_tools = deduplicate(all_tools)

    # 分类
    cost_list = []
    efficiency_list = []
    for tool in all_tools:
        category = classify_tool(tool['desc'], tool['title'])
        if category == "cost":
            cost_list.append(tool)
        else:
            efficiency_list.append(tool)

    # 如果抓取结果太少，补充手动数据
    manual = get_manual_tools()
    if len(cost_list) < 2:
        cost_list = manual["cost"]
    if len(efficiency_list) < 3:
        efficiency_list = manual["efficiency"]

    # 获取趋势
    trend = get_trend_news()

    # 保存
    data = {
        "cost": cost_list,
        "efficiency": efficiency_list,
        "trend": trend
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 成功生成 data.json！")
    print(f"   - 成本杀手: {len(cost_list)} 个（含国际工具）")
    print(f"   - 效率倍增: {len(efficiency_list)} 个（含国际工具）")
    print(f"   - 趋势雷达: {len(trend)} 条")

if __name__ == "__main__":
    main()