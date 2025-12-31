# src - 核心后端模块

[根目录](../CLAUDE.md) > **src**

---

## 模块职责

`src/` 是 DeepTutor 的核心后端模块，包含：

- **Agents** (智能体层): 6 大核心功能智能体
- **API** (接口层): FastAPI 后端服务
- **Core** (核心层): 配置、日志、LLM 封装
- **Knowledge** (知识库层): 基于 LightRAG 的知识库管理
- **Tools** (工具层): RAG、搜索、代码执行等工具

---

## 目录结构

```
src/
├── agents/                    # 智能体模块
│   ├── solve/                # 问题求解智能体（双循环架构）
│   ├── question/             # 问题生成智能体（双模式）
│   ├── research/             # 深度研究智能体（DR-in-KG）
│   ├── guide/                # 引导学习智能体
│   ├── ideagen/              # 自动创意生成智能体
│   └── co_writer/            # 交互式写作智能体
│
├── api/                       # API 后端
│   ├── main.py               # FastAPI 应用入口
│   ├── run_server.py         # 服务器启动脚本
│   ├── routers/              # 路由模块
│   └── utils/                # API 工具（日志拦截、进度广播）
│
├── core/                      # 核心工具
│   ├── core.py               # 配置加载、LLM 初始化
│   ├── setup.py              # 系统初始化
│   └── logging/              # 日志系统
│
├── knowledge/                 # 知识库管理
│   ├── start_kb.py           # KB 启动脚本（主入口）
│   ├── initializer.py        # KB 初始化器
│   ├── add_documents.py      # 增量文档添加
│   ├── manager.py            # KB 管理器
│   └── extract_numbered_items.py  # 编号项目提取
│
└── tools/                     # 工具集合
    ├── rag_tool.py           # RAG 检索工具
    ├── web_search.py         # 网络搜索工具
    ├── code_executor.py      # 代码执行工具
    ├── paper_search_tool.py  # 论文搜索工具
    └── query_item_tool.py    # 编号项目查询工具
```

---

## 智能体模块 (agents/)

### 1. Solve - 问题求解智能体

**路径**: `src/agents/solve/`

**架构**: 双循环架构（Analysis Loop + Solve Loop）

**核心组件**:
- `MainSolver`: 主控制器
- `analysis_loop/`: 分析循环（InvestigateAgent + NoteAgent）
- `solve_loop/`: 求解循环（PlanAgent → ManagerAgent → SolveAgent → CheckAgent）
- `memory/`: 记忆系统（InvestigateMemory + SolveMemory）

**详细文档**: [src/agents/solve/README.md](agents/solve/README.md)

---

### 2. Question - 问题生成智能体

**路径**: `src/agents/question/`

**架构**: 双模式架构

**两种模式**:
- **Custom Mode**: 基于知识库的自定义生成
- **Mimic Mode**: 基于参考试卷的模仿生成

**核心组件**:
- `AgentCoordinator`: 协调器
- `QuestionGenerationAgent`: 生成智能体（ReAct 循环）
- `ValidationWorkflow`: 验证工作流

**详细文档**: [src/agents/question/README.md](agents/question/README.md)

---

### 3. Research - 深度研究智能体

**路径**: `src/agents/research/`

**架构**: DR-in-KG（动态主题队列）

**三阶段流程**:
1. **Planning**: RephraseAgent + DecomposeAgent
2. **Researching**: ManagerAgent + ResearchAgent + NoteAgent
3. **Reporting**: ReportingAgent

**核心特性**:
- 并行/串行执行模式
- 统一引用管理系统
- 动态主题发现

**详细文档**: [src/agents/research/README.md](agents/research/README.md)

---

### 4. Guide - 引导学习智能体

**路径**: `src/agents/guide/`

**多智能体架构**:
- `LocateAgent`: 知识点定位
- `InteractiveAgent`: 交互页面生成
- `ChatAgent`: 上下文问答
- `SummaryAgent`: 学习总结

**详细文档**: [src/agents/guide/README.md](agents/guide/README.md)

---

### 5. IdeaGen - 自动创意生成智能体

**路径**: `src/agents/ideagen/`

**双过滤工作流**:
1. `MaterialOrganizerAgent`: 知识点提取
2. `BaseIdeaAgent`: 宽过滤 → 探索 → 严过滤 → 生成

**详细文档**: [src/agents/ideagen/README.md](agents/ideagen/README.md)

---

### 6. Co-Writer - 交互式写作智能体

**路径**: `src/agents/co_writer/`

**核心功能**:
- `EditAgent`: 重写、缩短、扩写
- `NarratorAgent`: TTS 旁白生成

**详细文档**: [src/agents/co_writer/README.md](agents/co_writer/README.md)

---

## API 模块 (api/)

**路径**: `src/api/`

**框架**: FastAPI + Uvicorn

**接口类型**:
- **REST API**: 标准 HTTP 请求
- **WebSocket**: 实时流式传输

**路由模块** (`routers/`):
- `solve.py`: 问题求解接口
- `question.py`: 问题生成接口
- `research.py`: 研究接口
- `knowledge.py`: 知识库接口
- `guide.py`: 引导学习接口
- `co_writer.py`: 写作接口
- `notebook.py`: 笔记本接口
- `ideagen.py`: 创意生成接口
- `dashboard.py`: 仪表盘接口
- `settings.py`: 设置接口
- `system.py`: 系统接口

**工具模块** (`utils/`):
- `history.py`: 活动历史管理
- `log_interceptor.py`: 日志拦截（流式传输）
- `notebook_manager.py`: 笔记本管理
- `progress_broadcaster.py`: 进度广播
- `task_id_manager.py`: 任务 ID 管理

**详细文档**: [src/api/README.md](api/README.md)

---

## 核心工具模块 (core/)

**路径**: `src/core/`

**核心功能**:
- `core.py`: 配置加载、LLM 初始化
- `setup.py`: 系统初始化（目录创建）
- `logging/`: 统一日志系统

**详细文档**: [src/core/README.md](core/README.md)

---

## 知识库模块 (knowledge/)

**路径**: `src/knowledge/`

**基于**: LightRAG-HKU

**核心功能**:
- `start_kb.py`: 主入口脚本（CLI）
- `initializer.py`: 知识库初始化
- `add_documents.py`: 增量文档添加
- `manager.py`: 知识库管理器
- `extract_numbered_items.py`: 编号项目提取

**详细文档**: [src/knowledge/README.md](knowledge/README.md)

---

## 工具模块 (tools/)

**路径**: `src/tools/`

**核心工具**:

| 工具 | 文件 | 功能 |
|------|------|------|
| RAG Tool | `rag_tool.py` | 基于 LightRAG 的检索 |
| Web Search | `web_search.py` | Perplexity API 网络搜索 |
| Code Executor | `code_executor.py` | Python 沙箱代码执行 |
| Paper Search | `paper_search_tool.py` | arXiv 论文搜索 |
| Query Item | `query_item_tool.py` | 编号项目查询 |
| TeX Chunker | `tex_chunker.py` | LaTeX 文档分块 |
| TeX Downloader | `tex_downloader.py` | LaTeX 资源下载 |

**详细文档**: [src/tools/README.md](tools/README.md)

---

## 入口与启动

### Web 服务（推荐）

```bash
python scripts/start_web.py
# 或
python src/api/run_server.py
```

### CLI 模式

```bash
python scripts/start.py
```

### 知识库管理

```bash
# 列出知识库
python -m src.knowledge.start_kb list

# 初始化新知识库
python -m src.knowledge.start_kb init my_kb --docs doc.pdf

# 增量添加文档
python -m src.knowledge.add_documents my_kb --docs new_doc.pdf
```

---

## 对外接口

### REST API 示例

```bash
# 获取知识库列表
curl http://localhost:8001/api/v1/knowledge/list

# 创建学习会话
curl -X POST http://localhost:8001/api/v1/guide/create_session \
  -H "Content-Type: application/json" \
  -d '{"notebook_ids": ["nb1"]}'
```

### WebSocket 示例

```javascript
// 连接问题求解接口
const ws = new WebSocket('ws://localhost:8001/api/v1/solve');

ws.onopen = () => {
  ws.send(JSON.stringify({
    question: "What is deep learning?",
    kb_name: "ai_textbook"
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

---

## 关键依赖

### Python 依赖 (`requirements.txt`)

```
fastapi>=0.100.0          # Web 框架
uvicorn[standard]>=0.24.0 # ASGI 服务器
openai>=1.0.0             # LLM API
lightrag-hku>=1.0.0       # RAG 引擎
websockets>=12.0          # WebSocket 支持
```

### 外部依赖

- **LightRAG**: 知识图谱 + 向量存储
- **RAG-Anything**: 多模态 RAG

---

## 配置文件

### `config/main.yaml`

主配置文件，包含：
- 端口配置
- 路径配置
- 工具开关
- 各模块参数

### `config/agents.yaml`

智能体 LLM 参数配置：
- temperature
- max_tokens
- model 选择

---

## 测试与质量

### 代码质量工具

- **Ruff**: Python 格式化和 Linting
- **Pre-commit**: Git hooks

```bash
# 运行检查
ruff format .
ruff check .

# Pre-commit
pre-commit run --all-files
```

---

## 常见问题 (FAQ)

### Q1: 如何添加新的智能体？

1. 在 `src/agents/` 下创建新目录
2. 继承 `BaseAgent` 基类
3. 在 `src/api/routers/` 中添加对应路由
4. 在前端添加对应页面

### Q2: 如何修改 LLM 参数？

编辑 `config/agents.yaml` 中的对应模块配置。

### Q3: 知识库初始化失败？

检查：
- `.env` 文件配置
- LLM API key 是否有效
- 使用 `clean-rag` 命令清理损坏的 RAG 存储

---

## 相关文件清单

### 核心入口

- `scripts/start_web.py`: Web 服务启动
- `scripts/start.py`: CLI 模式启动
- `src/api/main.py`: FastAPI 应用
- `src/api/run_server.py`: 服务器启动

### 配置文件

- `config/main.yaml`: 主配置
- `config/agents.yaml`: 智能体参数
- `.env.example`: 环境变量模板

---

*最后更新: 2025-12-31 19:52:47 CST*
