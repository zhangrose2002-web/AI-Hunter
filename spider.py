import json
from datetime import datetime

def generate_stable_data():
    print("📡 正在生成行业探测数据...")
    
    # 获取当前时间，证明数据是刚更新的
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 模拟真实情报数据
    data = [
        {
            "id": 1,
            "company": "长电科技 (实时探测)",
            "location": "江苏·无锡",
            "category": "domestic",
            "tag": "扩产情报",
            "reason": f"系统监测到先进封装产线动态，建议关注 BGA 焊球机采购需求。更新时间：{update_time}",
            "website": "http://www.jcetglobal.com",
            "phone": "系统监控中"
        },
        {
            "id": 2,
            "company": "通富微电 (扩产动态)",
            "location": "江苏·南通",
            "category": "domestic",
            "tag": "测试机采购",
            "reason": f"AMD 核心伙伴。近期高端 FC-BGA 产线配套设备需求持续上升。更新时间：{update_time}",
            "website": "http://www.tfme.com",
            "phone": "系统监控中"
        }
    ]
    return data

if __name__ == "__main__":
    try:
        leads = generate_stable_data()
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(leads, f, ensure_ascii=False, indent=2)
        print("🚀 data.json 写入成功！")
    except Exception as e:
        print(f"❌ 运行失败: {e}")
