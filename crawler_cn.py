# -*- coding: utf-8 -*-
import json, requests, os, sys
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def is_link_valid(url):
    """ 链接体检：仅针对国内源，防止 403 导致过滤 """
    if not url or url == "#": return False
    try:
        # 国外源容易误报 403，因此体检逻辑只留给国内
        res = requests.get(url, headers=HEADERS, timeout=5, stream=True)
        return res.status_code < 400
    except: return False

def fetch_futuretools():
    print("🌍 正在猎捕：FutureTools (全球源)...")
    tools = []
    try:
        res = requests.get("https://www.futuretools.io/?sort=date-added", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 改用更强大的链接匹配，不依赖特定的 div 结构
        links = soup.find_all('a', href=True)
        for l in links:
            href = l['href']
            if '/tool/' in href and len(tools) < 15:
                title = l.get_text(strip=True)
                if len(title) > 3:
                    tools.append({
                        "title": "🌐 " + title,
                        "desc": "Global Emerging AI Technology",
                        "source": "https://www.futuretools.io" + href if href.startswith('/') else href
                    })
    except: pass
    return tools

def fetch_topai():
    print("🌍 正在猎捕：Topai.tools (备用源)...")
    tools = []
    try:
        res = requests.get("https://topai.tools/new", headers=HEADERS, timeout=15)
        cards = BeautifulSoup(res.text, 'html.parser').select('.card-title a')[:10]
        for c in cards:
            tools.append({"title": "🚀 " + c.get_text(strip=True), "desc": "International AI Release", "source": c['href']})
    except: pass
    return tools

def fetch_aibot():
    print("🔍 猎捕中：AI工具集 (国内)...")
    tools = []
    try:
        res = requests.get("https://ai-bot.cn/", headers=HEADERS, timeout=10)
        cards = BeautifulSoup(res.text, 'html.parser').select('.url-card')[:15]
        for c in cards:
            link = c.select_one('a')['href']
            if is_link_valid(link): # 国内链接依然保持体检
                tools.append({
                    "title": c.select_one('strong').get_text(strip=True),
                    "desc": c.select_one('.url-info p').get_text(strip=True),
                    "source": link
                })
    except: pass
    return tools

def main():
    print("🚀 AI Hunter 全球同步系统启动...")
    data = {"cost": [], "efficiency": [], "trend": []}
    
    # 强制标记：看到这个说明同步成功了！
    data["efficiency"].append({
        "title": "🚨 系统更新：全球多源同步已开启 (2025)",
        "desc": "如果看到此条，说明数据已成功同步至服务器",
        "source": "http://cs.bj77.cn"
    })

    # 抓取三方工具并汇总
    all_tools = fetch_futuretools() + fetch_topai() + fetch_aibot()
    
    # 分类逻辑：放宽分类分值，不漏掉一个
    seen = set()
    for t in all_tools:
        name = t['title'].lower().strip()
        if name not in seen:
            seen.add(name)
            # 只要带有 🌐 或 🚀 图标的，通通分入 efficiency
            if any(icon in t['title'] for icon in ["🌐", "🚀"]):
                data["efficiency"].append(t)
            elif any(kw in (t['title'] + t['desc']).lower() for kw in ['免费', '开源', 'free', 'save']):
                data["cost"].append(t)
            else:
                data["efficiency"].append(t)

    # 资讯雷达多源抓取
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
    except Exception as e: print(f"❌ 写入失败: {e}")

if __name__ == "__main__":
    main()
