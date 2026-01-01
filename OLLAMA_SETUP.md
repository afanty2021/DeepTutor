# Ollama + BGE-M3 快速设置指南

## 📋 完整配置清单

✅ **LLM**: 智谱 GLM-4-Flash
✅ **Embedding**: Ollama BGE-M3（本地免费）
✅ **Web Search**: Exa AI

---

## 🚀 快速设置步骤

### Step 1: 安装和配置 Ollama

#### macOS/Linux
```bash
# 1. 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. 启动 Ollama 服务
ollama serve

# 3. 下载 BGE-M3 模型（新开一个终端）
ollama pull bge-m3:v2

# 4. 验证安装
curl http://localhost:11434/api/tags
```

#### Windows
```powershell
# 1. 下载 Ollama
# 访问 https://ollama.com/download
# 下载并安装 Windows 版本

# 2. 启动 Ollama（安装后自动运行）

# 3. 下载 BGE-M3 模型
ollama pull bge-m3:v2

# 4. 验证安装
curl http://localhost:11434/api/tags
```

### Step 2: 获取 API Keys

#### 2.1 智谱 AI API Key（必需）
```
1. 访问：https://open.bigmodel.cn/usercenter/apikeys
2. 注册/登录
3. 创建 API Key
4. 复制保存
```

#### 2.2 Exa AI API Key（推荐）
```
1. 访问：https://dashboard.exa.ai
2. 使用 GitHub 或邮箱注册
3. 进入 API Keys 页面
4. 创建 API Key
5. 复制保存
```

### Step 3: 编辑 `.env` 文件

```bash
cd /Users/berton/Github/DeepTutor
vim .env  # 或使用你喜欢的编辑器
```

填入以下配置：

```bash
# ============================================
# 必需配置
# ============================================

# LLM 配置（智谱 GLM-4）
LLM_BINDING_API_KEY=你的智谱API_Key

# Embedding 配置（已配置为 Ollama，无需修改）
EMBEDDING_BINDING=ollama
EMBEDDING_MODEL=bge-m3:v2
EMBEDDING_DIM=1024
EMBEDDING_BINDING_HOST=http://localhost:11434

# Web Search 配置（Exa AI）
EXA_API_KEY=你的Exa_API_Key
```

### Step 4: 测试 Ollama 连接

```bash
# 测试嵌入模型
curl http://localhost:11434/api/embeddings -d '{
  "model": "bge-m3:v2",
  "prompt": "你好，世界"
}'
```

预期输出：
```json
{
  "embedding": [数组...]
}
```

### Step 5: 安装 Python 依赖

```bash
cd /Users/berton/Github/DeepTutor
pip install exa-python
bash scripts/install_all.sh
```

### Step 6: 启动服务

```bash
# 确保先启动 Ollama
ollama serve

# 新开终端，启动 DeepTutor
conda activate aitutor  # 如果使用 conda
python scripts/start_web.py
```

### Step 7: 验证运行

```bash
# 访问前端
open http://localhost:3782

# 访问 API 文档
open http://localhost:8001/docs
```

---

## 🧪 测试知识库创建

### 创建测试知识库

1. 访问 http://localhost:3782/knowledge
2. 点击 "New Knowledge Base"
3. 输入名称：`test_kb`
4. 上传一个测试 PDF 文件
5. 等待处理完成

### 验证嵌入

```bash
# 查看知识库配置
cat data/knowledge_bases/kb_config.json

# 应该看到：
{
  "test_kb": {
    "embedding_model": "bge-m3:v2",
    "embedding_dim": 1024
  }
}
```

---

## ⚠️ 常见问题

### Q1: Ollama 连接失败
```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 如果失败，重启 Ollama
ollama serve
```

### Q2: 模型下载慢
```bash
# 使用镜像（如果访问慢）
export OLLAMA_HOST=mirror.ollama.com
ollama pull bge-m3:v2
```

### Q3: 内存不足
```
BGE-M3 需要约 2-4GB 内存
建议：
- 关闭其他应用
- 或使用更小的模型（bge-small）
```

### Q4: 嵌入维度错误
```bash
# 错误：维度不匹配
# 解决：删除旧知识库，重新创建
rm -rf data/knowledge_bases/旧知识库名
```

---

## 📊 性能参考

| 配置 | 首次嵌入 | 后续嵌入 | 内存占用 |
|------|---------|---------|----------|
| BGE-M3 (本地) | ~500ms | ~100ms | ~2GB |
| 智谱 embedding-2 | ~300ms | ~200ms | 0 |

---

## 💡 优化建议

### 提升嵌入速度

```bash
# 设置 Ollama 使用 GPU（如果有）
OLLAMA_NUM_GPU=1 ollama serve

# 或在 .env 中配置
EMBEDDING_BINDING_HOST=http://localhost:11434
# Ollama 会自动使用可用 GPU
```

### 多知识库管理

```bash
# 每个知识库独立初始化
python -m src.knowledge.start_kb init kb1 --docs doc1.pdf
python -m src.knowledge.start_kb init kb2 --docs doc2.pdf

# 查看所有知识库
python -m src.knowledge.start_kb list
```

---

## 🎯 下一步

1. ✅ Ollama + BGE-M3 已配置
2. ✅ `.env` 文件已更新
3. ✅ 可以开始创建知识库

需要帮助？
- 查看 [README.md](README.md)
- 访问 [官方文档](https://hkuds.github.io/DeepTutor/)
- 提交 [Issue](https://github.com/HKUDS/DeepTutor/issues)

---

**配置完成！** 🎉

你的 DeepTutor 现在使用：
- LLM: 智谱 GLM-4-Flash（便宜快速）
- Embedding: Ollama BGE-M3（本地免费）
- Web Search: Exa AI（高质量研究）

月成本预估：**¥5-10**（仅 LLM 费用）
