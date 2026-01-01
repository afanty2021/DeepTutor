#!/bin/bash
# Install CosyVoice dependencies in DeepTutor conda environment

set -e

echo "=================================================="
echo "CosyVoice 依赖安装脚本"
echo "=================================================="

# 检查 conda 环境
if [[ -z "${CONDA_DEFAULT_ENV}" ]]; then
    echo "❌ 请先激活 conda 环境:"
    echo "   conda activate DeepTutor-env-3.11"
    exit 1
fi

echo "✅ 当前环境: ${CONDA_DEFAULT_ENV}"
echo "   Python: $(which python3)"

# 进入 CosyVoice 目录
COSYVOICE_ROOT="/Users/berton/Github/CosyVoice"
cd "${COSYVOICE_ROOT}"

echo ""
echo "安装 CosyVoice 核心依赖..."

# 方法：直接从 CosyVoice 的 requirements.txt 安装
# 但排除一些不需要的大型依赖（如 deepspeed, gradio webui）

# 先安装核心 TTS 依赖（使用兼容版本）
echo ""
echo "安装 PyTorch 生态系统（兼容版本）..."
# 使用 torchvision 要求的 torch 版本以避免兼容性问题
pip install --upgrade \
    'torch==2.3.1' \
    'torchaudio==2.3.1' \
    'torchvision==0.18.1'

echo ""
echo "安装 CosyVoice 核心依赖..."
# 基于CosyVoice requirements.txt
pip install --upgrade \
    tqdm \
    'numpy==1.26.4' \
    pyyaml \
    'modelscope>=1.20.0' \
    einops \
    'conformer>=0.3.2' \
    'accelerate>=0.20.0,<1.0.0' \
    'transformers==4.51.3' \
    'diffusers>=0.20.0,<1.0.0' \
    sentencepiece \
    inflect \
    librosa \
    scipy \
    'onnx==1.16.0' \
    onnxruntime \
    'lightning>=2.2.0' \
    'x-transformers>=2.11.0' \
    'wetext>=0.0.4' \
    gdown \
    rich \
    soundfile \
    'pyarrow>=18.0.0' \
    omegaconf \
    'matcha-tts>=0.0.7' || {
    echo ""
    echo "⚠️  部分依赖安装失败，继续验证..."
}

echo ""
echo "安装可选依赖（可能失败）..."
pip install --upgrade \
    colorful \
    cn2an \
    'eng-to-ipa>=0.0.1' \
    hydra-core \
    HyperPyYAML \
    'matplotlib>=3.5.0,<4.0.0' \
    pypinyin \
    pyworld \
    zhconv 2>/dev/null || echo "  (部分可选依赖未安装，不影响主要功能)"

echo ""
echo "✅ CosyVoice 依赖安装完成！"
echo ""
echo "验证安装："
python3 << 'EOF'
import sys
sys.path.insert(0, '/Users/berton/Github/CosyVoice')
try:
    from cosyvoice.cli.cosyvoice import AutoModel
    print("✅ CosyVoice 导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)
EOF

echo ""
echo "现在可以运行测试："
echo "  cd /Users/berton/Github/DeepTutor"
echo "  python3 src/tools/cosyvoice_tts.py"
