import os
import re
import json
import requests
from datetime import datetime

# 模拟抓取逻辑（实际可对接具体 API 或 BeautifulSoup 爬取）
def fetch_industry_leads():
    print("开始执行全网线索搜寻...")
    # 这里定义你的关键词矩阵逻辑
    # 示例数据：实际开发中这里是爬虫抓取回来的结果
    new_leads = [
        {
            "id": int(datetime.now().timestamp()),
            "company": "某头部功率半导体厂",
            "location": "广东·深圳",
            "category": "domestic",
            "reason": "新增 [SiC功率器件] 封装产线招标，急需 [真空平行缝焊机] 及气密性检测设备。",
            "website": "example.com",
            "phone": "见招标公告",
            "tag": "新增产线"
        },
        {
            "id": int(datetime.now().timestamp()) + 1,
            "company": "Global Opto-Tech Inc.",
            "location": "新加坡 / 海外",
            "category": "intl",
            "reason": "[800G光模块] 产能翻倍计划启动，涉及 [TO-CAN封装] 及 [EML激光器] 封焊工艺升级。",
            "website": "globalopto.com",
            "phone": "Global Office",
            "tag": "产能翻倍"
        }
    ]
    return new_leads

def update_index_html(new_data):
    file_path = 'index.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到 leadsData 数组并替换
    # 使用正则匹配 /* DATA_START */ 和 /* DATA_END */ 之间的内容
    pattern = r'/\* DATA_START \*/(.*?)/\* DATA_END \*/'
    
    # 将新数据转为格式化的 JS 数组
    js_data_str = f"\n    const leadsData = {json.dumps(new_data, ensure_ascii=False, indent=6)};\n    "
    
    new_content = re.sub(pattern, f"/* DATA_START */{js_data_str}/* DATA_END */", content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("首页数据已完成热更新。")

if __name__ == "__main__":
    leads = fetch_industry_leads()
    update_index_html(leads)
