"""话术生成器 - 根据JD匹配结果生成各场景话术"""

import os

from experience_manager import _load_db
from jd_matcher import match_experiences

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")


def _load_template(name):
    """加载模板文件"""
    path = os.path.join(TEMPLATE_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _get_basic_info():
    """获取基本信息"""
    db = _load_db()
    return db.get("basic_info", {})


def _format_experience_brief(exp, max_achievements=1):
    """简短格式化一条经历"""
    parts = [exp["title"]]
    for a in exp.get("achievements", [])[:max_achievements]:
        parts.append(a)
    return "，".join(parts)


def _format_experience_detail(exp):
    """详细格式化一条经历"""
    lines = [f"· {exp['title']}"]
    if exp.get("description"):
        lines.append(f"  {exp['description']}")
    for a in exp.get("achievements", []):
        lines.append(f"  - {a}")
    return "\n".join(lines)


def generate_boss_greeting(jd_text, position="该", company="贵司"):
    """生成Boss直聘打招呼话术"""
    info = _get_basic_info()
    matches, jd_info = match_experiences(jd_text, top_n=2)

    # 构建经历亮点（Boss直聘字数有限，要简短）
    experience_highlight = ""
    if matches:
        top = matches[0]["experience"]
        if top.get("type") == "internship":
            experience_highlight = f"曾在{top['title'].split(' - ')[0]}实习，"
        elif top.get("achievements"):
            experience_highlight = f"曾{top['achievements'][0]}，"

    # 构建匹配原因
    match_reason = ""
    if jd_info["keywords"]:
        kw_list = list(jd_info["keywords"])[:3]
        match_reason = f"我在{'、'.join(kw_list)}方面有相关经验。"

    template = _load_template("boss_greeting.txt")
    message = template.format(
        name=info.get("name", "XX"),
        university=info.get("university", "XX大学"),
        major=info.get("major", "XX专业"),
        graduation_year=info.get("graduation_year", "20XX"),
        position=position,
        experience_highlight=experience_highlight,
        match_reason=match_reason,
    )

    # Boss直聘有字数限制（约300字），截断处理
    if len(message) > 280:
        message = message[:277] + "..."

    return message


def generate_email_intro(jd_text, position="该岗位", company="贵司", channel="招聘平台"):
    """生成邮件自我介绍"""
    info = _get_basic_info()
    db = _load_db()
    matches, jd_info = match_experiences(jd_text, top_n=3)

    # 个人亮点
    highlights = []
    edu = db.get("education", [])
    if edu:
        e = edu[0]
        h = f"{e.get('school', '')} {e.get('major', '')} {e.get('degree', '')}"
        if e.get("gpa"):
            h += f"，GPA: {e['gpa']}"
        if e.get("highlights"):
            h += f"，{', '.join(e['highlights'][:2])}"
        highlights.append(h)

    skills = db.get("skills", [])
    matched_skills = []
    for s in skills:
        if s["name"] in jd_info.get("keywords", set()) or \
           s["name"].lower() in {k.lower() for k in jd_info.get("keywords", set())}:
            matched_skills.append(s["name"])
    if matched_skills:
        highlights.append(f"技术栈: {', '.join(matched_skills[:6])}")

    highlights_text = "\n".join(f"· {h}" for h in highlights) if highlights else "（请补充个人亮点）"

    # 匹配经历
    exp_texts = []
    for m in matches:
        exp_texts.append(_format_experience_detail(m["experience"]))
    matched_exp_text = "\n".join(exp_texts) if exp_texts else "（请补充相关经历）"

    template = _load_template("email_intro.txt")
    message = template.format(
        name=info.get("name", "XX"),
        university=info.get("university", "XX大学"),
        major=info.get("major", "XX专业"),
        degree=info.get("degree", "本科"),
        graduation_year=info.get("graduation_year", "20XX"),
        position=position,
        channel=channel,
        highlights=highlights_text,
        matched_experiences=matched_exp_text,
        why_company=f"对{company}的业务方向非常感兴趣，希望能在实习中深入学习和贡献自己的力量。",
        phone=info.get("phone", ""),
        email=info.get("email", ""),
    )
    return message


def generate_interview_intro(jd_text, position="该岗位"):
    """生成面试自我介绍话术"""
    info = _get_basic_info()
    db = _load_db()
    matches, jd_info = match_experiences(jd_text, top_n=3)

    # 教育亮点
    edu = db.get("education", [])
    edu_highlight = ""
    if edu:
        e = edu[0]
        parts = []
        if e.get("gpa"):
            parts.append(f"GPA {e['gpa']}")
        if e.get("highlights"):
            parts.extend(e["highlights"][:2])
        if parts:
            edu_highlight = f"在校期间，{'，'.join(parts)}。"

    # 匹配经历（面试版，更详细但口语化）
    exp_parts = []
    for m in matches:
        exp = m["experience"]
        part = f"在{exp['title']}期间，{exp.get('description', '')}"
        if exp.get("achievements"):
            part += "。" + "；".join(exp["achievements"][:2])
        exp_parts.append(part)
    exp_text = "\n".join(f"  {i+1}. {p}" for i, p in enumerate(exp_parts)) if exp_parts else "（请补充经历）"

    # 匹配点
    match_points = []
    all_matched_tags = set()
    for m in matches:
        all_matched_tags.update(m.get("matched_tags", []))
    if all_matched_tags:
        match_points.append(f"在{'、'.join(list(all_matched_tags)[:4])}方面有实践经验")

    evaluations = db.get("self_evaluation", [])
    if evaluations:
        match_points.append(evaluations[0])

    match_text = "\n".join(f"  · {p}" for p in match_points) if match_points else "（请补充匹配点）"

    template = _load_template("interview_intro.txt")
    message = template.format(
        name=info.get("name", "XX"),
        university=info.get("university", "XX大学"),
        major=info.get("major", "XX专业"),
        degree=info.get("degree", "本科"),
        graduation_year=info.get("graduation_year", "20XX"),
        education_highlight=edu_highlight,
        matched_experiences=exp_text,
        match_points=match_text,
    )
    return message


def generate_all(jd_text, position="该岗位", company="贵司"):
    """生成所有场景的话术"""
    print("\n" + "=" * 60)
    print("  话术生成结果")
    print("=" * 60)

    print("\n" + "-" * 40)
    print("【1. Boss直聘打招呼】")
    print("-" * 40)
    boss = generate_boss_greeting(jd_text, position, company)
    print(boss)
    print(f"\n(共{len(boss)}字)")

    print("\n" + "-" * 40)
    print("【2. 邮件自我介绍】")
    print("-" * 40)
    email = generate_email_intro(jd_text, position, company)
    print(email)

    print("\n" + "-" * 40)
    print("【3. 面试自我介绍】")
    print("-" * 40)
    interview = generate_interview_intro(jd_text, position)
    print(interview)

    return {
        "boss_greeting": boss,
        "email_intro": email,
        "interview_intro": interview,
    }
