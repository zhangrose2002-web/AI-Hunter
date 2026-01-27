import requests
import re
import json
import time
import hashlib
from datetime import datetime

class SalesHunterMonitor:
    def __init__(self, target_url):
        self.target_url = target_url
        self.last_data_hash = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # 核心销售关键词库
        self.market_intelligence = {
            # 1. 核心设备关联词 (直接关联产品)
            "device_links": {
                "平行缝焊机": ["金属管壳", "气密性", "真空封装", "SMD封装", "厚膜电路", "微波组件", "系统级封装", "SiP"],
                "激光封焊机": ["激光封焊", "激光焊接", "激光雷达", "光电探测器", "二极管封装", "OBC封装"],
                "封帽机/储能焊": ["TO-CAN", "TOSA", "ROSA", "晶振", "石英晶体", "石英振荡器"]
            },
            
            # 2. 行业高热度领域 (寻找潜在线索)
            "hot_sectors": [
                "800G光模块", "EML激光器", "高速光收发", "CPO技术", 
                "车规级认证", "IGBT模块", "SiC功率器件", "MEMS传感器", "红外探测器"
            ],
            
            # 3. 销售触发动作 (判断是否有钱买设备)
            "trigger_actions": ["产线扩能", "新增产线招标", "产能翻倍", "扩建厂房", "小批量试产", "工艺研发", "打样", "国产化替代", "自主可控"],
            
            # 4. 深度逻辑组合 (命中即为高优商机)
            "priority_combos": [
                (r"产能翻倍", r"TO-CAN封装"),
                (r"产线扩能", r"IGBT模块封装"),
                (r"增产", r"光收发组件\(TOSA\)"),
                (r"自主可控", r"气密性封装设备"),
                (r"国产替代", r"真空平行缝焊机"),
                (r"核心装备", r"微波组件封装"),
                (r"小批量试产", r"SiC功率模块"),
                (r"工艺研发", r"MEMS真空封装"),
                (r"打样", r"激光封焊工艺")
            ]
        }

    def get_data_hash(self, data_str):
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()

    def analyze_sales_opportunity(self, lead):
        """
        销售商机分析引擎
        """
        # 聚合所有文本内容用于检索
        content = f"{lead.get('company', '')} {lead.get('tag', '')} {lead.get('reason', '')} {lead.get('location', '')}".upper()
        
        matched_devices = []
        scores = 0
        match_details = []

        # 检查设备关联
        for device, keywords in self.market_intelligence["device_links"].items():
            for kw in keywords:
                if kw.upper() in content:
                    matched_devices.append(device)
                    match_details.append(f"设备相关: {kw}")
                    scores += 10
                    break

        # 检查触发动作 (加分项)
        for act in self.market_intelligence["trigger_actions"]:
            if act.upper() in content:
                match_details.append(f"触发动作: {act}")
                scores += 20

        # 检查高优组合 (核心得分点)
        for p1, p2 in self.market_intelligence["priority_combos"]:
            if re.search(p1.upper(), content) and re.search(p2.upper(), content):
                match_details.append(f"高优商机组合: {p1} + {p2}")
                scores += 50
                lead['is_hot'] = True

        # 检查热门领域
        for sector in self.market_intelligence["hot_sectors"]:
            if sector.upper() in content:
                match_details.append(f"目标领域: {sector}")
                scores += 15

        return {
            "is_opportunity": scores > 15,
            "score": scores,
            "matched_devices": list(set(matched_devices)),
            "reasons": match_details
        }

    def fetch_data(self):
        try:
            response = requests.get(self.target_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            html = response.text
            match = re.search(r'const leadsData = (\[.*?\]);', html, re.DOTALL)
            if not match: return None
            
            json_str = match.group(1)
            current_hash = self.get_data_hash(json_str)
            if current_hash == self.last_data_hash: return None
            
            self.last_data_hash = current_hash
            return json.loads(json_str)
        except Exception as e:
            print(f"数据获取失败: {e}")
            return None

    def process_and_push(self, leads):
        print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 正在扫描新一批线索...")
        
        found_any = False
        for lead in leads:
            result = self.analyze_sales_opportunity(lead)
            
            if result["is_opportunity"]:
                found_any = True
                print(f"\n🔥 发现高价值销售商机！")
                print(f"【公司】: {lead['company']}")
                print(f"【推荐设备】: {' / '.join(result['matched_devices']) if result['matched_devices'] else '封装相关设备'}")
                print(f"【信心指数】: {result['score']} 分")
                print(f"【匹配详情】: {', '.join(result['reasons'])}")
                print(f"【联络信息】: {lead['phone']} | {lead['website']}")
                print("-" * 50)
                
                # 此处可扩展发送至网页端、企业微信、或数据库
                # requests.post("http://your-backend.com/api/push", json={...})

        if not found_any:
            print("本轮更新未发现匹配的销售线索。")

    def run(self, interval=30):
        print("="*60)
        print("AI 猎人 - 封装设备销售情报系统 启动")
        print(f"当前监控: 封帽机 / 平行缝焊机 / 激光封焊机 场景")
        print("="*60)
        while True:
            leads = self.fetch_data()
            if leads:
                self.process_and_push(leads)
            time.sleep(interval)

if __name__ == "__main__":
    # 使用本地模拟地址，实际请替换为你的数据源 URL
    TARGET_URL = "http://localhost:8000/index.html" 
    monitor = SalesHunterMonitor(TARGET_URL)
    monitor.run(interval=20)
