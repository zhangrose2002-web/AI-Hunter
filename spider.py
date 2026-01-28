import os
import json
import ftplib
import time
import random  # 确保这个在这里
import urllib.parse
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_industry_leads():
    # --- 核心关键词库 ---
    # 包含单词监控和组合逻辑监控
    raw_keywords = [
        "800G光模块", "EML激光器", "高速光收发", "CPO技术", "产线扩能", 
        "车规级认证", "IGBT模块", "SiC功率器件", "新增产线招标", "OBC封装", 
        "石英晶体振荡器", "KDS/精工替代", "SMD封装", "频率元件", "产能翻倍", 
        "微波组件", "厚膜电路", "金属管壳封装", "国产化替代", "自主可控", 
        "MEMS传感器", "红外探测器", "真空封装", "小批量试产", "工艺研发", 
        "先进封装", "气密性测试", "系统级封装(SiP)", "先进封测项目公示", 
        "TO-CAN封装", "激光雷达", "光电探测器", "二极管封装", "扩建厂房",
        "产能翻倍 TO-CAN封装", "产线扩能 IGBT模块封装", 
        "增产 光收发组件(TOSA)", "自主可控 气密性封装设备", 
        "国产替代 真空平行缝焊机", "核心装备 微波组件封装", 
        "小批量试产 SiC功率模块", "工艺研发 MEMS真空封装", 
        "打样 激光封焊工艺"
    ]

    print(f"🚀 引擎启动：正在对 {len(raw_keywords)} 组核心关键词进行深度线索探测...")
    real_leads = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    # 为了避免被搜索引擎封禁，我们随机抽取 15组关键词进行单次轮询
    import random
    selected_kws = random.sample(raw_keywords, min(15, len(raw_keywords)))

    for kw in selected_kws:
        # 处理组合搜索逻辑：把 "A" + "B" 转换为搜索引擎识别的 A B
        search_query = kw.replace('"', '').replace('+', ' ')
        encoded_query = urllib.parse.quote(search_query)
        
        # 使用 Bing 搜索进行全网探测
        url = f"https://www.bing.com/search?q={encoded_query}"
        
        try:
            time.sleep(1) # 避开频率限制
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 解析搜索结果
            items = soup.find_all('li', class_='b_algo', limit=2) # 每个词取前2条最相关的
            for i, item in enumerate(items):
                title_elem = item.find('h2')
                snippet_elem = item.find('p')
                link_elem = item.find('a')

                if title_elem and link_elem:
                    real_leads.append({
                        "id": int(datetime.now().timestamp()) + random.randint(1, 1000),
                        "company": title_elem.text[:25], # 截取标题前段作为参考机构
                        "location": "全网探测",
                        "category": "domestic" if "替代" in kw or "国产" in kw else "intl",
                        "tag": kw.replace('"', '').split('+')[0].strip(), # 提取第一个关键词做标签
                        "reason": snippet_elem.text[:100] if snippet_elem else "点击链接查看详细招标/扩产详情...",
                        "website": link_elem['href'],
                        "phone": "见详情页公示"
                    })
            print(f"✅ 关键词 [{kw}] 探测完成")
        except Exception as e:
            print(f"⚠️ 关键词 [{kw}] 抓取异常: {e}")

    if not real_leads:
        print("⚠️ 本次未探测到实时动态，启用行业常态线索...")
        real_leads = [
            {
                "id": 999,
                "company": "行业动态监控中",
                "location": "全国",
                "category": "domestic",
                "tag": "系统提示",
                "reason": "当前实时搜索未发现新公告，正在扩大范围监控 45 组核心关键词...",
                "website": "#",
                "phone": "-"
            }
        ]

    return real_leads

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





