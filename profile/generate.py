# coding=utf-8
"""
Generate profile README files (Markdown) and Website (HTML).
Reads from content.json (projects) and static.json (static text).
"""

import json
import re
from urllib.parse import quote

# --- 全局配置 ---
DEFAULT_STARS = True  # 默认是否显示 GitHub Stars


# ----------------------------
# 1. 辅助函数
# ----------------------------
def qs(s, safe=""):
    """URL 编码，将 - 替换为 %20"""
    out = quote(s, safe=safe)
    return out.replace("-", "%20")


# ----------------------------
# 2. Badge 类定义 (用于 Markdown)
# ----------------------------
class Badge(object):
    def __init__(self, id, label, badge_url, url):
        self.id, self.label, self.badge_url, self.url = id, label, badge_url, url

    def to_markdown(self) -> str:
        return f"[![{self.label}]({self.badge_url})]({self.url})"


class Project(Badge):
    def __init__(self, id, url):
        super().__init__(
            id,
            "Project",
            f"https://img.shields.io/badge/🌐%20%20Project-{qs(id)}-blue.svg",
            url,
        )


class ArXiv(Badge):
    def __init__(self, id):
        super().__init__(
            id,
            "arXiv",
            f"https://img.shields.io/badge/Arxiv-{id}-b31b1b.svg?logo=arXiv",
            f"https://arxiv.org/abs/{id}",
        )


class Publish(Badge):
    def __init__(self, id, url, publisher="conference"):
        prefix = "🏛  Conference"
        if publisher.lower() == "journal":
            prefix = "📗  Journal"
        elif publisher.lower() == "report":
            prefix = "📖  Report"
        super().__init__(
            id,
            "Conference",
            f"https://img.shields.io/badge/{qs(prefix)}-{qs(id)}-green.svg",
            url,
        )


class GitHub(Badge):
    def __init__(self, repo, id="Code", stars=None, not_finished=False):
        label = "GitHub"
        if not_finished:
            id = "Code (Comming Soon)"
        self.stars = stars if stars is not None else DEFAULT_STARS
        self.stars = self.stars and not not_finished
        super().__init__(
            id,
            label,
            f"https://img.shields.io/badge/{qs(id)}-{label}-181717.svg?logo=GitHub",
            f"https://github.com/{repo}",
        )
        self.repo = repo

    def to_markdown(self) -> str:
        base = super().to_markdown()
        return base + (
            f"\n![GitHub Stars](https://img.shields.io/github/stars/{self.repo})"
            if self.stars
            else ""
        )


class HuggingFace(Badge):
    def __init__(self, repo, id="HuggingFace", model=False, space=False, dataset=False):
        super().__init__(id, "HuggingFace", None, None)
        self.repo, self.model, self.space, self.dataset = repo, model, space, dataset

    def to_markdown(self) -> str:
        items = []
        if self.model:
            items.append(
                f"[![HuggingFace Model](https://img.shields.io/badge/🤗-HuggingFace-FFD21E.svg)](https://huggingface.co/{self.repo})"
            )
        if self.space:
            items.append(
                f"[![HuggingFace Space](https://img.shields.io/badge/🤗-HuggingFace%20Space-FFD21E.svg)](https://huggingface.co/spaces/{self.repo})"
            )
        if self.dataset:
            items.append(
                f"[![HuggingFace Dataset](https://img.shields.io/badge/🤗-HuggingFace%20Dataset-FFD21E.svg)](https://huggingface.co/datasets/{self.repo})"
            )
        return "\n".join(items) if items else ""


class ModelScope(Badge):
    def __init__(self, repo, id="ModelScope", model=True, studio=False, dataset=False):
        super().__init__(id, "ModelScope", None, None)
        self.repo, self.model, self.studio, self.dataset = repo, model, studio, dataset

    def to_markdown(self) -> str:
        items = []
        if self.model:
            items.append(
                f"[![ModelScope](https://img.shields.io/badge/👾-ModelScope-604DF4.svg)](https://modelscope.cn/models/{self.repo})"
            )
        if self.studio:
            items.append(
                f"[![ModelScope Studio](https://img.shields.io/badge/👾-ModelScope%20Studio-604DF4.svg)](https://modelscope.cn/studios/{self.repo})"
            )
        if self.dataset:
            items.append(
                f"[![ModelScope Dataset](https://img.shields.io/badge/👾-ModelScope%20Dataset-604DF4.svg)](https://modelscope.cn/datasets/{self.repo})"
            )
        return "\n".join(items) if items else ""


def create_badge(badge_type: str, **kwargs) -> Badge:
    badge_type = badge_type.lower()
    mapping = {
        "project": Project,
        "arxiv": ArXiv,
        "publish": Publish,
        "github": GitHub,
        "huggingface": HuggingFace,
        "modelscope": ModelScope,
    }
    return mapping[badge_type](**kwargs) if badge_type in mapping else None


# ----------------------------
# 3. HTML Badge 生成器
# ----------------------------
def create_html_badge(badge_type, data):
    url, icon, label = "", "", ""
    badge_type = badge_type.lower()

    if badge_type == "project":
        url, label, icon = data.get("url", "#"), "Project", "fas fa-globe"
    elif badge_type == "arxiv":
        url, label, icon = (
            f"https://arxiv.org/abs/{data.get('id', '')}",
            "arXiv",
            "fas fa-file-pdf",
        )
    elif badge_type == "publish":
        url, label, icon = (
            data.get("url", "#"),
            data.get("id", "Conference"),
            "fas fa-landmark",
        )
    elif badge_type == "huggingface":
        repo = data.get("repo", "")
        if data.get("model", False):
            url = f"https://huggingface.co/{repo}"
            label = "HuggingFace"
            icon = "fas fa-face-smile"
        elif data.get("space", False):
            url = f"https://huggingface.co/spaces/{repo}"
            label = "HuggingFace Space"
            icon = "fas fa-face-smile"
        elif data.get("dataset", False):
            url = f"https://huggingface.co/datasets/{repo}"
            label = "HuggingFace Dataset"
            icon = "fas fa-face-smile"
        else:
            return ""  # 如果没有指定类型，不生成
    elif badge_type == "modelscope":
        repo = data.get("repo", "")
        if data.get("model", False):
            url = f"https://modelscope.cn/models/{repo}"
            label = "ModelScope"
            icon = "fas fa-cube"
        elif data.get("studio", False):
            url = f"https://modelscope.cn/studios/{repo}"
            label = "ModelScope Studio"
            icon = "fas fa-cube"
        elif data.get("dataset", False):
            url = f"https://modelscope.cn/datasets/{repo}"
            label = "ModelScope Dataset"
            icon = "fas fa-cube"
        else:
            return ""  # 如果没有指定类型，不生成

    # --- GitHub 特殊处理 ---
    elif badge_type == "github":
        repo = data.get("repo", "")
        url = f"https://github.com/{repo}"
        label = "Code"

        not_finished = data.get("not_finished", False)
        if not_finished:
            label = "Coming Soon"

        show_stars = data.get("stars", DEFAULT_STARS)
        # data-github-repo 属性是 JS 查找的关键
        data_attr = (
            f'data-github-repo="{repo}"' if (show_stars and not not_finished) else ""
        )

        # 结构：<a ... data-github-repo="xxx"> <i...> Code <span class="star-suffix" style="display:none"> ( <span class="star-count"></span> <i...> ) </span> </a>
        html = (
            f'<a href="{url}" target="_blank" class="badge badge-github" {data_attr}>'
        )
        html += f'<i class="fab fa-github"></i> {label}'

        if show_stars and not not_finished:
            html += '<span class="star-suffix" style="display:none"> (<span class="star-count"></span> <i class="fas fa-star"></i>)</span>'

        html += "</a>"
        return html

    else:
        return ""

    return f'<a href="{url}" target="_blank" class="badge badge-{badge_type}"><i class="{icon}"></i> {label}</a>'


# ----------------------------
# 4. 生成器逻辑
# ----------------------------
def generate():
    # Load Data
    with open("profile/content.json", "r", encoding="utf-8") as f:
        projects = json.load(f)
    with open("profile/static.json", "r", encoding="utf-8") as f:
        static = json.load(f)

    langs = [("en", "index.html", "index.zh.html"),
             ("zh", "index.zh.html", "index.html")]

    # --- HTML 模板 ---
    TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {subtitle}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Space+Grotesk:wght@300;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="ambient-light one"></div>
    <div class="ambient-light two"></div>
    <div class="grid-overlay"></div>

    <nav>
        <div class="logo">{title}</div>
        <div class="nav-links">
            <a href="#overview">{nav_home}</a>
            <a href="https://github.com/Fantasy-AMAP/">{nav_projects}</a>
            <a href="#news">{nav_news}</a>
            <a href="{lang_link}" class="lang-btn">{lang_btn}</a>
        </div>
    </nav>

    <header class="hero">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </header>

    <main class="container">
        <!-- overview Section -->
        <section id="overview" class="overview">
            <h2 class="section-title"><i class="fas fa-lightbulb"></i> {philo_title}</h2>
            <div class="text-content">
                {philo_content}
            </div>
        </section>
        
        <!-- News Section -->
        <section id="news" class="news-section">
            <h2 class="section-title"><i class="fas fa-bolt"></i> {news_title}</h2>
            <div class="news-list">
                {news_html}
            </div>
        </section>

        <!-- Projects Section -->
        <section id="projects">
            {projects_html}
        </section>
    </main>

    <footer>
        <p>{footer}</p>
    </footer>
    <script src="script.js"></script>
</body>
</html>"""

    for lang, filename, target_link in langs:
        s = static[lang]

        # 1. Generate Projects HTML
        projects_html = ""
        badge_order = ["publish", "project", "arxiv", "github", "huggingface", "modelscope"]

        for p in projects:
            desc = p["intro_zh"] if lang == "zh" else p["intro"]
            
            # Generate badges HTML
            badges_html = ""
            for b_type in badge_order:
                if b_type in p:
                    # Special handling for HuggingFace and ModelScope (multiple badges possible)
                    if b_type == "huggingface":
                        hf_data = p[b_type]
                        if hf_data.get("model", False):
                            badge_html = create_html_badge(b_type, {"repo": hf_data["repo"], "model": True})
                            if badge_html:
                                badges_html += badge_html + " "
                        if hf_data.get("space", False):
                            badge_html = create_html_badge(b_type, {"repo": hf_data["repo"], "space": True})
                            if badge_html:
                                badges_html += badge_html + " "
                        if hf_data.get("dataset", False):
                            badge_html = create_html_badge(b_type, {"repo": hf_data["repo"], "dataset": True})
                            if badge_html:
                                badges_html += badge_html + " "
                    elif b_type == "modelscope":
                        ms_data = p[b_type]
                        if ms_data.get("model", False):
                            badge_html = create_html_badge(b_type, {"repo": ms_data["repo"], "model": True})
                            if badge_html:
                                badges_html += badge_html + " "
                        if ms_data.get("studio", False):
                            badge_html = create_html_badge(b_type, {"repo": ms_data["repo"], "studio": True})
                            if badge_html:
                                badges_html += badge_html + " "
                        if ms_data.get("dataset", False):
                            badge_html = create_html_badge(b_type, {"repo": ms_data["repo"], "dataset": True})
                            if badge_html:
                                badges_html += badge_html + " "
                    else:
                        badge_html = create_html_badge(b_type, p[b_type])
                        if badge_html:
                            badges_html += badge_html + " "

            # Video Embed
            video_html = ""
            if "video_url" in p and p["video_url"]:
                video_url = p["video_url"]
                # 判断是否是 YouTube 视频
                is_youtube = "youtube.com/embed" in video_url or "youtu.be" in video_url
                
                if is_youtube:
                    # YouTube 视频使用标准 iframe 格式
                    # 从 URL 中提取视频 ID（如果还没有 embed 格式，需要转换）
                    if "youtube.com/embed/" in video_url:
                        video_id = video_url.split("youtube.com/embed/")[1].split("?")[0]
                    elif "youtu.be/" in video_url:
                        video_id = video_url.split("youtu.be/")[1].split("?")[0]
                    else:
                        video_id = video_url
                    
                    embed_url = f"https://www.youtube.com/embed/{video_id}"
                    video_title = p.get("title", "Video")
                    
                    video_html = f"""
                <div class="video-container">
                    <iframe width="922" height="519" src="{embed_url}" title="{video_title}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
                </div>
                """
                else:
                    # 非 YouTube 视频（如 MP4）使用 video 标签
                    video_html = f"""
                <div class="video-container">
                    <video controls style="width: 100%; height: 100%;">
                        <source src="{video_url}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>
                """
            else:
                # Placeholder if no video
                video_html = f"""
                <div class="video-container">
                    <span class="video-placeholder-text">VIDEO PREVIEW: {p['title']}</span>
                </div>
                """

            projects_html += f"""
            <article class="project-card">
                {video_html}
                <div class="card-content">
                    <div class="project-header">
                        <div class="project-title">{p['title']}</div>
                        <div class="project-badges">{badges_html}</div>
                    </div>
                    <div class="project-desc">{desc}</div>
                </div>
            </article>
            """

        # 2. Generate News HTML
        news_html = ""
        for item in s["news"]["items"]:
            news_html += f'<div class="news-item"><div class="news-text">{item}</div></div>'

        # 3. Fill Template
        html = TEMPLATE.format(
            lang=lang,
            title=s["title"],
            subtitle=s["subtitle"],
            nav_home=s["nav"]["home"],
            nav_projects=s["nav"]["projects"],
            nav_news=s["nav"]["news"],
            lang_btn=s["nav"]["lang_btn"],
            lang_link=target_link,
            philo_title=s["overview"]["title"],
            philo_content=s["overview"]["content"],
            projects_html=projects_html,
            news_title=s["news"]["title"],
            news_html=news_html,
            footer=s["footer"]
        )

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ Generated {filename}", flush=True)

    # 4. Generate README.md
    readme_content = f"""# Fantasy AIGC Family

Fantasy AIGC Family is an open-source initiative exploring Human-centric AI, World Modeling, and Human-World Interaction, aiming to bridge perception, understanding, and generation in the real and digital worlds.

## 🔥🔥🔥 News!!
"""
    # Add news items from static.json (English version)
    news_items = static["en"]["news"]["items"]
    for item in news_items:
        # Convert HTML links to Markdown format
        item_md = item
        item_md = re.sub(r"<a href='([^']+)'><strong>([^<]+)</strong></a>", r'[\2](\1)', item_md)
        item_md = re.sub(r"<a href='([^']+)'>([^<]+)</a>", r'[\2](\1)', item_md)
        item_md = re.sub(r'<strong>([^<]+)</strong>', r'**\1**', item_md)
        item_md = re.sub(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', r'[\2](\1)', item_md)
        readme_content += f"* {item_md}\n"

    readme_content += "\n## ✨✨✨ Members\n\n"

    # Add projects from content.json
    badge_order = ["publish", "project", "arxiv", "github", "huggingface", "modelscope"]
    
    for p in projects:
        title = p["title"]
        intro = p["intro"]
        
        readme_content += f"### {title}\n\n"
        
        # Add badges
        for b_type in badge_order:
            if b_type in p:
                badge_obj = create_badge(b_type, **p[b_type])
                if badge_obj:
                    badge_md = badge_obj.to_markdown()
                    if badge_md:
                        readme_content += badge_md + "\n"
        
        # Add description
        readme_content += f"\n{intro}\n"
        readme_content += "<br><br>\n\n"

    readme_content += """## 🌟🌟🌟 Our wishes.
1. **Giving Back to the Community**: In our daily work, we benefit immensely from the resources, expertise, and support of the open source community, and we aim to give back by making our own projects open source.
2. **Attracting More Contributors**: By open sourcing our code, we invite developers worldwide to collaborate—making our models smarter, our engineering more robust, and extending benefits to even more users.
3. **Building an Open Ecosystem**: We believe that open source brings together diverse expertise to create a collaborative innovation platform—driving technological progress, industry growth, and broader societal impact.
"""

    with open("profile/README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"✅ Generated profile/README.md", flush=True)


if __name__ == "__main__":
    generate()
