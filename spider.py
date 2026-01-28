import os
import re
import json
import ftplib
from datetime import datetime

# ==========================================
# 1. 模拟抓取逻辑
# ==========================================
def fetch_industry_leads():
    print("开始执行全网线索搜寻...")
    # 这里是你的关键词抓取结果汇总
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
# 2. 更新本地 index.html
# ==========================================
def update_index_html(new_data):
    file_path = 'index.html'
    if not os.path.exists(file_path):
        print(f"❌ 错误: 找不到 {file_path} 文件")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配首页中的数据标记区
    pattern = r'/\* DATA_START \*/(.*?)/\* DATA_END \*/'
    js_data_str = f"\n    const leadsData = {json.dumps(new_data, ensure_ascii=False, indent=6)};\n    "
    
    new_content = re.sub(pattern, f"/* DATA_START */{js_data_str}/* DATA_END */", content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ 首页数据本地更新完成。")

# ==========================================
# 3. 传回阿里云虚拟空间 (核心处理)
# ==========================================
def upload_to_server():
    # 直接填入你的阿里云 FTP 信息
    FTP_SERVER = "qxu1590320302.my3w.com"
    FTP_USER = "qxu1590320302"
    FTP_PASS = "123456ab"

    try:
        print(f"正在连接 FTP: {FTP_SERVER} ...")
        session = ftplib.FTP()
        session.connect(FTP_SERVER, 21, timeout=30)
        session.login(FTP_USER, FTP_PASS)
        
        # 阿里云主机必须开启被动模式
        session.set_pasv(True)
        
        # 阿里云主机的网页根目录必须是 /htdocs
        session.cwd('/htdocs')
        
        # 定义需要同步的文件
        files_to_send = ['index.html', 'spider.html', 'live.html']
        
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

# 建议在 spider.py 的上传部分增加一层判断
try:
    session.login(FTP_USER, FTP_PASS)
    session.set_pasv(True)
    
    # 尝试进入目录，如果进不去说明已经在里面了
    try:
        session.cwd('/htdocs')
    except:
        print("已经在根目录或 htdocs 无法访问")
        
    # 执行上传...

# ==========================================
# 4. 统一执行入口
# ==========================================
if __name__ == "__main__":
    # 第一步：模拟或实际爬取数据
    leads = fetch_industry_leads()
    
    # 第二步：将数据写入本地 HTML 模板
    update_index_html(leads)
    
    # 第三步：将更新后的 HTML 推送到阿里云空间
    upload_to_server()

