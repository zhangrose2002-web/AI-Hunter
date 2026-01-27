import requests
import re
import json
import time
from datetime import datetime

class IndustryLeadSpider:
    def __init__(self, url):
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0 SalesHunter/1.0'}
        # 定义销售关键词权重
        self.sales_keywords = {
            "parallel_seam": ["平行缝焊机", "金属管壳", "气密性", "真空封装", "微波组件", "厚膜电路"],
            "cap_sealer": ["封帽机", "TO-CAN", "TOSA", "ROSA", "晶振", "储能焊"],
            "laser_welder": ["激光封焊", "激光打样", "OBC封装", "激光雷达", "动力电池封装"]
        }

    def fetch_and_parse(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 正在扫描目标网页线索...")
        try:
            # 在实际运行中，如果是本地文件，可以使用 open().read()
            # 这里演示从 URL 获取
            response = requests.get(self.url, headers=self.headers, timeout=5)
            html_content = response.text
            
            # 使用正则提取网页内的 leadsData 数组
            data_match = re.search(r'const leadsData = (\[.*?\]);', html_content, re.DOTALL)
            if not data_match:
                print("未找到 leadsData 数据源")
                return []

            raw_leads = json.loads(data_match.group(1))
            return self.analyze_leads(raw_leads)
        except Exception as e:
            print(f"读取失败: {e}")
            return []

    def analyze_leads(self, leads):
        analyzed_results = []
        for lead in leads:
            score = 0
            reason = lead.get('reason', '')
            
            # 1. 识别产品线关联
            target_machines = []
            for machine, keys in self.sales_keywords.items():
                if any(k in reason for k in keys):
                    target_machines.append(machine)
                    score += 20
            
            # 2. 识别“扩产”或“招标”动作（高价值商机）
            if any(k in reason for k in ["产线扩能", "新增产线", "招标", "投产", "翻倍", "小批量试产"]):
                score += 50
                lead['is_priority'] = True
            
            if score >= 20:
                lead['analysis_score'] = score
                lead['target_machines'] = target_machines
                analyzed_results.append(lead)
        
        return analyzed_results

    def push_to_ui_mock(self, lead):
        """
        模拟将爬取到的新商机推送到网页前端
        """
        print(f"!!! 发现高价值线索 !!!")
        print(f"公司: {lead['company']}")
        print(f"建议推销设备: {lead.get('target_machines')}")
        print(f"联系电话: {lead['phone']}")
        print("-" * 30)

    def run_forever(self):
        print("AI 销售情报爬虫已启动，正在监控封测设备商机...")
        while True:
            leads = self.fetch_and_parse()
            for lead in leads:
                if lead.get('is_priority'):
                    self.push_to_ui_mock(lead)
            
            time.sleep(60) # 每分钟扫描一次

if __name__ == "__main__":
    # 实际使用时将 path 替换为 index.html 的访问路径
    spider = IndustryLeadSpider("http://localhost:8000/index.html")
    # spider.run_forever() # 启动循环
    
    # 单次运行演示
    found = spider.fetch_and_parse()
    print(f"本轮共发现 {len(found)} 条高度相关的封装设备商机。")
