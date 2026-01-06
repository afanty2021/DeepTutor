import os
from huggingface_hub import snapshot_download

print("=" * 60)
print("MinerU 模型下载")
print("=" * 60)
print("模型: opendatalab/MinerU2.5-2509-1.2B")
print("大小: 约 2.4 GB")
print("位置: ~/.cache/huggingface/hub/")
print("=" * 60)
print()

# 使用镜像站点（可选，如果直连慢）
# os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

try:
    print("开始下载...")
    model_path = snapshot_download(
        'opendatalab/MinerU2.5-2509-1.2B',
        repo_type='model',
        resume_download=True,  # 支持断点续传
    )
    print(f"\n✅ 下载完成!")
    print(f"模型位置: {model_path}")

    # 验证文件
    safetensors_path = os.path.join(model_path, 'model.safetensors')
    if os.path.exists(safetensors_path):
        size_gb = os.path.getsize(safetensors_path) / (1024**3)
        print(f"model.safetensors: {size_gb:.2f} GB ✅")
    else:
        print("⚠️  model.safetensors 未找到")
        print("已下载文件:")
        for f in os.listdir(model_path):
            print(f"  - {f}")

except Exception as e:
    print(f"\n❌ 下载失败: {e}")
    print("\n建议:")
    print("1. 检查网络连接")
    print("2. 稍后重试（可能有速率限制）")
    print("3. 或使用镜像站点")
