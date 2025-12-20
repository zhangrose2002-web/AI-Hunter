# -*- coding: utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import sys
import time
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- 关键词库：支持中英文识别 ---
COST_KEYWORDS = ['免费', '开源', '降本', '节省', '平替', 'free', 'open source', 'save cost', 'low code']
EFFICIENCY_KEYWORDS = ['提效', '智能', '一键', '办公', '剪辑', '写作', 'efficiency', 'productivity', 'boost', 'automate']

def is_link_valid(url):
    """ 链接体检：跳过死链 """
    if not url or url == "#": return False
    if "futuretools.io" in url: return True # 国外源体检容易误报，直接放行
    try:
        res = requests.get(url, headers=HEADERS, timeout=8, stream=True)
        return res.status_code < 400
    except: return False

def clean_text(text):
    return ''.join(c for c in str(text) if ord(c) >= 32).strip() if text else ""

def classify_tool(desc, title):
    """ 分类逻辑：确保国外工具也能分入 efficiency """
    text = (title + " " + desc).lower()
    cost_score = sum(2 if kw in text else 0 for kw in COST_KEYWORDS)
    return "cost" if cost_score > 0 else "efficiency"

# --- 工具抓取：国内+国外 ---
def fetch_aibot():
    tools = []
    try:
        res = requests.get("https://ai-bot.cn/", headers=HEADERS, timeout=10)
        cards = BeautifulSoup(res.text, 'html.parser').select('.url-card')[:20]
        for c in cards:
            tools.append({
                "title": c.select_one('strong').get_text(strip=True),
                "desc": c.select_one('.url-info p').get_text(strip=True),
                "source": c.select_one('a')['href']
            })
    except: pass
    return tools

def fetch_futuretools():
    print("🌍 正在猎捕：FutureTools (全球源)...")
    tools = []
    try:
        res = requests.get("https://www.futuretools.io/?sort=date-added", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        cards = soup.select('div[role="article"]')[:20]
        for card in cards:
            t_elem = card.select_one('h2 a')
            if t_elem:
                tools.append({
                    "title": "🌐 " + t_elem.get_text(strip=True),
                    "desc": "Global AI Tool Insight",
                    "source": t_elem['href']
                })
    except: pass
    return tools

# --- 趋势雷达：多源整合 (36Kr + IT桔子 + 机器之心) ---
def fetch_global_trends():
    print("📡 趋势雷达：正在扫描全网情报...")
    trends = []
    
    # 源 1: 36Kr (综合快讯)
    try:
        res = requests.get("https://36kr.com/newsflashes", headers=HEADERS, timeout=10)
        res.encoding = 'utf-8'
        items = BeautifulSoup(res.text, 'html.parser').select('a.article-title')[:3]
        for i in items:
            trends.append({"title": "🔥 " + clean_text(i.get_text()), "desc": "36Kr 实时快讯", "source": "https://36kr.com" + i['href']})
    except: pass

    # 源 2: 机器之心 (深度技术)
    try:
        res = requests.get("https://www.jiqizhixin.com/", headers=HEADERS, timeout=10)
        items = BeautifulSoup(res.text, 'html.parser').select('.article-title')[:2]
        for i in items:
            trends.append({"title": "🧠 " + i.get_text(strip=True), "desc": "机器之心技术深度", "source": "https://www.jiqizhixin.com" + i['href']})
    except: pass

    # 源 3: V2EX (独立开发/社区热点)
    try:
        res = requests.get("https://www.v2ex.com/go/ai", headers=HEADERS, timeout=10)
        items = BeautifulSoup(res.text, 'html.parser').select('.item_title a')[:2]
        for i in items:
            trends.append({"title": "💻 " + i.get_text(strip=True), "desc": "V2EX 社区热议", "source": "https://www.v2ex.com" + i['href']})
    except: pass

    # 兜底：如果上面都挂了，不让页面空白
    if len(trends) < 3:
        trends.append({"title": "💡 AI 创业者需关注：模型降本与 Agent 落地", "desc": "行业分析", "source": "https://36kr.com"})
    
    return trends[:8] # 最多显示 8 条

def main():
    print("🚀 AI Hunter 全球商机系统启动...")
    data = {"cost": [], "efficiency": [], "trend": []}
    
    # 1. 抓取工具
    raw_tools = fetch_aibot() + fetch_futuretools()
    
    # 2. 去重与分类
    seen = set()
    for t in raw_tools:
        name = t['title'].lower().strip()
        if name not in seen:
            seen.add(name)
            data[classify_tool(t['desc'], t['title'])].append(t)

    # 3. 抓取多源趋势
    data["trend"] = fetch_global_trends()

    # 4. 写入文件
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 竣工！成功写入 {os.path.getsize('data.json')} 字节")
    except Exception as e:
        print(f"❌ 失败: {e}")

if __name__ == "__main__":
    main()
