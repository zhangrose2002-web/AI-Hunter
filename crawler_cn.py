# -*- coding: utf-8 -*-
"""
AI Hunter - 创业者加强版 (全球猎捕 + 自动链接体检)
功能：抓取数据 -> 自动检测链接 -> 剔除异常(403/404/超时) -> 生成 data.json
"""

import json
import requests
from bs4 import BeautifulSoup
import sys
import time
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- 关键词库 ---
COST_KEYWORDS = ['免费', '开源', '降本', '替代', '自动化', '人力', '节省', '平替', 'free', 'save cost', 'low code']
EFFICIENCY_KEYWORDS = ['效率', '提效', '一键', '生成', '批量', '智能', '办公', '营销', '写作', 'efficiency', 'productivity']

def is_link_valid(url):
    """
    【核心新增】链接体检函数
    尝试访问链接，如果返回非200状态码或超时，则视为异常
    """
    if not url or url == "#":
        return False
    try:
        # 使用 HEAD 请求快速检测，设置 5 秒超时
        # allow_redirects=True 允许自动跳转到最终地址
        response = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=True)
        
        # 如果 HEAD 请求不被允许(有些站报405)，则尝试 GET 请求只读取前 1 字节
        if response.status_code >= 400:
            response = requests.get(url, headers=HEADERS, timeout=5, stream=True)
            
        if response.status_code == 200:
            return True
        else:
            print(f"❌ 链接失效 ({response.status_code}): {url}")
            return False
    except Exception as e:
        print(f"❌ 链接无法连接: {url} | 错误: {e}")
        return False

def clean_text(text):
    return ''.join(c for c in str(text) if ord(c) >= 32).strip() if text else ""

def classify_tool(desc, title):
    text = (title + " " + desc).lower()
    cost_score = sum(2 if kw in text else 0 for kw in COST_KEYWORDS)
    eff_score = sum(1 if kw in text else 0 for kw in EFFICIENCY_KEYWORDS)
    return "cost" if cost_score >= eff_score and cost_score > 0 else "efficiency"

# --- 捕猎函数 (逻辑同原版) ---
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
            # 在这里直接进行体检
            if is_link_valid(link):
                tools.append({"title": title, "desc": desc, "source": link})
    except Exception as e: print(f"⚠️ AI工具集捕获跳过: {e}")
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
            # 注意：源站链接也要检查
            if is_link_valid(source):
                tools.append({"title": title, "desc": desc, "source": source})
    except Exception as e: print(f"⚠️ 发现AI捕获跳过: {e}")
    return tools

def fetch_futuretools(max_items=20):
    print("🔍 猎捕中：FutureTools (全球)...")
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
    except Exception as e: print(f"⚠️ FutureTools捕获跳过: {e}")
    return tools

def fetch_36kr_trends(max_items=6):
    print("📡 监测中：36Kr 趋势雷达...")
    trends = []
    try:
        res = requests.get("https://36kr.com/newsflashes", headers=HEADERS, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('a.article-title')
        growth_keywords = ['AI', '人工智能', '机器人', '数字化', '创业', '融资', 'AIGC']
        
        for item in items:
            title = clean_text(item.get_text(strip=True))
            link = "https://36kr.com" + item['href']
            if any(kw.lower() in title.lower() for kw in growth_keywords):
                # 趋势链接也要检查
                if is_link_valid(link):
                    trends.append({"title": title, "desc": "💡 商业趋势快报", "source": link})
            if len(trends) >= max_items: break
    except Exception as e: print(f"⚠️ 趋势捕获异常: {e}")
    return trends

def main():
    print("🚀 AI Hunter 启动，正在进行‘质量保障型’猎捕...")
    
    raw_tools = []
    raw_tools.extend(fetch_aibot(20))
    raw_tools.extend(fetch_faxianai(15))
    raw_tools.extend(fetch_futuretools(20))

    # 去重处理
    unique_tools = []
    seen_titles = set()
    for t in raw_tools:
        name = t['title'].lower().strip()
        if name not in seen_titles:
            seen_titles.add(name)
            unique_tools.append(t)

    data = {"cost": [], "efficiency": [], "trend": []}
    for t in unique_tools:
        cat = classify_tool(t['desc'], t['title'])
        if cat in data:
            data[cat].append(t)

    data["trend"] = fetch_36kr_trends(6)

    # 兜底趋势
    if not data["trend"]:
        data["trend"] = [
            {"title": "2025 AI 商业化趋势：降本增效成核心", "desc": "💡 行业趋势", "source": "https://36kr.com"},
            {"title": "全球 AI Agents 技术栈趋于成熟", "desc": "⚡ 效能趋势", "source": "https://36kr.com"}
        ]

    # 写入 JSON
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 成功生成 data.json！异常链接已自动过滤。")
    except Exception as e:
        print(f"❌ 写入文件失败: {e}")

if __name__ == "__main__":
    main()
