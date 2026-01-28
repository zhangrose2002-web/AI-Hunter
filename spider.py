import os
import json
import ftplib
from datetime import datetime

# ==========================================
# 1. 模拟抓取逻辑 (字段名已修正，确保与 index.html 匹配)
# ==========================================
def fetch_industry_leads():
    print("开始执行全网线索搜寻...")
    # 模拟抓取结果
    # 注意：这里的键名必须与 index.html 中 item.xxx 的后缀完全一致
    new_leads = [
        {
            "id": 1001,
            "company": "长电科技（绍兴）有限公司", # 【修正】org_name -> company
            "location": "浙江·绍兴",            # 【修正】region -> location
            "category": "domestic",
            "tag": "FC-BGA扩产",
            "reason": "推荐理由：国家集成电路产业基金增持。应用领域：高端 FC-BGA 封装线扩产，急需固晶机与焊线机设备。", # 【修正】reason_field -> reason
            "website": "http://www.jcetglobal.com",
            "phone": "0575-88886666"
        },
        {
            "id": 1002,
            "company": "通富微电总部",
            "location": "江苏·南通",
            "category": "domestic",
            "tag": "先进封装",
            "reason": "推荐理由：AMD 核心封测伙伴。应用领域：7nm/5nm 先进封装扩产，正进行大规模设备招标。",
            "website": "http://www.tfme.com",
            "phone": "0513-85055555"
        },
        {
            "id": 1003,
            "company": "华天科技（昆山）",
            "location": "江苏·昆山",
            "category": "domestic",
            "tag": "TSV技术",
            "reason": "推荐理由：TSV 封装技术领先。应用领域：CIS 图像传感器封装，产线技术升级改造中。",
            "website": "http://www.ht-tech.com",
            "phone": "0512-57351111"
        }
    ]
    return new_leads

# ==========================================
# 2. 生成 JSON 数据文件 (保持不变)
# ==========================================
def save_to_json(data):
    file_path = 'data.json'
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 数据已成功写入本地 {file_path}")
    except Exception as e:
        print(f"❌ 写入 JSON 失败: {e}")

# ==========================================
# 3. 传回阿里云虚拟空间 (保持不变)
# ==========================================
def upload_to_server():
    FTP_SERVER = "qxu1590320302.my3w.com"
    FTP_USER = "qxu1590320302"
    FTP_PASS = "123456ab"

    try:
        print(f"正在连接 FTP: {FTP_SERVER} ...")
        session = ftplib.FTP()
        session.connect(FTP_SERVER, 21, timeout=30)
        session.login(FTP_USER, FTP_PASS)
        session.set_pasv(True)
        
        try:
            session.cwd('/htdocs')
        except:
            print("已经在根目录或 htdocs 无法访问")
        
        # 确保同步最新的三个核心文件
        files_to_send = ['index.html', 'spider.html', 'data.json']
        
        for file_name in files_to_send:
            if os.path.exists(file_name):
                with open(file_name, 'rb') as f:
                    session.storbinary(f'STOR {file_name}', f)
                    print(f"🚀 已成功同步到空间: {file_name}")
            else:
                print(f"⚠️ 跳过: 本地未找到 {file_name}")

        session.quit()
        print(f"✨ 实时同步完成！")
        
    except Exception as e:
        print(f"❌ 传输失败: {e}")

# ==========================================
# 4. 统一执行入口
# ==========================================
if __name__ == "__main__":
    leads = fetch_industry_leads()
    save_to_json(leads)
    upload_to_server()
