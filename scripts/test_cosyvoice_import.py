#!/usr/bin/env python3
"""Test CosyVoice import and diagnose issues"""

import sys
import os

# Add CosyVoice to path
cosyvoice_path = "/Users/berton/Github/CosyVoice"
if cosyvoice_path not in sys.path:
    sys.path.insert(0, cosyvoice_path)

print("=" * 60)
print("CosyVoice 导入诊断")
print("=" * 60)

# Test 1: Check basic dependencies
print("\n1. 检查基础依赖...")
deps_to_check = [
    'torch',
    'torchaudio',
    'numpy',
    'transformers',
    'tqdm',
    'modelscope',
]

for dep in deps_to_check:
    try:
        mod = __import__(dep)
        version = getattr(mod, '__version__', 'unknown')
        print(f"  ✅ {dep}: {version}")
    except ImportError as e:
        print(f"  ❌ {dep}: {e}")

# Test 2: Try importing CosyVoice CLI
print("\n2. 尝试导入 CosyVoice CLI...")
try:
    from cosyvoice.cli.cosyvoice import AutoModel
    print("  ✅ CosyVoice CLI 导入成功")
except ImportError as e:
    print(f"  ❌ CosyVoice CLI 导入失败: {e}")

    # Try to get more details
    print("\n3. 详细错误分析...")
    import traceback
    traceback.print_exc()

# Test 3: Check Qwen2ForCausalLM availability
print("\n4. 检查 Qwen2 模型可用性...")
try:
    from transformers import AutoConfig
    print("  ✅ transformers AutoModel 可用")

    # Try to load Qwen2 config
    try:
        config = AutoConfig.from_pretrained("Qwen/Qwen2-0.5B", trust_remote_code=True)
        print(f"  ✅ Qwen2 配置加载成功: {config}")
    except Exception as e:
        print(f"  ⚠️  Qwen2 配置加载失败: {e}")

except ImportError as e:
    print(f"  ❌ transformers 不可用: {e}")

# Test 4: ModelScope model loading
print("\n5. 测试 ModelScope 模型加载...")
try:
    from modelscope import snapshot_download
    print("  ✅ ModelScope snapshot_download 可用")

    # Check if model exists
    model_dir = "/Users/berton/.cache/modelscope/hub/FunAudioLLM/Fun-CosyVoice3-0.5B-2512"
    if os.path.exists(model_dir):
        print(f"  ✅ 模型目录存在: {model_dir}")

        # List files
        files = os.listdir(model_dir)
        print(f"  📁 模型文件 ({len(files)} 个):")
        for f in sorted(files)[:10]:
            print(f"     - {f}")
    else:
        # Try to find any matching directory
        import glob
        pattern = "/Users/berton/.cache/modelscope/hub/FunAudioLLM/Fun-CosyVoice3-0.5B*"
        matches = glob.glob(pattern)
        if matches:
            print(f"  ✅ 找到模型目录: {matches[0]}")
        else:
            print(f"  ❌ 模型目录不存在")

except ImportError as e:
    print(f"  ❌ ModelScope 不可用: {e}")

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
