#!/bin/bash
# Download CosyVoice model using ModelScope

set -e

echo "=================================================="
echo "CosyVoice 模型下载脚本"
echo "=================================================="

# 检查 conda 环境
if [[ -z "${CONDA_DEFAULT_ENV}" ]]; then
    echo "❌ 请先激活 conda 环境:"
    echo "   conda activate DeepTutor-env-3.11"
    exit 1
fi

echo "✅ 当前环境: ${CONDA_DEFAULT_ENV}"

# 检查 ModelScope 是否安装
echo ""
echo "检查 ModelScope..."
python3 -c "import modelscope; print('✅ ModelScope 已安装')" || {
    echo "❌ ModelScope 未安装，正在安装..."
    pip install modelscope
}

# 下载模型
echo ""
echo "开始下载 CosyVoice 3.0 模型..."
echo "模型: FunAudioLLM/Fun-CosyVoice3-0.5B"
echo "大小: 约 1-2 GB"
echo "位置: ~/.cache/modelscope/hub/FunAudioLLM/"
echo ""

python3 << 'EOF'
from modelscope import snapshot_download
import os

# 下载模型
model_dir = snapshot_download(
    'FunAudioLLM/Fun-CosyVoice3-0.5B',
    cache_dir=os.path.expanduser('~/.cache/modelscope')
)

print(f"\n✅ 模型下载成功！")
print(f"模型位置: {model_dir}")

# 列出模型文件
print("\n📁 模型文件:")
files = os.listdir(model_dir)
for f in sorted(files)[:15]:
    file_path = os.path.join(model_dir, f)
    if os.path.isfile(file_path):
        size = os.path.getsize(file_path) / (1024*1024)  # MB
        print(f"  - {f} ({size:.1f} MB)")
    else:
        print(f"  📂 {f}/")

if len(files) > 15:
    print(f"  ... 还有 {len(files) - 15} 个文件")
EOF

echo ""
echo "=================================================="
echo "模型下载完成！"
echo "=================================================="
echo ""
echo "现在可以测试 CosyVoice TTS:"
echo "  python3 src/tools/cosyvoice_tts.py"
echo ""
