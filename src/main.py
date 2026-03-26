#!/usr/bin/env python3
"""实习投递小助手 - CLI入口"""

import argparse
import sys
import os

# 确保src目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from experience_manager import init_from_resume, add_experience, show_experience_db
from jd_matcher import print_match_result
from message_generator import generate_all


def cmd_init(args):
    """初始化经验库"""
    if not os.path.exists(args.resume):
        print(f"错误: 找不到简历文件 {args.resume}")
        print("提示: 参考 data/resume_sample.json 创建你的简历文件")
        sys.exit(1)
    init_from_resume(args.resume)


def cmd_add(args):
    """交互式添加经历"""
    print("=== 添加新经历 ===\n")

    type_map = {
        "1": "internship",
        "2": "project",
        "3": "competition",
        "4": "campus",
        "5": "other",
    }
    print("经历类型:")
    print("  1. 实习经历")
    print("  2. 项目经历")
    print("  3. 竞赛经历")
    print("  4. 校园经历")
    print("  5. 其他经历")
    type_choice = input("\n选择类型 (1-5): ").strip()
    exp_type = type_map.get(type_choice, "other")

    title = input("标题 (如: XX公司 - XX实习生): ").strip()
    time_range = input("时间 (如: 2025-06 ~ 2025-09): ").strip()
    description = input("描述: ").strip()

    print("成果/亮点 (每行一条，输入空行结束):")
    achievements = []
    while True:
        line = input("  - ").strip()
        if not line:
            break
        achievements.append(line)

    tags = input("标签 (逗号分隔, 如: Python,数据分析,后端): ").strip()

    add_experience(exp_type, title, description, achievements, tags, time_range)


def cmd_show(args):
    """展示经验库"""
    show_experience_db()


def cmd_match(args):
    """JD匹配"""
    jd_text = _get_jd_text(args)
    print_match_result(jd_text)


def cmd_generate(args):
    """生成话术"""
    jd_text = _get_jd_text(args)
    position = args.position or "该岗位"
    company = args.company or "贵司"
    use_api = getattr(args, "api", False)
    generate_all(jd_text, position, company, use_api=use_api)


def cmd_set_key(args):
    """设置智谱API Key"""
    from zhipu_client import setup_api_key
    setup_api_key(args.key)


def _get_jd_text(args):
    """获取JD文本，支持直接输入或从文件读取"""
    if args.jd:
        return args.jd
    if args.jd_file:
        if not os.path.exists(args.jd_file):
            print(f"错误: 找不到JD文件 {args.jd_file}")
            sys.exit(1)
        with open(args.jd_file, "r", encoding="utf-8") as f:
            return f.read()
    # 交互式输入
    print("请粘贴岗位JD (输入空行结束):")
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "" and lines:
                break
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="实习投递小助手 - 帮你高效投递实习",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py init --resume ../data/resume.json     初始化经验库
  python main.py add                                    添加新经历
  python main.py show                                   查看经验库
  python main.py match --jd "JD内容"                    JD匹配分析
  python main.py generate --jd "JD内容" -p 后端实习生    生成话术（本地模板）
  python main.py generate --jd "JD内容" -p 后端实习生 --api  生成话术（智谱API）
  python main.py set-key YOUR_ZHIPU_API_KEY             设置智谱API Key
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # init
    p_init = subparsers.add_parser("init", help="从简历初始化经验库")
    p_init.add_argument("--resume", "-r", required=True, help="简历JSON文件路径")
    p_init.set_defaults(func=cmd_init)

    # add
    p_add = subparsers.add_parser("add", aliases=["add-experience"], help="添加新经历")
    p_add.set_defaults(func=cmd_add)

    # show
    p_show = subparsers.add_parser("show", help="查看经验库")
    p_show.set_defaults(func=cmd_show)

    # match
    p_match = subparsers.add_parser("match", help="JD匹配分析")
    p_match.add_argument("--jd", help="JD文本内容")
    p_match.add_argument("--jd-file", help="JD文件路径")
    p_match.set_defaults(func=cmd_match)

    # generate
    p_gen = subparsers.add_parser("generate", aliases=["gen"], help="生成话术")
    p_gen.add_argument("--jd", help="JD文本内容")
    p_gen.add_argument("--jd-file", help="JD文件路径")
    p_gen.add_argument("--position", "-p", help="岗位名称")
    p_gen.add_argument("--company", "-c", help="公司名称")
    p_gen.add_argument("--api", action="store_true",
                       help="使用智谱API生成（需先配置API Key）")
    p_gen.set_defaults(func=cmd_generate)

    # set-key
    p_key = subparsers.add_parser("set-key", help="设置智谱API Key")
    p_key.add_argument("key", help="你的智谱API Key")
    p_key.set_defaults(func=cmd_set_key)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
