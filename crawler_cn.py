import requests
import re
import json
import time
import hashlib
from datetime import datetime

class AIHunterMonitor:
    def __init__(self, target_url):
        self.target_url = target_url
        self.last_data_hash = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def get_data_hash(self, data_str):
        """计算数据的哈希值，用于比对内容是否变化"""
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()

    def fetch_leads(self):
        try:
            # 1. 获取网页源码
            response = requests.get(self.target_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            html = response.text

            # 2. 使用正则表达式提取 JS 中的 leadsData 数组
            # 匹配 const leadsData = [ ... ]; 结构
            pattern = re.compile(r'const leadsData = (\[.*?\]);', re.DOTALL)
            match = pattern.search(html)

            if not match:
                print(f"[{datetime.now()}] 错误: 未能在页面中找到 leadsData 数据结构")
                return None

            json_str = match.group(1)
            
            # 3. 检查数据是否更新
            current_hash = self.get_data_hash(json_str)
            if current_hash == self.last_data_hash:
                print(f"[{datetime.now()}] 状态: 扫描完毕，数据无变化")
                return None

            self.last_data_hash = current_hash
            
            # 4. 解析 JSON 数据
            leads = json.loads(json_str)
            return leads

        except Exception as e:
            print(f"[{datetime.now()}] 抓取异常: {e}")
            return None

    def process_leads(self, leads):
        """处理抓取到的新数据"""
        print(f"\n{'='*20} 发现数据更新！ {'='*20}")
        for lead in leads:
            print(f"ID: {lead['id']}")
            print(f"公司: {lead['company']}")
            print(f"标签: {lead['tag']}")
            print(f"地区: {lead['location']}")
            print(f"理由: {lead['reason']}")
            print(f"网站: {lead['website']}")
            print(f"电话: {lead['phone']}")
            print("-" * 50)
        print(f"{'='*55}\n")

    def start_monitoring(self, interval=60):
        """
        开始不间断监控
        :param interval: 抓取间隔时间（秒），默认60秒
        """
        print(f"AI 猎人 INSIGHT 监控启动...")
        print(f"目标地址: {self.target_url}")
        print(f"抓取频率: 每 {interval} 秒/次")
        print("-" * 50)

        while True:
            leads = self.fetch_leads()
            if leads:
                self.process_leads(leads)
            
            # 等待下一次抓取
            time.sleep(interval)

if __name__ == "__main__":
    # 将此处的 URL 替换为你网页的实际访问地址
    # 如果是本地文件，需要搭建一个简单的本地服务器（如 python -m http.server）
    TARGET_URL = "http://localhost:8000/index.html" 
    
    monitor = AIHunterMonitor(TARGET_URL)
    
    # 开始监控，建议设置合理的间隔（如 60 秒），避免给服务器造成负担
    monitor.start_monitoring(interval=30)
