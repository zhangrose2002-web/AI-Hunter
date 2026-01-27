import json
import os
import requests
import time
from datetime import datetime

# ==========================================
# 配置区域
# ==========================================
# 保持为空，系统会自动注入
API_KEY = "" 
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

# 1. 定义封焊机行业的核心关键词库
TARGET_KEYWORDS = [
    "红外探测器 封装厂家 扩产", 
    "MEMS传感器 气密性封焊 招标", 
    "平行封焊机 采购意向", 
    "激光封焊 模组企业 新闻",
    "碳化硅 SiC 功率器件 封装产线 建设",
    "石英晶体振荡器 制造企业 名单",
    "光通信 TO管壳 封装需求"
]

SYSTEM_PROMPT = """
你是一个封焊机行业的资深市场情报员。
你的任务是根据搜索结果，识别出那些可能需要采购“平行封焊机”或“激光封焊机”的潜在客户。
这些客户通常是半导体、传感器、光通信、功率器件的生产商。

对于每一个识别出的客户，请严格按照以下JSON格式输出列表：
{
    "name": "公司全称",
    "region": "国内/海外",
    "area": "省份·城市",
    "reason": "具体的需求线索描述，说明为什么要监控这家公司（如：近期扩产、中标新项目、发布新封装需求等）",
    "website": "官方网址或相关报道链接",
    "phone": "联系电话（如有，若无则填写暂无）",
    "crawlTime": "当前日期"
}
"""

def search_opportunities(keyword):
    """调用带有搜索工具的 Gemini API"""
    payload = {
        "contents": [{
            "parts": [{
                "text": f"基于关键词 '{keyword}'，请搜索并找出3-5家最近有扩产、新建产线或封装设备需求的潜在企业信息。"
            }]
        }],
        "systemInstruction": {
            "parts": [{ "text": SYSTEM_PROMPT }]
        },
        "tools": [{ "google_search": {} }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    # 指数退避重试机制
    for delay in [1, 2, 4, 8, 16]:
        try:
            response = requests.post(ENDPOINT, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                text_content = result['candidates'][0]['content']['parts'][0]['text']
                return json.loads(text_content)
            elif response.status_code == 429: # Rate limit
                time.sleep(delay)
            else:
                break
        except Exception as e:
            time.sleep(delay)
    return []

def run_crawler():
    print(f"[{datetime.now()}] 正在启动封焊设备目标客户检索...")
    
    all_results = []
    seen_names = set()

    for kw in TARGET_KEYWORDS:
        print(f"正在分析关键词: {kw} ...")
        items = search_opportunities(kw)
        
        if isinstance(items, list):
            for item in items:
                # 简单去重
                if item.get('name') and item['name'] not in seen_names:
                    item['crawlTime'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    all_results.append(item)
                    seen_names.add(item['name'])
        
        # 避免请求过快
        time.sleep(2)

    # 2. 确保保存的文件名为 data.json，供 index.html 读取
    output_path = 'data.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)
    
    print(f"检索完成，已更新 {len(all_results)} 家潜在客户到 {output_path}。")

if __name__ == "__main__":
    run_crawler()
