"""经验库管理模块 - 管理个人简历与经历数据"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DATA_DIR, "experience_db.json")


def _load_db():
    """加载经验库"""
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"basic_info": {}, "experiences": [], "skills": [], "self_evaluation": []}


def _save_db(db):
    """保存经验库"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def init_from_resume(resume_path):
    """从简历JSON初始化经验库"""
    with open(resume_path, "r", encoding="utf-8") as f:
        resume = json.load(f)

    db = _load_db()
    db["basic_info"] = resume.get("basic_info", {})
    db["self_evaluation"] = resume.get("self_evaluation", [])

    # 收集所有技能
    skills_data = resume.get("skills", {})
    all_skills = []
    for category, items in skills_data.items():
        for item in items:
            all_skills.append({"name": item, "category": category})
    db["skills"] = all_skills

    # 将所有经历统一归入经验库
    experiences = []

    for item in resume.get("internships", []):
        experiences.append({
            "type": "internship",
            "title": f'{item["company"]} - {item["position"]}',
            "time": f'{item.get("start_date", "")} ~ {item.get("end_date", "")}',
            "description": item.get("description", ""),
            "achievements": item.get("achievements", []),
            "tags": item.get("tags", []),
            "added_at": datetime.now().isoformat(),
        })

    for item in resume.get("projects", []):
        experiences.append({
            "type": "project",
            "title": f'{item["name"]} ({item.get("role", "")})',
            "time": f'{item.get("start_date", "")} ~ {item.get("end_date", "")}',
            "description": item.get("description", ""),
            "achievements": item.get("achievements", []),
            "tags": item.get("tags", []),
            "added_at": datetime.now().isoformat(),
        })

    for item in resume.get("competitions", []):
        experiences.append({
            "type": "competition",
            "title": f'{item["name"]} - {item.get("award", "")}',
            "time": item.get("date", ""),
            "description": item.get("description", ""),
            "achievements": [],
            "tags": item.get("tags", []),
            "added_at": datetime.now().isoformat(),
        })

    for item in resume.get("campus_activities", []):
        experiences.append({
            "type": "campus",
            "title": f'{item.get("organization", "")} - {item.get("role", "")}',
            "time": f'{item.get("start_date", "")} ~ {item.get("end_date", "")}',
            "description": item.get("description", ""),
            "achievements": [],
            "tags": item.get("tags", []),
            "added_at": datetime.now().isoformat(),
        })

    db["experiences"] = experiences
    db["education"] = resume.get("education", [])

    _save_db(db)
    print(f"✓ 经验库初始化完成，共导入 {len(experiences)} 条经历")
    return db


def add_experience(exp_type, title, description, achievements, tags, time_range=""):
    """添加一条新经历"""
    db = _load_db()
    exp = {
        "type": exp_type,
        "title": title,
        "time": time_range,
        "description": description,
        "achievements": achievements if isinstance(achievements, list) else [achievements],
        "tags": tags if isinstance(tags, list) else [t.strip() for t in tags.split(",")],
        "added_at": datetime.now().isoformat(),
    }
    db["experiences"].append(exp)
    _save_db(db)
    print(f"✓ 已添加经历: {title}")
    return exp


def show_experience_db():
    """展示经验库概况"""
    db = _load_db()
    info = db.get("basic_info", {})

    print("=" * 50)
    print(f"  个人经验库 - {info.get('name', '未设置')}")
    print(f"  {info.get('university', '')} {info.get('major', '')}")
    print("=" * 50)

    type_names = {
        "internship": "实习经历",
        "project": "项目经历",
        "competition": "竞赛经历",
        "campus": "校园经历",
        "other": "其他经历",
    }

    experiences = db.get("experiences", [])
    by_type = {}
    for exp in experiences:
        t = exp.get("type", "other")
        by_type.setdefault(t, []).append(exp)

    for t, name in type_names.items():
        items = by_type.get(t, [])
        if items:
            print(f"\n【{name}】({len(items)}条)")
            for i, item in enumerate(items, 1):
                print(f"  {i}. {item['title']}")
                if item.get("time"):
                    print(f"     时间: {item['time']}")
                if item.get("tags"):
                    print(f"     标签: {', '.join(item['tags'])}")
                if item.get("achievements"):
                    for a in item["achievements"]:
                        print(f"     - {a}")

    skills = db.get("skills", [])
    if skills:
        print(f"\n【技能标签】")
        skill_by_cat = {}
        for s in skills:
            skill_by_cat.setdefault(s.get("category", "other"), []).append(s["name"])
        for cat, names in skill_by_cat.items():
            print(f"  {cat}: {', '.join(names)}")

    print(f"\n共 {len(experiences)} 条经历, {len(skills)} 个技能标签")
    return db


def get_all_tags():
    """获取经验库中所有标签"""
    db = _load_db()
    tags = set()
    for exp in db.get("experiences", []):
        tags.update(exp.get("tags", []))
    for skill in db.get("skills", []):
        tags.add(skill["name"])
    return tags
