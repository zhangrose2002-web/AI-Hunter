# -*- coding: utf-8 -*-
"""
AI Hunter - 创业者质量保障版
1. 修复 os 模块缺失报错
2. 增强中英文分类识别，支持全球源
3. 自动剔除 403/404/失效链接
"""

import json
import requests
from bs4 import BeautifulSoup
import sys
import time
import os  # [核心修复] 补全缺失的 os 模块，解决写入失败问题

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- 关键词库：新增英文支持，确保 FutureTools 的洋工具能被正确分类 ---
COST_KEYWORDS = [
    '免费', '开源', '降本', '替代', '节省', '平替',
    'free', 'open source', 'save cost', 'replace', 'automate', 'low code'
]

EFFICIENCY_KEYWORDS = [
    '效率', '提效', '一键', '生成', '批量', '智能', '办公', '剪辑', '写作',
    'efficiency', 'productivity', 'boost', 'workflow', 'marketing', 'content creation'
]

def is_link_valid(url):
    """ 自动检测链接是否可用，跳过 trae.cn 等 403 错误 """
    if not url or url == "#":
        return False
    try:
        # 尝试快速检测
        res = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=True)
        if res.status_code >= 400:
            res = requests.get(url, headers=HEADERS, timeout=5, stream=True)
        return res.status_code == 200
    except:
        return False

def clean_text(text):
    return ''.join(c for c in str(text) if ord(c) >= 32).strip() if text else ""

def classify_tool(desc, title):
    """ 分类逻辑：通过中英文关键词计算得分 """
    text = (title + " " + desc).lower()
    cost_score = sum(2 if kw in text else 0 for kw in COST_KEYWORDS)
    eff_score = sum(1 if kw in text else 0 for kw in EFFICIENCY_KEYWORDS)
    
    if cost_score == 0 and eff_score == 0:
        return "efficiency"  # 兜底：未匹配到关键词的国外工具默认入提效类，防止丢失
    return "cost" if cost_score >= eff_score else "efficiency"

# --- 捕猎函数群 ---
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
            if is_link_valid(link): tools.append({"title": title, "desc": desc, "source": link})
    except Exception as e: print(f"⚠️ AI工具集跳过: {e}")
    return tools

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
            if is_link_valid(source): tools.append({"title": title, "desc": desc, "source": source})
    except Exception as e: print(f"⚠️ 发现AI跳过: {e}")
    return tools

def fetch_futuretools(max_items=25):
    print("🔍 猎捕中：FutureTools (全球源)...")
    tools = []
    try:
        res = requests.get("https://www.futuretools.io/?sort=date-added", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        cards = soup.select('div[role="article"]')[:max_items]
        for card in cards:
            title_elem = card.select_one('h2 a')
            desc_elem = card.select_one('p')
            if title_elem:
                link = title_elem['href'] if title_elem.has_attr('href') else "#"
                if is_link_valid(link):
                    tools.append({
                        "title": title_elem.get_text(strip=True),
                        "desc": desc_elem.get_text(strip=True) if desc_elem else "",
                        "source": link
                    })
    except Exception as e: print(f"⚠️ FutureTools跳过: {e}")
    return tools

def fetch_36kr_trends(max_items=6):
    print("📡 监测中：36Kr 趋势雷达...")
    trends = []
    try:
        res = requests.get("https://36kr.com/newsflashes", headers=HEADERS, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('a.article-title')
        growth_keywords = ['AI', '人工智能', '机器人', '创业', '融资', 'AIGC', '芯片']
        for item in items:
            title = clean_text(item.get_text(strip=True))
            link = "https://36kr.com" + item['href']
            if any(kw in title for kw in growth_keywords) and is_link_valid(link):
                trends.append({"title": title, "desc": "💡 商业趋势快报", "source": link})
            if len(trends) >= max_items: break
    except Exception as e: print(f"⚠️ 趋势抓取异常: {e}")
    return trends

def main():
    print("🚀 AI Hunter 质量保障版启动...")
    
    # 汇总
    raw_tools = []
    raw_tools.extend(fetch_aibot(20))
    raw_tools.extend(fetch_faxianai(15))
    raw_tools.extend(fetch_futuretools(25))

    # 去重
    unique_tools = []
    seen_titles = set()
    for t in raw_tools:
        name = t['title'].lower().strip()
        if name not in seen_titles:
            seen_titles.add(name)
            unique_tools.append(t)

    # 分类
    data = {"cost": [], "efficiency": [], "trend": []}
    for t in unique_tools:
        cat = classify_tool(t['desc'], t['title'])
        data[cat].append(t)

    # 趋势
    data["trend"] = fetch_36kr_trends(6)
    if not data["trend"]:
        data["trend"] = [{"title": "全球AI商业化白皮书：降本成核心", "desc": "💡 行业趋势", "source": "https://36kr.com"}]

    # 写入 JSON
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 写入成功！当前文件大小: {os.path.getsize('data.json')} 字节")
    except Exception as e:
        print(f"❌ 写入文件失败: {e}")

if __name__ == "__main__":
    main()
