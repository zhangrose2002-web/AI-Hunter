# -*- coding: utf-8 -*-
import json, requests, os, sys
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def is_link_valid(url):
    """ 仅对国内源进行体检，防止程序卡死 """
    if not url or url == "#" or "trae.cn" in url: return False
    try:
        res = requests.get(url, headers=HEADERS, timeout=5, stream=True)
        return res.status_code < 400
    except: return False

def fetch_futuretools():
    print("🌍 正在猎捕：FutureTools (全球源)...")
    tools = []
    try:
        # 尝试访问其按日期排序的页面
        res = requests.get("https://www.futuretools.io/?sort=date-added", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 改用更鲁棒的选择器查找所有包含链接的标题
        links = soup.find_all('a', href=True)
        for l in links:
            href = l['href']
            # 过滤出真正的工具详情页链接
            if '/tool/' in href and len(tools) < 20:
                title = l.get_text(strip=True)
                if title and len(title) > 2:
                    full_link = "https://www.futuretools.io" + href if href.startswith('/') else href
                    tools.append({
                        "title": "🌐 " + title,
                        "desc": "Global Emerging AI Technology",
                        "source": full_link
                    })
    except Exception as e: print(f"⚠️ FutureTools 抓取异常: {e}")
    return tools

def fetch_aibot():
    print("🔍 猎捕中：AI工具集 (国内)...")
    tools = []
    try:
        res = requests.get("https://ai-bot.cn/", headers=HEADERS, timeout=10)
        cards = BeautifulSoup(res.text, 'html.parser').select('.url-card')[:20]
        for c in cards:
            link = c.select_one('a')['href']
            if is_link_valid(link): # 国内工具依然保留体检
                tools.append({
                    "title": c.select_one('strong').get_text(strip=True),
                    "desc": c.select_one('.url-info p').get_text(strip=True),
                    "source": link
                })
    except: pass
    return tools

def fetch_multi_trends():
    print("📡 趋势雷达：多源情报整合中...")
    trends = []
    # 源 1: 36Kr
    try:
        res = requests.get("https://36kr.com/newsflashes", headers=HEADERS, timeout=10)
        res.encoding = 'utf-8'
        items = BeautifulSoup(res.text, 'html.parser').select('a.article-title')[:4]
        for i in items:
            trends.append({"title": "🔥 " + i.get_text(strip=True), "desc": "36Kr 快讯", "source": "https://36kr.com" + i['href']})
    except: pass
    # 源 2: V2EX
    try:
        res = requests.get("https://www.v2ex.com/go/ai", headers=HEADERS, timeout=10)
        items = BeautifulSoup(res.text, 'html.parser').select('.item_title a')[:3]
        for i in items:
            trends.append({"title": "💻 " + i.get_text(strip=True), "desc": "社区热议", "source": "https://www.v2ex.com" + i['href']})
    except: pass
    return trends

def main():
    print("🚀 AI Hunter 启动...")
    data = {"cost": [], "efficiency": [], "trend": []}
    
    # 获取并合并所有工具
    tools = fetch_aibot() + fetch_futuretools()
    
    # 简单的分类逻辑：带图标的进效率类，其余按关键词
    for t in tools:
        if "🌐" in t['title']:
            data["efficiency"].append(t)
        elif any(kw in (t['title'] + t['desc']).lower() for kw in ['免费', '开源', 'save', 'free']):
            data["cost"].append(t)
        else:
            data["efficiency"].append(t)

    data["trend"] = fetch_multi_trends()
    
    # 写入文件
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 成功写入 data.json, 大小: {os.path.getsize('data.json')} 字节")
    except Exception as e: print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()
