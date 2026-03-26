# 实习投递小助手 (Internship Say-Hi Helper)

一个帮助你高效投递实习的命令行工具。

## 功能

1. **经验库管理** - 基于简历和经历，构建结构化的个人经验库
2. **JD 匹配** - 根据岗位 JD，自动匹配最相关的个人经历
3. **话术生成** - 生成 Boss 直聘打招呼、邮件自我介绍、面试自我介绍话术

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 1. 初始化经验库（导入简历）
python src/main.py init --resume data/resume.json

# 2. 添加新经历
python src/main.py add-experience

# 3. 根据 JD 生成话术
python src/main.py generate --jd "粘贴JD内容"

# 4. 查看经验库
python src/main.py show
```

## 项目结构

```
├── data/
│   ├── resume.json          # 简历数据（结构化）
│   └── experience_db.json   # 经验库
├── src/
│   ├── main.py              # CLI 入口
│   ├── experience_manager.py # 经验库管理
│   ├── jd_matcher.py        # JD 匹配引擎
│   └── message_generator.py # 话术生成器
├── templates/
│   ├── boss_greeting.txt    # Boss直聘打招呼模板
│   ├── email_intro.txt      # 邮件自我介绍模板
│   └── interview_intro.txt  # 面试自我介绍模板
└── requirements.txt
```

## 使用流程

1. 将简历信息填入 `data/resume.json`
2. 运行 `python src/main.py init` 初始化经验库
3. 随时用 `python src/main.py add-experience` 增补经历
4. 找到心仪岗位后，运行 `python src/main.py generate --jd "JD内容"` 生成话术
