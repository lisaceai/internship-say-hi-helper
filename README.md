# 实习投递小助手 (Internship Say-Hi Helper)

一个帮助你高效投递实习的命令行工具，支持本地模板和智谱AI两种生成模式。

## 功能

1. **经验库管理** - 基于简历和经历，构建结构化的个人经验库
2. **JD 匹配** - 根据岗位 JD，自动匹配最相关的个人经历
3. **话术生成** - 生成 Boss 直聘打招呼、求职邮件、面试自我介绍话术
   - **本地模板模式**：零API消耗，秒出结果
   - **智谱API模式**：调用 GLM-4 生成高质量、结构化的求职话术

## 快速开始

```bash
# 1. 初始化经验库（导入简历）
python src/main.py init --resume data/resume_sample.json

# 2. 添加新经历（交互式）
python src/main.py add

# 3. 查看经验库
python src/main.py show

# 4. 本地模板生成话术
python src/main.py generate --jd "粘贴JD内容" -p "岗位名" -c "公司名"

# 5. 智谱API生成话术（需先配置API Key）
python src/main.py set-key YOUR_ZHIPU_API_KEY
python src/main.py generate --jd "粘贴JD内容" -p "岗位名" -c "公司名" --api
```

## 智谱API配置

1. 前往 [智谱开放平台](https://open.bigmodel.cn) 注册账号
2. 获取 API Key
3. 配置（二选一）：
   ```bash
   # 方式1：命令行保存
   python src/main.py set-key YOUR_API_KEY

   # 方式2：环境变量
   export ZHIPU_API_KEY=YOUR_API_KEY
   ```

默认使用 `glm-4-flash` 模型（有免费额度），单次生成约 1200-1900 token。

## 项目结构

```
├── data/
│   ├── resume_sample.json   # 简历模板（填入你的信息）
│   ├── resume.json          # 你的简历数据（gitignore）
│   ├── experience_db.json   # 经验库（自动生成）
│   └── api_config.json      # API配置（gitignore）
├── src/
│   ├── main.py              # CLI 入口
│   ├── experience_manager.py # 经验库管理
│   ├── jd_matcher.py        # JD 匹配引擎
│   ├── message_generator.py # 话术生成器（本地+API双模式）
│   └── zhipu_client.py      # 智谱API客户端
├── prompts/
│   ├── boss_system.txt      # Boss直聘 system prompt
│   ├── boss_user.txt        # Boss直聘 user prompt 模板
│   ├── email_system.txt     # 求职邮件 system prompt
│   ├── email_user.txt       # 求职邮件 user prompt 模板
│   ├── interview_system.txt # 面试介绍 system prompt
│   └── interview_user.txt   # 面试介绍 user prompt 模板
├── templates/
│   ├── boss_greeting.txt    # 本地模板：Boss直聘打招呼
│   ├── email_intro.txt      # 本地模板：邮件自我介绍
│   └── interview_intro.txt  # 本地模板：面试自我介绍
└── requirements.txt
```

## 使用流程

1. 复制 `data/resume_sample.json` 为 `data/resume.json`，填入你的真实信息
2. 运行 `python src/main.py init -r data/resume.json` 初始化经验库
3. 随时用 `python src/main.py add` 增补新经历
4. 找到心仪岗位后：
   - 快速生成：`python src/main.py generate --jd "JD" -p "岗位" -c "公司"`
   - AI生成：加上 `--api` 参数调用智谱API生成高质量话术

## Prompt 定制

`prompts/` 目录下的 prompt 文件可以自由修改，调整生成风格：
- 修改 `email_system.txt` 可调整求职邮件的结构、语气、字数要求
- 修改 `boss_system.txt` 可调整 Boss 直聘打招呼的风格
- 修改 `interview_system.txt` 可调整面试自我介绍的节奏

个人固定信息（姓名、学校、联系方式等）已固化在 system prompt 中，每次调用只需传入 JD 和匹配经历。
