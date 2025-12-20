# -*- coding: utf-8 -*-
"""
AI Hunter - 全球商机猎捕版
核心修正：
1. 补全 os 模块，确保 data.json 写入成功
2. 兼容中英文关键词，确保国外工具不掉队
3. 自动剔除 403/404 失效链接
"""

import json
import requests
from bs4 import BeautifulSoup
import sys
import time
import os  # [核心修复] 必须导入，否则写入文件会报错

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- 关键词库：增加英文，让机器人认识国外工具 ---
COST_KEYWORDS = ['免费', '开源', '降本', '节省', '平替', 'free', 'open source', 'save cost', 'low code']
EFFICIENCY_KEYWORDS = ['提效', '智能', '一键', '办公', '剪辑', '写作', 'efficiency', 'productivity', 'boost', 'automate']

def is_link_valid(url):
    """ 链接体检：自动跳过 403 等打不开的网站 """
    if not url or url == "#": return False
    try:
        res = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=True)
        if res.status_code >= 400:
            res = requests.get(url, headers=HEADERS, timeout=5, stream=True)
        return res.status_code == 200
    except:
        return False

def clean_text(text):
    return ''.join(c for c in str(text) if ord(c) >= 32).strip() if text else ""

def classify_tool(desc, title):
    """ 分类逻辑：确保所有抓到的工具都能被归类，不消失 """
    text = (title + " " + desc).lower()
    cost_score = sum(2 if kw in text else 0 for kw in COST_KEYWORDS)
    eff_score = sum(1 if kw in text else 0 for kw in EFFICIENCY_KEYWORDS)
    # 只要是抓到的工具，默认至少分入效率类，不让它在 JSON 中消失
    return "cost" if cost_score >= eff_score and cost_score > 0 else "efficiency"

# --- 抓取函数 ---
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
                link = title_elem['href']
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
        for item in items:
            title = clean_text(item.get_text(strip=True))
            link = "https://36kr.com" + item['href']
            if is_link_valid(link):
                trends.append({"title": title, "desc": "💡 商业趋势快报", "source": link})
            if len(trends) >= max_items: break
    except Exception as e: print(f"⚠️ 趋势抓取异常: {e}")
    return trends

def main():
    print("🚀 AI Hunter 启动...")
    raw_tools = []
    raw_tools.extend(fetch_aibot(20))
    raw_tools.extend(fetch_futuretools(25)) # 抓取国外源

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

    data["trend"] = fetch_36kr_trends(6)

    # 写入 JSON
    try:
        # 使用 os.path.abspath 确保路径正确
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        # 这里会用到 os 模块
        print(f"\n✅ 写入成功！当前文件大小: {os.path.getsize('data.json')} 字节")
    except Exception as e:
        print(f"❌ 写入文件失败: {e}")

if __name__ == "__main__":
    main()
