# CosyVoice TTS 设置和测试指南

## 📋 概述

CosyVoice 是阿里巴巴 DAMO 学院开源的多语言 TTS 系统，支持：
- **9 种语言**：中文、英文、日文、韩文、德文、西班牙文、法文、意大利文、俄文
- **18+ 中文方言/口音**：粤语、闽南语、四川话、东北话、陕西话等
- **多种推理模式**：SFT、零样本、跨语言、指令控制

**完全免费，本地运行！**

---

## ✅ 已完成的修改

| 文件 | 状态 | 说明 |
|------|------|------|
| `src/tools/cosyvoice_tts.py` | ✅ 新建 | CosyVoice TTS 工具类 |
| `src/agents/co_writer/narrator_agent.py` | ✅ 替换 | 支持 CosyVoice + OpenAI 双模式 |
| `src/core/core.py` | ✅ 更新 | `get_tts_config()` 支持 CosyVoice |
| `.env` | ✅ 更新 | 添加 CosyVoice 配置 |

---

## 🚀 快速设置

### Step 1: 激活 Conda 环境

```bash
conda activate DeepTutor-env-3.11
```

### Step 2: 安装 CosyVoice 依赖

**重要说明**：
- CosyVoice 是源码项目，没有标准的 `setup.py`
- 需要手动安装依赖包到 conda 环境
- 脚本会自动安装所有必要的依赖

**方法 1: 使用自动安装脚本（推荐）**

```bash
# 确保在 conda 环境中
conda activate DeepTutor-env-3.11

# 运行安装脚本
bash scripts/install_cosyvoice_deps.sh
```

**方法 2: 手动安装依赖**

```bash
# 确保在 conda 环境中
conda activate DeepTutor-env-3.11

# 安装核心依赖
pip install --upgrade \
    tqdm modelscope torch torchaudio pyyaml \
    conformer diffusers transformers accelerate \
    einops inflect librosa scipy sentencepiece onnxruntime
```

**安装说明**：
- 安装时间：约 5-10 分钟（取决于网络速度）
- torch/torchaudio 可能需要较大下载空间（~2GB）
- 包含 matcha-tts 依赖（用于流式匹配）
- 如果遇到版本冲突，脚本会自动处理

### Step 3: 验证模型文件

CosyVoice 模型应该已经存在于你的 CosyVoice 源码目录中：

```bash
# 检查模型目录
ls -la /Users/berton/Github/CosyVoice/pretrained_models/Fun-CosyVoice3-0.5B/

# 应该看到模型文件：
# - cosyvoice3.yaml
# - flow.pt
# - hift.pt
# - llm.pt
# - 等文件
```

**模型位置说明**：
- DeepTutor 代码会自动检测 CosyVoice 仓库中的模型
- 默认路径：`/Users/berton/Github/CosyVoice/pretrained_models/Fun-CosyVoice3-0.5B/`
- 如果模型在其他位置，可以通过 `COSYVOICE_MODEL_DIR` 环境变量指定

### Step 4: 测试 CosyVoice

```bash
cd /Users/berton/Github/DeepTutor

# 激活环境
conda activate DeepTutor-env-3.11

# 测试 TTS 工具
python3 src/tools/cosyvoice_tts.py
```

**预期输出**：
```
Testing CosyVoice TTS...
==================================================

1. Testing instruct mode...
✅ Audio saved to: cosyvoice_20250101_xxxxx.wav
   Duration: 5.23s

2. Testing MP3 conversion...
✅ MP3 saved to: cosyvoice_20250101_xxxxx.mp3

==================================================
Test completed!
```

---

## ⚙️ 配置说明

### .env 文件配置

```bash
# TTS 提供商选择
USE_COSYVOICE=true        # 使用 CosyVoice（本地免费）

# CosyVoice 版本
COSYVOICE_VERSION=3.0    # 推荐：3.0 最新版

# 推理模式
COSYVOICE_MODE=instruct  # 指令模式（推荐）

# Conda 环境
COSYVOICE_CONDA_ENV=DeepTutor-env-3.11

# 默认说话人
TTS_VOICE=中文女         # 可选：中文男, 英文女, etc.
```

### 可选配置

```bash
# 自定义模型路径（如果使用非默认路径）
# 默认情况下，系统会自动查找 ~/.cache/modelscope/hub/FunAudioLLM/
# 如果模型在其他位置，可以手动指定完整路径：
COSYVOICE_MODEL_DIR=/Users/berton/.cache/modelscope/hub/FunAudioLLM/Fun-CosyVoice3-0.5B-2512

# 切换到 OpenAI TTS（备用，付费）
USE_COSYVOICE=false
TTS_MODEL=tts-1
TTS_URL=https://api.openai.com/v1
TTS_API_KEY=你的OpenAI_API_Key
```

**自动查找机制**：
- 系统会自动在 `~/.cache/modelscope/hub/FunAudioLLM/` 目录下查找匹配的模型
- 支持带日期后缀的目录（如 `Fun-CosyVoice3-0.5B-2512`）
- 优先使用最新修改的模型目录
- 大多数情况下无需设置 `COSYVOICE_MODEL_DIR`

---

## 🎤 说话人选项

### CosyVoice 内置说话人（Instruct 模式）

| 说话人 | 代码 | 说明 |
|--------|------|------|
| 中文女 | `中文女` | 默认，自然女声 |
| 中文男 | `中文男` | 自然男声 |
| 英文女 | `英文女` | English female |
| 英文男 | `英文男` | English male |
| 粤语女 | `粤语女` | 广东话女声 |
| 四川话 | `四川话` | 四川话女声 |
| 东北话 | `东北话` | 东北话女声 |

### 指令控制示例

```python
# 语速控制
"请用快一点的语速说这句话<|endofprompt|>"
"请用慢一点的语速说这句话<|endofprompt|>"

# 情感控制
"[laughter]哈哈哈哈，这真是太有趣了[laughter]"
"[breath]（深呼吸）让我慢慢告诉你[breath]"

# 方言控制
"请用四川话说这句话<|endofprompt|>"
"请用广东话说这句话<|endofprompt|>"
```

---

## 🧪 测试 TTS 功能

### 方法 1: 直接测试工具

```bash
conda activate DeepTutor-env-3.11
python3 src/tools/cosyvoice_tts.py
```

### 方法 2: 在 Web 界面测试

```bash
# 启动服务
python3 scripts/start_web.py

# 访问 Co-Writer 页面
open http://localhost:3782/co_writer

# 测试步骤：
# 1. 输入文本
# 2. 点击 "Narrate" 按钮
# 3. 选择说话人（中文女/中文男）
# 4. 等待音频生成
# 5. 播放音频
```

### 方法 3: Python API 测试

```python
import asyncio
from src.agents.co_writer.narrator_agent import NarratorAgent

async def test_tts():
    narrator = NarratorAgent(use_cosyvoice=True)

    # 生成旁白
    result = await narrator.narrate(
        content="今天天气真不错，适合出去散步。",
        style="friendly",
        voice="中文女",
        output_format="mp3"
    )

    print(f"音频已生成: {result['audio_path']}")
    print(f"说话人: {result['voice']}")
    print(f"TTS 提供商: {result['tts_provider']}")
    print(f"时长: {result.get('duration', 0):.2f}秒")

asyncio.run(test_tts())
```

---

## 📊 CosyVoice vs 其他 TTS

| 特性 | CosyVoice | OpenAI TTS | 阿里云 TTS |
|------|-----------|------------|------------|
| **成本** | 完全免费 | $15/百万字符 | ¥0.5/百万字符 |
| **语言支持** | 9 种语言 + 18+ 方言 | 多语言 | 中英文 |
| **质量** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **延迟** | ~500ms（本地，GPU ~200ms） | ~200ms | ~300ms |
| **自定义** | 高（指令控制） | 低 | 中 |
| **离线使用** | ✅ | ❌ | ❌ |
| **声音克隆** | ✅ 零样本 | ❌ | ❌ |
| **GPU 加速** | ✅ MPS/CUDA | ❌ | ❌ |

---

## ⚠️ 常见问题

### Q1: 模型未下载

**错误**：`FileNotFoundError: pretrained_models/Fun-CosyVoice3-0.5B`

**解决**：
```bash
# 下载模型
cd /Users/berton/Github/CosyVoice
python3 -m from_platform import ModelScope
ms = ModelScope()
ms.snapshot_download('FunAudioLLM/Fun-CosyVoice3-0.5B')
```

### Q2: Conda 环境错误

**错误**：`conda activate DeepTutor-env-3.11` 失败

**解决**：
```bash
# 检查环境
conda env list

# 创建环境（如果不存在）
conda create -n DeepTutor-env-3.11 python=3.11 -y

# 安装依赖
conda activate DeepTutor-env-3.11
pip install torch torchaudio pyyaml
```

### Q3: 音频生成失败

**错误**：`RuntimeError: Failed to load CosyVoice`

**解决**：
```bash
# 检查 CosyVoice 安装
cd /Users/berton/Github/CosyVoice
python3 -c "from cosyvoice.cli.cosyvoice import AutoModel; print('OK')"

# 重新安装 CosyVoice
pip install -e .

# 检查模型文件
ls pretrained_models/Fun-CosyVoice3-0.5B/
```

### Q4: MP3 转换失败

**错误**：`ffmpeg: command not found`

**解决**：
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg

# 或保持 WAV 格式（无需转换）
# 在代码中使用 output_format="wav"
```

### Q5: 生成速度慢

```
首次生成会慢（模型加载），后续会快很多

优化建议：
1. 预加载模型（保持服务运行）
2. GPU 加速（自动检测）
   - Apple Silicon (M1/M2/M3): 自动启用 MPS 加速
   - NVIDIA GPU: 自动启用 CUDA 加速
   - 其他: 使用 CPU
3. 缩短文本长度
```

**GPU 加速说明**：
- 系统会自动检测并使用最佳可用设备
- 查看日志确认使用的设备：`Using device: mps` / `cuda` / `cpu`
- MPS 加速可提升 2-3 倍速度（Apple Silicon）
- CUDA 加速可提升 3-5 倍速度（NVIDIA GPU）

---

## 💡 高级用法

### 零样本声音克隆

```python
from src.tools.cosyvoice_tts import CosyVoiceTTS

tts = CosyVoiceTTS(mode="zero_shot")

# 使用参考音频克隆声音
result = tts.synthesize(
    text="这是测试音频。",
    prompt_audio="./reference.wav",  # 参考音频路径
    output_path="cloned.wav"
)
```

### 跨语言合成

```python
tts = CosyVoiceTTS(mode="cross_lingual")

result = tts.synthesize(
    text="Hello, this is a test.",
    prompt_audio="./chinese_reference.wav",
    output_path="cross_lingual.wav"
)
```

### 流式生成

```python
# 使用流式推理（实时生成）
result = tts.synthesize(
    text="这是一个长文本...",
    stream=True  # 启用流式
)
```

---

## 🎯 下一步

### 1. 在 Co-Writer 中使用

访问 `http://localhost:3782/co_writer`，然后：
1. 输入或粘贴文本
2. 点击 "Narrate" 按钮
3. 选择说话人和风格
4. 等待音频生成
5. 播放或下载音频

### 2. API 集成

```python
from src.agents.co_writer.narrator_agent import NarratorAgent

# 初始化（自动使用 CosyVoice）
narrator = NarratorAgent()

# 生成旁白
result = await narrator.narrate(
    content="你的内容...",
    style="friendly",
    voice="中文女"
)
```

### 3. 自定义配置

```python
# 使用不同版本
narrator_v2 = NarratorAgent(use_cosyvoice=True)
# 修改 cosyvoice_tts.py 中的版本参数

# 使用不同模式
tts = CosyVoiceTTS(mode="sft")  # 监督微调模式
tts = CosyVoiceTTS(mode="zero_shot")  # 零样本模式
```

---

## 📚 相关资源

- **CosyVoice GitHub**: https://github.com/FunAudioLLM/CosyVoice
- **Demo 页面**: https://funaudiollm.github.io/cosyvoice3/
- **论文**: https://arxiv.org/pdf/2505.17589
- **ModelScope**: https://www.modelscope.cn/models/FunAudioLLM/Fun-CosyVoice3-0.5B

---

**配置完成！** 🎉

你的 DeepTutor 现在使用：
- LLM: 智谱 GLM-4-Flash
- Embedding: Ollama BGE-M3（免费）
- Web Search: Exa AI
- **TTS: CosyVoice（免费）** ✨

**总成本：约 ¥5/月**（仅 LLM 费用）
