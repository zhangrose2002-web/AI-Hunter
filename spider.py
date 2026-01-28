import os
import json
import time
import random
import urllib.parse
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_industry_leads():
    # 关键词列表
    raw_keywords = ["半导体 招标", "封测 扩产", "光模块 采购", "通富微电 公告", "长电科技 招标"]
    selected_kws = random.sample(raw_keywords, 3)
    real_leads = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"📡 启动扫描: {selected_kws}")

    for kw in selected_kws:
        try:
            query = urllib.parse.quote(kw)
            url = f"https://www.baidu.com/s?wd={query}"
            time.sleep(2)
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('.result')
            
            for item in items[:2]:
                title_el = item.select_one('h3')
                if title_el:
                    title = title_el.get_text().strip()
                    real_leads.append({
                        "id": int(time.time()) + random.randint(1, 999),
                        "company": title[:20],
                        "location": "实时更新",
                        "category": "domestic",
                        "tag": "行业动态",
                        "reason": f"搜索发现线索: {title[:40]}...",
                        "website": "#",
                        "phone": "见官网"
                    })
            print(f"✅ 完成 [{kw}]")
        except Exception as e:
            print(f"⚠️ 跳过 [{kw}]: {e}")

    # 保底数据
    if not real_leads:
        real_leads = [{
            "id": 1,
            "company": "AI 猎人系统节点",
            "location": "监控中",
            "category": "domestic",
            "tag": "系统状态",
            "reason": "搜索引擎接口响应中，请稍后刷新获取最新招标线索。",
            "website": "#",
            "phone": "400-888"
        }]
    return real_leads

if __name__ == "__main__":
    data = fetch_industry_leads()
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("🚀 数据保存成功")
