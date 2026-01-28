import os
import json
import ftplib
from datetime import datetime

# ==========================================
# 1. 模拟抓取逻辑 (字段名已修正，确保与 index.html 匹配)
# ==========================================
import requests
from bs4 import BeautifulSoup

def fetch_industry_leads():
    print("🚀 正在启动真实爬虫引擎，扫描行业公开情报...")
    real_leads = []
    
    # 示例：抓取某个行业公告页（这里填入你关注的招标网或新闻地址）
    target_url = "https://www.example-bidding.com/search?q=封焊机" 
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(target_url, timeout=10, headers=headers)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 假设网页上的每一条公告都在 <div class="news-item"> 里
            # 这部分需要根据你目标网站的 HTML 结构具体调整
            items = soup.find_all('div', class_='news-item') 
            
            for i, item in enumerate(items[:5]): # 只取前5条最新线索
                real_leads.append({
                    "id": int(datetime.now().timestamp()) + i,
                    "company": item.find('span', class_='company').text.strip(),
                    "location": "情报解析中",
                    "category": "domestic",
                    "tag": "实时招标",
                    "reason": item.find('a').text.strip(), # 抓取标题作为理由
                    "website": target_url,
                    "phone": "见原公告"
                })
        
        if not real_leads:
            print("⚠️ 未能从目标网页解析到数据，请检查选择器结构。")
            
    except Exception as e:
        print(f"❌ 真实抓取失败: {e}")
        
    return real_leads if real_leads else fetch_mock_data() # 如果抓不到就回退到模拟数据

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

