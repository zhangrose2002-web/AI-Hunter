# -*- coding: utf-8 -*-
"""
AI Hunter - 全球版（GitHub Actions 优化版）
抓取国内外热门 AI 工具，并智能分类到 cost / efficiency
自动去重、兜底、生成标准 data.json
"""

import json
import requests
from bs4 import BeautifulSoup
import sys
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

def clean_text(text):
    """安全清理文本：移除控制字符，保留合法空白"""
    if not text:
        return ""
    return ''.join(c for c in str(text) if ord(c) >= 32 or c in '\n\t\r')

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
    text = (clean_text(title) + " " + clean_text(desc)).lower()
    cost_score = sum(1 for kw in COST_KEYWORDS if kw in text)
    eff_score = sum(1 for kw in EFFICIENCY_KEYWORDS if kw in text)
    return "cost" if cost_score > eff_score else "efficiency"

def deduplicate(tools):
    seen = set()
    unique = []
    for t in tools:
        key = clean_text(t['title']).strip().lower()
        if key and key not in seen:
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
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        cards = soup.select('a[href^="/tool/"]')[:max_items]
        for card in cards:
            title_elem = card.select_one('h3')
            desc_elem = card.select_one('p')
            tag_elem = card.select_one('span.bg-blue-100')
            title = clean_text(title_elem.get_text(strip=True)) if title_elem else ""
            desc = clean_text(desc_elem.get_text(strip=True)) if desc_elem else ""
            tag = clean_text(tag_elem.get_text(strip=True)) if tag_elem else ""
            source = "https://faxianai.com" + card['href']
            if title:
                tools.append({"title": title, "desc": f"{desc} {tag}".strip(), "source": source})
    except Exception as e:
        print(f"⚠️ 发现AI抓取失败: {e}")
    return tools

# ========================
# 抓取国外：FutureTools.io
# ========================

def fetch_futuretools(max_items=10):
    tools = []
    try:
        res = requests.get("https://www.futuretools.io", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        cards = soup.select('div[role="article"]')[:max_items]
        for card in cards:
            title_elem = card.select_one('h2 a')
            desc_elem = card.select_one('p')
            if not title_elem:
                continue
            title = clean_text(title_elem.get_text(strip=True))
            desc = clean_text(desc_elem.get_text(strip=True)) if desc_elem else ""
            source = title_elem['href'] if title_elem.has_attr('href') else "#"
            if title:
                tools.append({"title": title, "desc": desc, "source": source})
    except Exception as e:
        print(f"⚠️ FutureTools抓取失败: {e}")
    return tools

# ========================
# 手动兜底数据
# ========================

def get_manual_tools():
    return {
        "cost": [
            {"title": "Doubao (豆包)", "desc": "免费 AI 助手，适用于客服与日常问答", "source": "https://www.doubao.com"},
            {"title": "WPS AI", "desc": "自动化办公任务，降低软件采购与人力成本", "source": "https://www.wps.cn/ai"}
        ],
        "efficiency": [
            {"title": "美图秀秀", "desc": "AI 一键修图、抠图、美化，秒出专业效果", "source": "https://xiuxiu.meitu.com"},
            {"title": "通义千问 (Qwen)", "desc": "自动生成周报、邮件、总结，提升写作效率", "source": "https://qwen.ai"},
            {"title": "Canva Magic Studio", "desc": "用文字生成海报、PPT、社交媒体图", "source": "https://www.canva.com/magic-studio/"},
            {"title": "Notion AI", "desc": "智能整理笔记、生成待办、总结长文", "source": "https://www.notion.so/product/ai"}
        ]
    }

# ========================
# 趋势新闻（36氪）
# ========================

def get_trend_news(max_items=3):
    try:
        res = requests.get("https://36kr.com/newsflashes", headers=HEADERS, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        items = []
        for item in soup.select('div.newsflash-item')[:max_items]:
            title_elem = item.select_one('a.article-title')
            if not title_elem:
                continue
            title = clean_text(title_elem.get_text(strip=True))
            link = "https://36kr.com" + title_elem['href'] if title_elem.has_attr('href') else "#"
            if any(kw in title for kw in ['AI', '人工智能', '大模型', 'AIGC', '生成式']):
                items.append({"title": title, "desc": "来源：36Kr", "source": link})
        return items or [{"title": "全球 AI 应用加速落地", "desc": "企业需求激增", "source": "https://36kr.com"}]
    except Exception as e:
        print(f"⚠️ 趋势新闻抓取失败: {e}")
        return [{"title": "趋势加载中...", "desc": "请稍后刷新", "source": "#"}]

# ========================
# 主程序
# ========================

def main():
    print("🚀 开始抓取全球 AI 工具...")

    all_tools = []

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

    # 限制数量（防止前端过载）
    cost_list = cost_list[:5]
    efficiency_list = efficiency_list[:8]

    # 兜底
    manual = get_manual_tools()
    if len(cost_list) < 2:
        cost_list = manual["cost"]
    if len(efficiency_list) < 3:
        efficiency_list = manual["efficiency"]

    # 趋势
    trend = get_trend_news()

    # 构建最终数据
    data = {
        "cost": cost_list,
        "efficiency": efficiency_list,
        "trend": trend
    }

    # 安全写入 data.json
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 成功生成 data.json！")
        print(f"   - 成本杀手: {len(cost_list)} 个")
        print(f"   - 效率倍增: {len(efficiency_list)} 个")
        print(f"   - 趋势雷达: {len(trend)} 条")
    except Exception as e:
        print(f"❌ 写入 data.json 失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()