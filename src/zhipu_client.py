"""智谱API客户端 - 调用GLM模型生成求职话术"""

import json
import os
import urllib.request
import urllib.error

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CONFIG_PATH = os.path.join(CONFIG_DIR, "api_config.json")

# 智谱API endpoint
ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"


def _load_api_key():
    """从配置文件或环境变量加载API Key"""
    # 优先环境变量
    key = os.environ.get("ZHIPU_API_KEY", "")
    if key:
        return key
    # 其次配置文件
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("zhipu_api_key", "")
    return ""


def _load_config():
    """加载API配置"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def setup_api_key(api_key):
    """保存API Key到配置文件"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config = _load_config()
    config["zhipu_api_key"] = api_key
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("✓ API Key 已保存")


def call_zhipu(system_prompt, user_prompt, model="glm-4-flash", temperature=0.7):
    """调用智谱API

    Args:
        system_prompt: 系统提示词
        user_prompt: 用户提示词
        model: 模型名称，默认 glm-4-flash（免费额度大）
        temperature: 温度参数

    Returns:
        生成的文本内容，失败时返回 None
    """
    api_key = _load_api_key()
    if not api_key:
        print("错误: 未配置智谱API Key")
        print("请通过以下方式之一配置：")
        print("  1. 环境变量: export ZHIPU_API_KEY=your_key")
        print("  2. 命令行:   python src/main.py set-key YOUR_KEY")
        print("  3. 前往 https://open.bigmodel.cn 注册获取API Key")
        return None

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ZHIPU_API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            content = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            total_tokens = usage.get("total_tokens", "?")
            print(f"  [API] 模型: {model} | Token用量: {total_tokens}")
            return content
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        print(f"错误: API调用失败 (HTTP {e.code})")
        if "401" in str(e.code):
            print("  → API Key无效，请检查后重新设置")
        elif "429" in str(e.code):
            print("  → 请求频率过高，请稍后重试")
        else:
            print(f"  → {body[:200]}")
        return None
    except urllib.error.URLError as e:
        print(f"错误: 网络连接失败 - {e.reason}")
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None
