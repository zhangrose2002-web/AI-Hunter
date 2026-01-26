import json
import os

# 1. 定义封焊机行业的核心关键词库
# 这些词决定了爬虫去哪里找客户
TARGET_KEYWORDS = [
    "红外探测器 封装厂家", 
    "MEMS传感器 气密性封焊", 
    "平行封焊机 采购", 
    "激光封焊 模组企业",
    "碳化硅 SiC 功率器件 封装",
    "石英晶体振荡器 制造",
    "光通信 TO管壳 封装"
]

def run_crawler():
    print("正在启动封焊设备目标客户检索...")
    
    # 这里是您的爬虫主逻辑
    # 逻辑修改点：将原有的 AI 搜索接口调用改为针对以上 TARGET_KEYWORDS 的搜索
    
    new_data = [
        {
            "name": "某传感器技术有限公司",
            "industry": "MEMS/红外探测器",
            "location": "江苏·无锡",
            "reason": "该司近期扩产红外探测器生产线，对气密性封焊设备有潜在需求。",
            "tags": ["平行封焊", "高气密性"],
            "url": "http://example.com"
        },
        {
            "name": "华南某功率半导体厂",
            "industry": "碳化硅/IGBT",
            "location": "广东·深圳",
            "reason": "新增多条碳化硅模块封测产线，正在寻找激光封焊解决方案。",
            "tags": ["激光封焊", "大功率模块"],
            "url": "http://example.com"
        }
    ]
    
    # 2. 确保保存的文件名为 data.json，供 index.html 读取
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)
    
    print(f"检索完成，已更新 {len(new_data)} 家潜在客户。")

if __name__ == "__main__":
    run_crawler()
