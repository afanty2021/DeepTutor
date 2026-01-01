# Demo 知识库使用 BGE-M3 重新初始化指南

## 📋 操作概述

本指南将帮助你：
1. ✅ 下载 Demo 数据包
2. ✅ 使用 BGE-M3（本地免费）初始化知识库
3. ✅ 验证知识库正常工作

---

## 🚀 完整操作步骤

### Step 1: 安装项目依赖

```bash
cd /Users/berton/Github/DeepTutor

# 安装 Python 依赖
pip3 install python-dotenv PyYAML tiktoken lightrag-hku

# 或使用安装脚本
bash scripts/install_all.sh
```

### Step 2: 下载 Demo 数据包

#### 方式 A: 浏览器下载（推荐）

1. **访问 Google Drive**
   ```
   https://drive.google.com/drive/folders/1iWwfZXiTuQKQqUYb5fGDZjLCeTUP6DA6?usp=sharing
   ```

2. **下载并解压**
   - 下载整个文件夹或 `demo_data.zip`
   - 解压到项目根目录
   - 确保得到 `data/` 文件夹结构

3. **验证数据**
   ```bash
   ls data/knowledge_bases/
   # 应该看到：ai_textbook/ 和 research_papers/
   ```

#### 方式 B: 使用 gdown（命令行）

```bash
# 安装 gdown
pip3 install gdown

# 下载 Demo 数据（示例链接，需要替换为实际链接）
# gdown https://drive.google.com/uc?id=FILE_ID -O demo_data.zip

# 解压
unzip demo_data.zip -d data/
```

### Step 3: 验证 Demo 数据

```bash
# 检查数据结构
ls -la data/knowledge_bases/

# 应该看到：
# ai_textbook/        - 数据科学教材（296 页，8 章节）
# research_papers/    - 5 篇研究论文
```

### Step 4: 初始化知识库（使用 BGE-M3）

#### 初始化 ai_textbook

```bash
cd /Users/berton/Github/DeepTutor

# 方式 A: 使用 Python 模块
python3 -m src.knowledge.start_kb init ai_textbook

# 方式 B: 使用脚本（如果存在）
bash scripts/init_kb.sh ai_textbook
```

#### 初始化 research_papers

```bash
python3 -m src.knowledge.start_kb init research_papers
```

**重要参数**：
- `--force`: 强制重新初始化（如果已存在）
- `--docs <path>`: 指定文档路径

**完整示例**：
```bash
python3 -m src.knowledge.start_kb init ai_textbook --force
```

### Step 5: 验证知识库

```bash
# 列出所有知识库
python3 -m src.knowledge.start_kb list

# 查看 ai_textbook 详细信息
python3 -m src.knowledge.start_kb info ai_textbook

# 应该看到：
# - embedding_dim: 1024 (BGE-M3)
# - embedding_model: bge-m3
# - RAG Status: Initialized
```

### Step 6: 测试知识库

```bash
# 启动服务
python3 scripts/start_web.py

# 访问前端
open http://localhost:3782

# 访问知识库页面
open http://localhost:3782/knowledge
```

---

## 📊 BGE-M3 vs 原版 Demo 对比

| 特性 | 原版 Demo | BGE-M3 版 |
|------|----------|-----------|
| **嵌入模型** | text-embedding-3-large | BGE-M3（本地） |
| **维度** | 3072 | 1024 |
| **成本** | $0.10/百万 tokens | 完全免费 |
| **速度** | ~300ms | ~100ms（本地） |
| **中文支持** | 优秀 | 优秀（专门优化） |
| **离线使用** | ❌ | ✅ |

---

## ⚠️ 常见问题

### Q1: ModuleNotFoundError: No module named 'dotenv'

```bash
# 安装缺失的依赖
pip3 install python-dotenv

# 或安装所有依赖
pip3 install -r requirements.txt
```

### Q2: Ollama 连接失败

```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 如果没运行，启动它
ollama serve
```

### Q3: 初始化失败 - 维度不匹配

```bash
# 删除旧的知识库数据
rm -rf data/knowledge_bases/ai_textbook
rm -rf data/knowledge_bases/research_papers

# 重新初始化
python3 -m src.knowledge.start_kb init ai_textbook --force
```

### Q4: 初始化很慢

```
这是正常的！首次初始化需要：
1. 读取并解析 PDF 文档
2. 分块文本
3. 调用 Ollama 生成嵌入向量（本地计算）
4. 构建向量索引和知识图谱

预计时间：
- ai_textbook: ~10-30 分钟（296 页）
- research_papers: ~5-10 分钟（5 篇论文）
```

### Q5: 内存不足

```bash
# BGE-M3 需要约 2-4GB 内存
# 如果内存不足，可以：

# 1. 关闭其他应用
# 2. 或使用更小的嵌入模型（如 bge-small）
# 3. 或分批初始化（先初始化一个知识库）
```

---

## 🔍 监控初始化进度

### 查看日志

初始化过程中，终端会显示进度信息：

```
正在初始化知识库: ai_textbook
[1/5] 正在读取文档...
[2/5] 正在解析内容...
[3/5] 正在生成嵌入向量（使用 BGE-M3）...
  进度: 100/500 块 (20%)
[4/5] 正在构建向量索引...
[5/5] 正在构建知识图谱...
✅ 初始化完成！
```

### 查看详细日志

```bash
# 日志保存在
tail -f data/user/logs/*.log
```

---

## 📈 初始化后的目录结构

```
data/knowledge_bases/
├── ai_textbook/
│   ├── input/                  # 原始 PDF 文档
│   ├── chunks/                 # 文本分块
│   ├── lightrag_cache/         # LightRAG 缓存
│   │   ├── vdb_chroma/         # 向量数据库
│   │   └── graph_db/           # 图谱数据库
│   └── kb_info.json            # 知识库信息
│
└── research_papers/
    └── ...（类似结构）
```

---

## 🎯 快速命令参考

```bash
# 列出所有知识库
python3 -m src.knowledge.start_kb list

# 查看知识库详情
python3 -m src.knowledge.start_kb info ai_textbook

# 设置默认知识库
python3 -m src.knowledge.start_kb set_default ai_textbook

# 删除知识库（小心！）
rm -rf data/knowledge_bases/ai_textbook

# 增量添加文档
python3 -m src.knowledge.add_documents ai_textbook --docs new_doc.pdf
```

---

## 🚀 下一步

初始化完成后：

1. **启动服务**
   ```bash
   python3 scripts/start_web.py
   ```

2. **测试问答**
   - 访问 http://localhost:3782/solver
   - 选择 ai_textbook 知识库
   - 提问：什么是深度学习？

3. **测试研究**
   - 访问 http://localhost:3782/research
   - 输入研究主题
   - 查看生成的报告

---

## 💡 提示

- ✅ BGE-M3 完全免费，无 API 调用成本
- ✅ 本地运行，数据隐私安全
- ✅ 中文和英文都有很好的效果
- ⚠️ 首次初始化需要较长时间
- ⚠️ 需要足够的内存（8GB+ 推荐）

---

**初始化完成后，你的 Demo 知识库将使用 BGE-M3，完全免费且高效！** 🎉
