# -*- coding: utf-8 -*-
import json, requests, os, sys
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def fetch_futuretools():
    print("🌍 捕猎源 1: FutureTools...")
    tools = []
    try:
        res = requests.get("https://www.futuretools.io/?sort=date-added", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.find_all('a', href=True)
        for l in links:
            if '/tool/' in l['href'] and len(tools) < 10:
                tools.append({"title": "🌐 " + l.get_text(strip=True), "desc": "Silicon Valley Trend", "source": "https://www.futuretools.io" + l['href']})
    except: pass
    return tools

def fetch_topai():
    print("🌍 捕猎源 2: Topai.tools...")
    tools = []
    try:
        res = requests.get("https://topai.tools/new", headers=HEADERS, timeout=15)
        cards = BeautifulSoup(res.text, 'html.parser').select('.card-title a')[:10]
        for c in cards:
            tools.append({"title": "🚀 " + c.get_text(strip=True), "desc": "Global New Release", "source": c['href'] if c['href'].startswith('http') else "https://topai.tools" + c['href']})
    except: pass
    return tools

def fetch_aibot():
    print("🔍 捕猎源 3: AI工具集 (国内)...")
    tools = []
    try:
        res = requests.get("https://ai-bot.cn/", headers=HEADERS, timeout=10)
        cards = BeautifulSoup(res.text, 'html.parser').select('.url-card')[:15]
        for c in cards:
            tools.append({"title": c.select_one('strong').get_text(strip=True), "desc": c.select_one('.url-info p').get_text(strip=True), "source": c.select_one('a')['href']})
    except: pass
    return tools

def main():
    print("🚀 全球 AI 猎捕系统启动...")
    data = {"cost": [], "efficiency": [], "trend": []}
    
    # 汇总所有源
    all_raw = fetch_futuretools() + fetch_topai() + fetch_aibot()
    
    # 强制标记：用于检查同步是否成功
    data["efficiency"].append({
        "title": "🚨 全球多源同步已开启",
        "desc": "当前已集成 FutureTools + Topai + 国内精选",
        "source": "http://cs.bj77.cn"
    })

    # 分类逻辑
    seen = set()
    for t in all_raw:
        name = t['title'].lower().strip()
        if name not in seen:
            seen.add(name)
            # 简单的关键词分类
            if any(kw in (t['title']+t['desc']).lower() for kw in ['free', '免费', '开源', 'save']):
                data["cost"].append(t)
            else:
                data["efficiency"].append(t)

    # 趋势雷达（保持多源抓取逻辑）
    try:
        res = requests.get("https://36kr.com/newsflashes", headers=HEADERS, timeout=10)
        items = BeautifulSoup(res.text, 'html.parser').select('a.article-title')[:6]
        data["trend"] = [{"title": "🔥 " + i.get_text(strip=True), "desc": "实时热点", "source": "https://36kr.com" + i['href']} for i in items]
    except: pass

    # 写入文件
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 竣工！文件大小: {os.path.getsize('data.json')} 字节")
    except Exception as e: print(f"❌ 失败: {e}")

if __name__ == "__main__": main()
