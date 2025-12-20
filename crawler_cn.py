# -*- coding: utf-8 -*-
import json, requests, os, sys
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def fetch_futuretools():
    print("🌍 正在深度扫描：FutureTools...")
    tools = []
    try:
        res = requests.get("https://www.futuretools.io/", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 修复：不再找 div，直接找所有包含 /tool/ 的链接，并向上寻找最接近的标题文本
        all_links = soup.find_all('a', href=True)
        for l in all_links:
            href = l['href']
            if '/tool/' in href and len(tools) < 15:
                # 尝试获取链接文本，如果太短，尝试获取父级元素的文本
                name = l.get_text(strip=True)
                if len(name) < 2: 
                    # 向上找两层，尝试抓取卡片标题
                    parent = l.parent.parent
                    name = parent.get_text(strip=True).split('\n')[0]
                
                if len(name) > 2 and name not in [t['title'] for t in tools]:
                    link = "https://www.futuretools.io" + href if href.startswith('/') else href
                    tools.append({"title": "🌐 " + name[:30], "desc": "Silicon Valley Hot Tool", "source": link})
    except Exception as e: print(f"⚠️ FutureTools 异常: {e}")
    return tools

def fetch_topai():
    print("🌍 正在深度扫描：Topai...")
    tools = []
    try:
        res = requests.get("https://topai.tools/new", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 修复：放弃 .card-title，寻找页面中所有的 h3/h4/h5 链接
        for heading in soup.find_all(['h3', 'h4', 'h5', 'div']):
            link_node = heading.find('a', href=True)
            if link_node and len(tools) < 10:
                name = link_node.get_text(strip=True)
                if name:
                    tools.append({"title": "🚀 " + name[:30], "desc": "International AI Release", "source": link_node['href']})
    except: pass
    return tools

def main():
    print("🚀 AI Hunter 全球同步系统 [深度版] 启动...")
    data = {"cost": [], "efficiency": [], "trend": []}
    
    # 1. 验证标记 (增加时间戳，防止缓存误判)
    import datetime
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    data["efficiency"].append({
        "title": f"🚨 同步成功反馈 [{now_str}]",
        "desc": "如果你看到本条，说明 GitHub 同步链路 100% 正常",
        "source": "http://cs.bj77.cn"
    })

    # 2. 多源混合抓取
    all_raw = fetch_futuretools() + fetch_topai()
    
    # 抓取国内 (AI工具集)
    try:
        res = requests.get("https://ai-bot.cn/", headers=HEADERS, timeout=10)
        cards = BeautifulSoup(res.text, 'html.parser').select('.url-card')[:15]
        for c in cards:
            all_raw.append({
                "title": c.select_one('strong').get_text(strip=True),
                "desc": c.select_one('.url-info p').get_text(strip=True),
                "source": c.select_one('a')['href']
            })
    except: pass

    # 3. 去重与强制分类
    seen = set()
    for t in all_raw:
        title_clean = t['title'].replace("🌐 ", "").replace("🚀 ", "").lower().strip()
        if title_clean not in seen:
            seen.add(title_clean)
            # 只要是带地球/火箭图标的，或者是英文名，直接进 efficiency
            if "🌐" in t['title'] or "🚀" in t['title'] or any(ord(c) < 128 for c in t['title'][:5]):
                data["efficiency"].append(t)
            else:
                data["cost"].append(t)

    # 4. 资讯雷达
    try:
        res = requests.get("https://36kr.com/newsflashes", headers=HEADERS, timeout=10)
        items = BeautifulSoup(res.text, 'html.parser').select('a.article-title')[:6]
        data["trend"] = [{"title": "🔥 " + i.get_text(strip=True), "desc": "实时快讯", "source": "https://36kr.com" + i['href']} for i in items]
    except: pass

    # 5. 写入
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 竣工！文件大小: {os.path.getsize('data.json')} 字节")
    except Exception as e: print(f"❌ 写入失败: {e}")

if __name__ == "__main__":
    main()
