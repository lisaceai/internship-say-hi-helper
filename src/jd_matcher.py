"""JD匹配引擎 - 将岗位JD与个人经历进行匹配"""

import re

try:
    import jieba
    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False

from experience_manager import _load_db, get_all_tags


def _tokenize(text):
    """中文分词，若无jieba则用简单字符切分"""
    if HAS_JIEBA:
        return set(jieba.cut(text))
    # 简单回退：按标点和空白切分 + 2-gram
    tokens = set(re.split(r'[，。、；：！？\s,;:!?\n\r]+', text))
    tokens.discard("")
    words = re.findall(r'[\u4e00-\u9fff]{2,4}|[a-zA-Z0-9+#]+', text)
    tokens.update(words)
    return tokens


def parse_jd(jd_text):
    """解析JD，提取关键信息"""
    result = {
        "raw": jd_text,
        "keywords": set(),
        "requirements": [],
    }

    # 提取JD中的关键词
    tokens = _tokenize(jd_text)
    # 获取用户经验库中的所有标签
    my_tags = get_all_tags()

    # 关键词 = JD分词结果中与个人标签匹配的 + JD中的技术关键词
    tech_pattern = re.compile(
        r'(?:Python|Java|C\+\+|JavaScript|TypeScript|Go|Rust|SQL|'
        r'React|Vue|Angular|Node\.?js|Spring|Django|Flask|FastAPI|'
        r'Docker|K8s|Kubernetes|AWS|Azure|GCP|Linux|Git|'
        r'MySQL|PostgreSQL|MongoDB|Redis|Kafka|RabbitMQ|'
        r'机器学习|深度学习|NLP|CV|大模型|LLM|AI|'
        r'数据分析|数据挖掘|ETL|Spark|Hadoop|Flink|'
        r'产品|运营|市场|营销|策划|商业分析|'
        r'PPT|Excel|Tableau|Power\s*BI|SPSS|'
        r'文案|写作|新媒体|短视频|小红书|抖音)',
        re.IGNORECASE
    )
    tech_matches = set(tech_pattern.findall(jd_text))
    result["keywords"].update(tech_matches)

    # 匹配个人标签
    jd_lower = jd_text.lower()
    for tag in my_tags:
        if tag.lower() in jd_lower:
            result["keywords"].add(tag)

    # 提取岗位要求（按行切分，找带序号或关键提示的行）
    lines = jd_text.strip().split("\n")
    for line in lines:
        line = line.strip()
        if re.match(r'^[\d一二三四五六七八九十]+[.、)）]', line) or \
           any(kw in line for kw in ["负责", "参与", "熟悉", "了解", "掌握", "具备", "能够", "有"]):
            result["requirements"].append(line)

    return result


def match_experiences(jd_text, top_n=5):
    """将JD与经验库中的经历匹配，返回排序后的匹配结果"""
    db = _load_db()
    jd_info = parse_jd(jd_text)
    jd_keywords = jd_info["keywords"]
    jd_tokens = _tokenize(jd_text)

    scored = []
    for exp in db.get("experiences", []):
        score = 0
        matched_tags = []

        # 标签匹配（权重最高）
        exp_tags = set(exp.get("tags", []))
        for tag in exp_tags:
            if tag in jd_keywords or tag.lower() in {k.lower() for k in jd_keywords}:
                score += 10
                matched_tags.append(tag)

        # 内容文本匹配
        exp_text = exp.get("description", "") + " ".join(exp.get("achievements", []))
        exp_tokens = _tokenize(exp_text)
        overlap = jd_tokens & exp_tokens
        # 过滤掉过短的匹配词
        meaningful_overlap = {w for w in overlap if len(w) >= 2}
        score += len(meaningful_overlap) * 2

        # 实习经历加权
        if exp.get("type") == "internship":
            score += 5
        elif exp.get("type") == "project":
            score += 3

        if score > 0:
            scored.append({
                "experience": exp,
                "score": score,
                "matched_tags": matched_tags,
                "matched_words": list(meaningful_overlap)[:10],
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n], jd_info


def print_match_result(jd_text):
    """打印匹配结果"""
    matches, jd_info = match_experiences(jd_text)

    print("=" * 50)
    print("  JD 匹配分析")
    print("=" * 50)

    print(f"\n【JD关键词】{', '.join(jd_info['keywords']) if jd_info['keywords'] else '未提取到明确关键词'}")

    if jd_info["requirements"]:
        print(f"\n【岗位要求】")
        for r in jd_info["requirements"][:8]:
            print(f"  · {r}")

    if matches:
        print(f"\n【匹配经历】(共匹配到 {len(matches)} 条)")
        for i, m in enumerate(matches, 1):
            exp = m["experience"]
            print(f"\n  {i}. [{exp['type']}] {exp['title']}  (匹配度: {m['score']})")
            if m["matched_tags"]:
                print(f"     匹配标签: {', '.join(m['matched_tags'])}")
            if exp.get("achievements"):
                for a in exp["achievements"][:2]:
                    print(f"     - {a}")
    else:
        print("\n  未找到匹配经历，建议补充相关经历到经验库。")

    return matches, jd_info
