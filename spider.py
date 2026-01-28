import os
import json
import ftplib
from datetime import datetime

# ==========================================
# 1. 模拟抓取逻辑 (保持并优化)
# ==========================================
def fetch_industry_leads():
    print("开始执行全网线索搜寻...")
    # 模拟抓取结果，确保字段名与前端 index.html 渲染逻辑完全一致
    new_leads = [
        {
            "id": int(datetime.now().timestamp()),
            "company": "某头部功率半导体厂",
            "location": "广东·深圳",
            "category": "domestic",
            "reason": "新增 [SiC功率器件] 封装产线招标，急需 [真空平行缝焊机] 及气密性检测设备。",
            "website": "cs.bj77.cn",
            "phone": "见官网公告",
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

# ==========================================
# 2. 生成 JSON 数据文件 (核心改变：不再改写 HTML)
# ==========================================
def save_to_json(data):
    file_path = 'data.json'
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            # indent=2 让文件有缩进，方便人工查看
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 数据已写入本地 {file_path}")
    except Exception as e:
        print(f"❌ 写入 JSON 失败: {e}")

# ==========================================
# 3. 传回阿里云虚拟空间
# ==========================================
def upload_to_server():
    # FTP 信息保持不变
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
        
        # 【关键】增加 data.json 到同步列表
        # 既然 index.html 现在是动态加载，我们其实只需要传 data.json 即可
        # 但如果是第一次部署，还是建议把 HTML 也传上去
        files_to_send = ['index.html', 'spider.html', 'data.json']
        
        for file_name in files_to_send:
            if os.path.exists(file_name):
                with open(file_name, 'rb') as f:
                    session.storbinary(f'STOR {file_name}', f)
                    print(f"🚀 已成功同步到空间: {file_name}")
            else:
                print(f"⚠️ 跳过: 本地未找到 {file_name}")

        session.quit()
        print(f"✨ 实时同步完成！访问地址: http://cs.bj77.cn/")
        
    except Exception as e:
        print(f"❌ 传输失败: {e}")

# ==========================================
# 4. 统一执行入口
# ==========================================
if __name__ == "__main__":
    # 第一步：获取数据
    leads = fetch_industry_leads()
    
    # 第二步：保存为 data.json (首页会通过 fetch 读取这个文件)
    save_to_json(leads)
    
    # 第三步：将更新后的文件推送到阿里云
    upload_to_server()
