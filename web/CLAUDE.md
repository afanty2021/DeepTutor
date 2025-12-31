# web - Web 前端模块

[根目录](../CLAUDE.md) > **web**

---

## 模块职责

`web/` 是 DeepTutor 的前端应用，基于 **Next.js 14 (App Router)** 构建，提供完整的用户界面。

---

## 目录结构

```
web/
├── app/                          # Next.js App Router
│   ├── page.tsx                 # 仪表盘（首页）
│   ├── layout.tsx               # 根布局
│   ├── globals.css              # 全局样式
│   ├── solver/                  # 问题求解页面
│   ├── question/                # 问题生成页面
│   ├── research/                # 研究页面
│   ├── guide/                   # 引导学习页面
│   ├── co_writer/               # 写作页面
│   ├── notebook/                # 笔记本页面
│   ├── ideagen/                 # 创意生成页面
│   ├── knowledge/               # 知识库页面
│   └── settings/                # 设置页面
│
├── components/                   # React 组件
│   ├── Sidebar.tsx              # 侧边栏导航（多语言支持）
│   ├── SystemStatus.tsx         # 系统状态
│   ├── ActivityDetail.tsx       # 活动详情
│   ├── CoWriterEditor.tsx       # 协作写作编辑器
│   ├── CoMarkerEditor.tsx       # 标注编辑器
│   ├── Mermaid.tsx              # Mermaid 图表
│   ├── AddToNotebookModal.tsx   # 添加到笔记本弹窗
│   ├── NotebookImportModal.tsx  # 笔记本导入弹窗
│   ├── question/                # 问题相关组件
│   │   ├── QuestionDashboard.tsx
│   │   ├── QuestionTaskGrid.tsx
│   │   └── ActiveQuestionDetail.tsx
│   ├── research/                # 研究相关组件
│   │   ├── ResearchDashboard.tsx
│   │   ├── TaskGrid.tsx
│   │   └── ActiveTaskDetail.tsx
│   └── ui/                      # UI 基础组件
│       ├── Button.tsx
│       ├── Modal.tsx
│       └── index.ts
│
├── context/                      # React Context
│   └── GlobalContext.tsx        # 全局状态管理
│
├── lib/                          # 工具库
│   └── api.ts                   # API 客户端
│
├── package.json                  # NPM 依赖
├── tsconfig.json                 # TypeScript 配置
├── tailwind.config.js            # Tailwind CSS 配置
└── postcss.config.js             # PostCSS 配置
```

---

## 技术栈

### 核心框架

- **Next.js**: 14.0.3 (App Router)
- **React**: 18.x
- **TypeScript**: 5.x

### 样式

- **Tailwind CSS**: 3.3.0
- **Framer Motion**: 动画效果

### Markdown & 数学公式

- **react-markdown**: 9.0.1
- **rehype-katex**: 7.0.0 (数学公式)
- **remark-math**: 6.0.0
- **remark-gfm**: 4.0.0 (GitHub Flavored Markdown)

### PDF 导出

- **jsPDF**: 2.5.1
- **html2canvas**: 1.4.1

### 图标

- **lucide-react**: 0.294.0

### 可视化

- **cytoscape**: 3.33.1 (图形可视化)
- **mermaid**: 11.12.2 (流程图)

---

## 页面模块详细

### 1. Dashboard (仪表盘)

**路径**: `app/page.tsx`

**功能**:
- 显示最近活动
- 知识库概览
- 笔记本统计
- 快速访问入口

---

### 2. Solver (问题求解)

**路径**: `app/solver/page.tsx`

**布局**: 双栏设计
- **左栏**: 聊天界面（消息历史 + 输入框）
- **右栏**: 逻辑流（Analysis/Solve 循环可视化）

**功能**:
- 输入问题
- 选择知识库
- 实时显示求解过程（双循环架构）
- 查看最终答案

**WebSocket**: `/api/v1/solve`

**状态管理**:
- `messages`: 消息历史
- `logicFlow`: 逻辑流状态
- `isProcessing`: 处理中标识

---

### 3. Question (问题生成)

**路径**: `app/question/page.tsx`

**三种模式状态**:
- `config`: 配置模式（表单输入）
- `generating`: 生成中（显示进度）
- `result`: 结果展示

**两种生成模式**:
1. **Custom Mode** (自定义)
   - 配置知识点/主题
   - 选择难度
   - 选择类型（选择题/问答题）
   - 设置题目数量

2. **Mimic Mode** (模仿试卷)
   - 上传 PDF 试卷
   - 或输入预解析目录名
   - 系统自动解析并生成相似题

**双视图切换**:
- **Questions Tab**: 展示生成的题目、答题界面、验证报告
- **Process Tab**: 展示生成进度（QuestionDashboard 组件）

**核心组件集成**:
- `QuestionDashboard`: Planning/Generating 两阶段进度展示
- `QuestionTaskGrid`: 并行任务网格
- `AddToNotebookModal`: 添加到笔记本

**WebSocket**: `/api/v1/question/generate`

---

### 4. Research (深度研究)

**路径**: `app/research/page.tsx`

**布局**: 左右分栏
- **左侧**: 配置面板 + 聊天界面
- **右侧**: 仪表盘/报告视图切换

**研究模式**:
- `quick`: 快速研究
- `medium`: 中等深度
- `deep`: 深度研究
- `auto`: 自动选择

**三阶段流程**:
1. **Planning**: 主题分解
2. **Researching**: 并行研究
3. **Reporting**: 报告生成

**核心组件集成**:
- `ResearchDashboard`: 三阶段进度展示
- `TaskGrid`: 并行任务网格
- `ActiveTaskDetail`: 活动任务详情

**WebSocket**: `/api/v1/research/run`

---

### 5. Guide (引导学习)

**路径**: `app/guide/page.tsx`

**功能**:
- 跨笔记本选择记录
- 生成个性化学习计划
- 交互式学习页面（iframe 渲染 HTML）
- KaTeX 数学公式自动注入
- 上下文问答

**核心特性**:
1. **多笔记本支持**: 可从多个笔记本选择记录组合学习
2. **知识点序列**: 系统自动分析并生成学习路径
3. **交互式内容**: iframe 渲染带 KaTeX 的 HTML 页面
4. **HTML 调试**: 支持报告并修复 HTML 问题
5. **可调整布局**: 支持侧边栏折叠和宽度切换（1:3/3:1）

**布局设计**:
- **左侧面板**:
  - 笔记本选择（展开/折叠）
  - 学习进度条
  - 聊天界面
- **右侧面板**:
  - 交互式学习内容（iframe）
  - 完成后显示学习总结

**REST API**:
- `POST /api/v1/guide/create_session` - 创建学习会话
- `POST /api/v1/guide/start` - 开始学习
- `POST /api/v1/guide/next` - 下一个知识点
- `POST /api/v1/guide/chat` - 发送问题
- `POST /api/v1/guide/fix_html` - 修复 HTML 问题

**关键组件**:
- `NotebookSelector`: 跨笔记本记录选择器
- `ProgressBar`: 学习进度展示
- `ChatInterface`: 聊天界面
- `HTMLViewer`: iframe 内容渲染器（带 KaTeX 自动注入）

---

### 6. Co-Writer (写作)

**路径**: `app/co_writer/page.tsx`

**功能**:
- Markdown 编辑器
- AI 文本编辑（重写/缩短/扩写）
- 自动标注
- TTS 旁白生成

**REST API**:
- `POST /api/v1/co_writer/edit`
- `POST /api/v1/co_writer/automark`
- `POST /api/v1/co_writer/narrate`

---

### 7. IdeaGen (创意生成)

**路径**: `app/ideagen/page.tsx`

**功能**:
- 跨笔记本选择记录
- 生成研究创意
- 查看结构化输出
- 保存到笔记本

**核心特性**:
1. **多笔记本支持**: 可从多个笔记本选择记录作为创意源
2. **用户思考输入**: 可选的额外思考描述
3. **实时进度**: WebSocket 流式显示生成状态
4. **创意选择**: 支持单选/全选创意
5. **保存功能**: 将创意保存到笔记本

**布局设计**:
- **左侧面板** (33%):
  - 笔记本选择器（展开/折叠）
  - 用户思考输入框
  - 生成按钮
- **右侧面板** (67%):
  - 状态栏（显示进度和状态消息）
  - 创意列表卡片

**WebSocket**: `/api/v1/ideagen/generate`

**创意卡片结构**:
- 知识点标题（带闪电图标）
- 描述摘要
- 研究创意标签预览
- 展开/收起完整声明
- 选择复选框
- 保存按钮

**状态管理** (GlobalContext):
- `isGenerating`: 生成中标识
- `generationStatus`: 状态消息
- `generatedIdeas`: 生成的创意列表
- `progress`: 进度计数

---

### 8. Notebook (笔记本)

**路径**: `app/notebook/page.tsx`

**功能**:
- 笔记本列表
- 创建/编辑/删除笔记本
- 查看笔记本记录
- 组织记录

**REST API**:
- `GET /api/v1/notebook/list`
- `POST /api/v1/notebook/create`
- `GET /api/v1/notebook/{id}`
- `PUT /api/v1/notebook/{id}`
- `DELETE /api/v1/notebook/{id}`

---

### 9. Knowledge (知识库)

**路径**: `app/knowledge/page.tsx`

**功能**:
- 知识库列表
- 创建新知识库
- 上传文档
- 查看知识库详情

**REST API**:
- `GET /api/v1/knowledge/list`
- `GET /api/v1/knowledge/{kb_name}`
- `POST /api/v1/knowledge/create`
- `POST /api/v1/knowledge/{kb_name}/upload`

---

### 10. Settings (设置)

**路径**: `app/settings/page.tsx`

**功能**:
- 系统配置
- 用户偏好

---

## 核心组件详细

### Sidebar (侧边栏导航)

**文件**: `components/Sidebar.tsx`

**功能**:
- 导航菜单（支持折叠）
- 模块快捷入口
- 多语言支持（中文/英文切换）

**导航项**:
- Dashboard（仪表盘）
- Solver（问题求解）
- Question（问题生成）
- Research（深度研究）
- Guide（引导学习）
- Co-Writer（协作写作）
- IdeaGen（创意生成）
- Notebook（笔记本）
- Knowledge（知识库）
- Settings（设置）

---

### CoWriterEditor (协作写作编辑器)

**文件**: `components/CoWriterEditor.tsx`

**核心功能**:
1. **Markdown 编辑**
   - 实时预览
   - 语法高亮
   - 自动保存

2. **AI 编辑操作**
   - Rewrite（重写）
   - Shorten（缩短）
   - Expand（扩写）

3. **AI 标注**
   - 自动检测可标注文本
   - 生成教学注释
   - 显示标注气泡

4. **PDF 导出**
   - 基于 jsPDF
   - 保留 Markdown 格式
   - 支持自定义样式

5. **TTS 旁白**
   - 文本转语音
   - 生成音频文件
   - 播放/下载功能

**状态管理**:
- `content`: 编辑器内容
- `selection`: 选中文本
- `marks`: 标注列表
- `audioUrl`: TTS 音频 URL

---

### QuestionDashboard (问题生成仪表盘)

**文件**: `components/question/QuestionDashboard.tsx`

**两阶段展示**:

**Planning 阶段**:
- 显示主题分解进度
- 任务初始化状态
- 预计完成时间

**Generating 阶段**:
- 并行任务网格
- 实时进度更新
- 完成状态追踪

**状态类型**:
- `pending`: 等待中
- `analyzing`: 分析中
- `generating`: 生成中
- `validating`: 验证中
- `done`: 完成
- `error`: 错误

**扩展标识**:
- `extended`: 扩展问题（超出 KB 范围）

---

### QuestionTaskGrid (问题任务网格)

**文件**: `components/question/QuestionTaskGrid.tsx`

**布局**: 响应式网格（1/2 列）

**任务卡片信息**:
- 任务 ID
- 状态图标（带颜色编码）
- 当前轮次/最大轮次
- 焦点/原题预览
- 结果预览或错误信息

**排序规则**:
1. 活动任务优先
2. 运行中任务次之
3. 等待中任务
4. 完成任务最后

**双模式支持**:
- **Custom Mode**: 显示 Focus（焦点主题）
- **Mimic Mode**: 显示 Origin Question（原题内容）

---

### ResearchDashboard (研究仪表盘)

**文件**: `components/research/ResearchDashboard.tsx`

**三阶段展示**:

**Planning 阶段**:
- 主题分解可视化
- 子主题队列
- 优先级排序

**Researching 阶段**:
- 并行任务网格
- 工具使用追踪
- 实时日志流

**Reporting 阶段**:
- 报告生成进度
- 章节结构预览
- 引用统计

**切换视图**:
- Dashboard View: 仪表盘模式
- Chat View: 聊天模式（仅 Researching 阶段）
- Report View: 报告预览（仅 Reporting 阶段）

---

### ResearchTaskGrid (研究任务网格)

**文件**: `components/research/TaskGrid.tsx`

**布局**: 响应式网格（1/2 列）

**任务卡片信息**:
- 主题名称
- 状态图标
- 当前操作
- 迭代次数
- 工具使用情况

**工具图标映射**:
- RAG: 蓝色数据库图标
- Web Search: 绿色地球图标
- Paper Search: 紫色学术帽图标
- Code Execute: 橙色代码图标

---

### GlobalContext (全局状态管理)

**文件**: `context/GlobalContext.tsx`

**管理状态**:
- `solveState`: 问题求解状态
- `questionState`: 问题生成状态
- `researchState`: 研究状态
- `guideState`: 引导学习状态
- `coWriterState`: 写作状态
- `ideagenState`: 创意生成状态
- `notebooks`: 笔记本列表
- `knowledgeBases`: 知识库列表
- `language`: 界面语言（中文/英文）

**提供的操作**:
- 状态更新函数
- 会话管理函数
- 数据获取函数

---

### API Client (API 客户端)

**文件**: `lib/api.ts`

**功能**:
- 统一 API 调用
- WebSocket 连接管理
- 错误处理

**配置**:
```typescript
export const apiUrl = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001";
export const wsUrl = process.env.NEXT_PUBLIC_WS_BASE || "ws://localhost:8001";
```

**辅助函数**:
- `processLatexContent()`: LaTeX 内容处理
- `formatTimestamp()`: 时间戳格式化

---

## UI 基础组件

### Button (按钮组件)

**文件**: `components/ui/Button.tsx`

**Props**:
- `variant`: "primary" | "secondary" | "danger" | "ghost"
- `size`: "sm" | "md" | "lg"
- `loading`: boolean (显示加载动画)
- `icon`: React.ReactNode (图标)
- `children`: React.ReactNode
- 继承所有原生 button 属性

**样式变体**:
- `primary`: 靛蓝色渐变 + 阴影
- `secondary`: 灰色背景
- `danger`: 红色渐变 + 阴影
- `ghost`: 透明背景 + 悬停效果

**尺寸**:
- `sm`: 小号 (px-3 py-1.5 text-xs)
- `md`: 中号 (px-4 py-2 text-sm)
- `lg`: 大号 (px-6 py-3 text-base)

**使用示例**:
```tsx
<Button variant="primary" size="md" loading={isLoading} icon={<Icon />}>
  Click Me
</Button>
```

---

### Modal (模态框组件)

**文件**: `components/ui/Modal.tsx`

**Props**:
- `isOpen`: boolean (控制显示/隐藏)
- `onClose`: () => void (关闭回调)
- `title`: string (标题)
- `children`: React.ReactNode (内容)
- `size`: "sm" | "md" | "lg" | "xl"
- `showCloseButton`: boolean

**尺寸**:
- `sm`: max-w-sm (384px)
- `md`: max-w-md (448px)
- `lg`: max-w-lg (512px)
- `xl`: max-w-xl (576px)

**特性**:
- ESC 键关闭
- 点击背景关闭
- 自动锁定 body 滚动
- 动画效果 (fade-in + zoom-in)
- 关闭按钮（可隐藏）

**使用示例**:
```tsx
<Modal isOpen={showModal} onClose={() => setShowModal(false)} title="标题" size="lg">
  <p>模态框内容</p>
</Modal>
```

---

### UI 组件导出

**文件**: `components/ui/index.ts`

```typescript
export { default as Button } from "./Button";
export { default as Modal } from "./Modal";
```

---

## API 集成

### REST API 调用

```typescript
const response = await fetch(`${apiUrl}/api/v1/knowledge/list`, {
  method: "GET",
  headers: {
    "Content-Type": "application/json",
  },
});
const data = await response.json();
```

### WebSocket 连接

```typescript
const ws = new WebSocket(`${wsUrl}/api/v1/solve`);

ws.onopen = () => {
  ws.send(JSON.stringify({
    question: "Your question",
    kb_name: "ai_textbook",
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // 处理流式数据
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

ws.onclose = () => {
  console.log("WebSocket closed");
};
```

---

## 样式系统

### Tailwind CSS

配置文件: `tailwind.config.js`

```javascript
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // 自定义颜色
      },
    },
  },
  plugins: [],
};
```

### 全局样式

文件: `app/globals.css`

包含：
- 基础样式
- CSS 变量
- 工具类

---

## 开发指南

### 安装依赖

```bash
cd web
npm install
```

### 开发模式

```bash
npm run dev
```

访问: `http://localhost:3782`

### 构建生产版本

```bash
npm run build
npm start
```

### 代码检查

```bash
npm run lint
```

---

## 添加新页面

### 1. 创建页面文件

```typescript
// app/my-page/page.tsx
export default function MyPage() {
  return (
    <div>
      <h1>My Page</h1>
      {/* 页面内容 */}
    </div>
  );
}
```

### 2. 添加导航链接

在 `components/Sidebar.tsx` 中添加：

```typescript
<Link href="/my-page">
  <SidebarItem icon={Icon} label="My Page" />
</Link>
```

---

## 添加新组件

### 1. 创建组件文件

```typescript
// components/MyComponent.tsx
export default function MyComponent({ prop1, prop2 }) {
  return (
    <div className="...">
      {/* 组件内容 */}
    </div>
  );
}
```

### 2. 导出组件（可选）

在 `components/index.ts` 中：

```typescript
export { default as MyComponent } from './MyComponent';
```

---

## 环境变量

创建 `web/.env.local`:

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8001
NEXT_PUBLIC_WS_BASE=ws://localhost:8001
```

---

## 相关文件清单

### 核心配置

- `package.json`: NPM 依赖
- `tsconfig.json`: TypeScript 配置
- `tailwind.config.js`: Tailwind CSS 配置
- `postcss.config.js`: PostCSS 配置
- `next.config.js`: Next.js 配置

### 入口文件

- `app/page.tsx`: 首页（仪表盘）
- `app/layout.tsx`: 根布局
- `lib/api.ts`: API 客户端

### UI 基础组件

- `components/ui/Button.tsx`: 按钮组件
- `components/ui/Modal.tsx`: 模态框组件
- `components/ui/index.ts`: UI 组件导出

### 页面组件

- `app/guide/page.tsx`: 引导学习页面（1444 行）
- `app/ideagen/page.tsx`: 创意生成页面（754 行）

---

## 常见问题 (FAQ)

### Q1: API 连接失败？

检查：
1. 后端服务是否启动
2. `NEXT_PUBLIC_API_BASE` 是否正确配置
3. CORS 设置是否允许前端域名

### Q2: WebSocket 连接断开？

可能原因：
1. 长时间操作导致超时
2. 网络不稳定
3. 后端服务重启

### Q3: 样式不生效？

检查：
1. Tailwind CSS 配置是否正确
2. class 名是否拼写正确
3. 是否需要清除浏览器缓存

### Q4: Guide 页面 HTML 不显示数学公式？

解决方案：
1. Guide 页面已实现 `injectKaTeX()` 函数自动注入 KaTeX 支持
2. 检查 HTML 是否包含 KaTeX CDN 链接
3. 如果没有，系统会自动添加 KaTeX CSS 和 JS

### Q5: iframe 内容加载失败？

可能原因：
1. srcdoc 属性不支持（使用 contentDocument 回退）
2. 同源策略限制（使用 sandbox 属性放宽）
3. HTML 内容过大（检查浏览器控制台错误）

---

## 相关模块

- **API Backend**: `src/api/` - FastAPI 后端服务
- **Config**: `config/main.yaml` - 端口和路径配置
- **Agents**: `src/agents/` - 智能体实现
- **Guide Agent**: `src/agents/guide/` - 引导学习智能体
- **IdeaGen Agent**: `src/agents/ideagen/` - 创意生成智能体

---

## 变更记录

### 2025-12-31 19:52:47 CST - 深度补捞第 3 轮
- 新增 UI 基础组件文档 (Button, Modal)
- 新增 Guide 页面详细文档（跨笔记本选择、KaTeX 注入、可调布局）
- 新增 IdeaGen 页面详细文档（多笔记本支持、实时进度、创意卡片）
- 新增 docs/ 文档站点结构记录

---

*最后更新: 2025-12-31 19:52:47 CST*
