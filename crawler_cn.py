# -*- coding: utf-8 -*-
"""
AI Hunter - 稳定版爬虫（混合自动+手动）
目标：确保网站始终展示丰富工具，不依赖不可靠的动态网站
"""

import json
import requests
import os
import datetime
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

def clean_text(text):
    if not text:
        return ""
    return ' '.join(str(text).split())

def fetch_ai_bot():
    """抓取 https://ai-bot.cn/ —— 可靠的中文源"""
    print("🇨🇳 抓取 ai-bot.cn...")
    tools = []
    try:
        res = requests.get("https://ai-bot.cn/", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        cards = soup.select('.url-card')[:20]
        for card in cards:
            title_elem = card.select_one('strong')
            desc_elem = card.select_one('.url-info p')
            link_elem = card.select_one('a')
            if title_elem and link_elem:
                title = clean_text(title_elem.get_text())
                desc = clean_text(desc_elem.get_text()) if desc_elem else "AI 工具"
                link = link_elem['href']
                if title and len(title) > 1:
                    tools.append({"title": title, "desc": desc, "source": link})
        print(f"✅ 抓取到 {len(tools)} 个中文工具")
    except Exception as e:
        print(f"⚠️ ai-bot.cn 抓取失败: {e}")
    return tools

def get_manual_global_tools():
    """手动维护的国外热门 AI 工具（确保显示）"""
    return [
        {"title": "Gamma.app", "desc": "用一句话生成 PPT、文档或网页，无需设计", "source": "https://gamma.app"},
        {"title": "Runway ML", "desc": "AI 视频编辑：文本生成视频、绿幕抠像、运动追踪", "source": "https://runwayml.com"},
        {"title": "HeyGen", "desc": "创建 AI 数字人视频，支持多语言口型同步", "source": "https://www.heygen.com"},
        {"title": "ElevenLabs", "desc": "超拟真 AI 语音合成，支持情感与多语种", "source": "https://elevenlabs.io"},
        {"title": "Notion AI", "desc": "智能笔记助手：总结、扩写、翻译、生成待办", "source": "https://www.notion.so/product/ai"},
        {"title": "Otter.ai", "desc": "实时语音转文字，自动生成会议摘要", "source": "https://otter.ai"},
        {"title": "Canva Magic Studio", "desc": "AI 设计套件：文生图、背景移除、文案生成", "source": "https://www.canva.com/magic-studio/"},
        {"title": "Perplexity AI", "desc": "会联网的答案引擎，替代传统搜索", "source": "https://www.perplexity.ai"},
        {"title": "Loom AI", "desc": "录制视频时自动生成摘要、章节和行动项", "source": "https://www.loom.com"},
        {"title": "Fireflies.ai", "desc": "自动记录并分析 Zoom/Teams 会议内容", "source": "https://fireflies.ai"}
    ]

def get_manual_cost_tools():
    """降本类工具（偏企业/客服/自动化）"""
    return [
        {"title": "Doubao (豆包)", "desc": "免费多模态 AI 助手，适合客服问答", "source": "https://www.doubao.com"},
        {"title": "WPS AI", "desc": "自动化办公流程，减少人力重复操作", "source": "https://www.wps.cn/ai"},
        {"title": "Tidbyt", "desc": "开源硬件看板，替代昂贵 SaaS 监控工具", "source": "https://tidbyt.com"},
        {"title": "Zapier", "desc": "连接不同 App 自动化工作流，节省开发成本", "source": "https://zapier.com"}
    ]

def get_trend_news():
    """抓取 36Kr 快讯（带 AI 关键词过滤）"""
    try:
        res = requests.get("https://36kr.com/newsflashes", headers=HEADERS, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        items = []
        for item in soup.select('div.newsflash-item')[:5]:
            title_elem = item.select_one('a.article-title')
            if not title_elem:
                continue
            title = clean_text(title_elem.get_text())
            if any(kw in title for kw in ['AI', '人工智能', '大模型', 'AIGC', '生成式']):
                link = "https://36kr.com" + title_elem['href'] if title_elem.has_attr('href') else "#"
                items.append({"title": "🔥 " + title, "desc": "来源：36Kr", "source": link})
        return items[:3] or [{"title": "全球 AI 应用加速落地", "desc": "企业需求激增", "source": "https://36kr.com"}]
    except Exception as e:
        print(f"⚠️ 趋势新闻抓取失败: {e}")
        return [{"title": "趋势加载中...", "desc": "请稍后刷新", "source": "#"}]

def deduplicate(tools):
    seen = set()
    unique = []
    for t in tools:
        key = t['title'].strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(t)
    return unique

def main():
    print("🚀 AI Hunter 稳定版启动...")

    # 1. 抓取国内工具
    auto_tools = fetch_ai_bot()

    # 2. 手动添加国外工具（确保数量）
    manual_efficiency = get_manual_global_tools()
    manual_cost = get_manual_cost_tools()

    # 3. 合并并去重
    all_efficiency = deduplicate(auto_tools + manual_efficiency)
    all_cost = deduplicate(manual_cost)

    # 4. 添加同步验证标记（用于确认 Action 是否生效）
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%m-%d %H:%M UTC")
    all_efficiency.insert(0, {
        "title": f"✅ 数据已更新 [{now_str}]",
        "desc": "GitHub Actions 自动同步成功",
        "source": "#"
    })

    # 5. 获取趋势
    trend = get_trend_news()

    # 6. 构建最终数据
    data = {
        "cost": all_cost,
        "efficiency": all_efficiency,
        "trend": trend
    }

    # 7. 写入文件
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 成功写入 data.json")
        print(f"   - 降本工具: {len(all_cost)} 个")
        print(f"   - 效率工具: {len(all_efficiency)} 个")
        print(f"   - 趋势新闻: {len(trend)} 条")
        print(f"   - 文件大小: {os.path.getsize('data.json')} 字节")
    except Exception as e:
        print(f"❌ 写入失败: {e}")
        exit(1)

if __name__ == "__main__":
    main()
