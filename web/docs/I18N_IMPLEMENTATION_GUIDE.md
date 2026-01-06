# DeepTutor 国际化（i18n）实现指南

> **实施日期**: 2025年1月4日
> **版本**: v1.0.0
> **支持语言**: 中文（zh）、英文（en）

---

## 📋 实施概览

DeepTutor 现已支持完整的中英文双语界面切换。本文档说明如何使用和扩展国际化功能。

---

## ✅ 已完成的工作

### 1. 核心翻译文件扩展

**文件**: `/Users/berton/Github/DeepTutor/web/lib/i18n.ts`

**新增内容**:
- ✅ 扩展了翻译条目从 ~100 个到 **400+ 个**
- ✅ 覆盖所有主要页面和组件
- ✅ 添加了通用翻译（按钮、操作、状态等）

**翻译覆盖范围**:
```typescript
- 通用词汇（Common）：50+ 条
- 设置页面（Settings）：50+ 条
- 仪表盘（Dashboard）：20+ 条
- 问题求解器（Solver）：30+ 条
- 题目生成器（Question）：40+ 条
- 深度研究（Research）：40+ 条
- 引导学习（Guide）：30+ 条
- 智能写作（Co-Writer）：25+ 条
- 创意生成（IdeaGen）：25+ 条
- 笔记本（Notebook）：25+ 条
- 知识库（Knowledge）：30+ 条
```

### 2. 语言切换器组件

**文件**: `/Users/berton/Github/DeepTutor/web/components/LanguageSwitcher.tsx`

**功能**:
- ✅ 简洁的切换按钮设计
- ✅ 显示当前语言（EN/中文）
- ✅ 一键切换，立即生效
- ✅ 自动保存到全局状态

**使用方式**:
```tsx
import LanguageSwitcher from "@/components/LanguageSwitcher";

<LanguageSwitcher />
```

### 3. Sidebar 集成

**文件**: `/Users/berton/Github/DeepTutor/web/components/Sidebar.tsx`

**更新内容**:
- ✅ 在顶部添加了语言切换器
- ✅ 位于 GitHub 链接左侧
- ✅ 保持布局美观和功能一致性

### 4. 示例页面更新

**文件**: `/Users/berton/Github/DeepTutor/web/app/solver/page.tsx`

**更新内容**:
- ✅ 添加了 i18n 导入
- ✅ 添加了 `t()` 翻译函数
- ✅ 更新了关键文本使用翻译

---

## 🚀 如何使用

### 用户端使用

#### 切换语言

1. **在 Sidebar 中切换**:
   - 点击左上角的语言切换器按钮（显示 "EN" 或 "中文"）
   - 语言会立即切换，无需刷新页面

2. **在设置页面切换**:
   - 导航到 "Settings" 页面
   - 在 "Interface Preferences" 部分选择 "Language"
   - 选择 "English" 或 "Chinese"

#### 默认语言

- 系统默认语言为**英语（en）**
- 首次访问时显示英文界面
- 语言设置会保存在浏览器本地存储中

---

## 👨‍💻 开发者指南

### 为新页面添加国际化

#### 步骤 1: 导入依赖

```tsx
import { useGlobal } from "@/context/GlobalContext";
import { getTranslation } from "@/lib/i18n";
```

#### 步骤 2: 添加翻译函数

```tsx
export default function MyPage() {
  const { uiSettings } = useGlobal();
  const t = (key: string) => getTranslation(uiSettings.language, key);

  // ... 组件代码
}
```

#### 步骤 3: 替换硬编码文本

**之前**:
```tsx
<h1>Welcome to DeepTutor</h1>
<button>Submit</button>
```

**之后**:
```tsx
<h1>{t("Welcome to DeepTutor")}</h1>
<button>{t("Submit")}</button>
```

### 添加新的翻译条目

#### 在 `lib/i18n.ts` 中添加

```typescript
export const translations = {
  en: {
    // ... 现有翻译
    "My New Text": "My New Text",
    "Another Translation": "Another Translation",
  },
  zh: {
    // ... 现有翻译
    "My New Text": "我的新文本",
    "Another Translation": "另一个翻译",
  },
};
```

#### 翻译规范

1. **键名规范**:
   - 使用英文键名
   - 使用 PascalCase 或句子格式
   - 键名应清晰描述内容

   ```typescript
   // ✅ 好的键名
   "Start Research": "开始研究"
   "Generating ideas...": "正在生成创意..."

   // ❌ 不好的键名
   "btn1": "开始"
   "txt": "生成中"
   ```

2. **翻译质量**:
   - 中文翻译应自然流畅
   - 避免直译，注重本地化
   - 保持专业术语一致性

3. **上下文相关**:
   - 考虑文本的使用场景
   - 提供足够的上下文信息
   - 使用描述性的键名

### 翻译文件结构

```typescript
export const translations = {
  en: {
    // Sidebar - 侧边栏导航
    "Dashboard": "Dashboard",
    "Settings": "Settings",

    // Common - 通用词汇
    "Save": "Save",
    "Cancel": "Cancel",

    // [Page Name] - 页面特定翻译
    "Page Title": "Page Title",
    "Action Button": "Action Button",
  },
  zh: {
    // Sidebar - 侧边栏导航
    "Dashboard": "仪表盘",
    "Settings": "设置",

    // Common - 通用词汇
    "Save": "保存",
    "Cancel": "取消",

    // [页面名称] - 页面特定翻译
    "Page Title": "页面标题",
    "Action Button": "操作按钮",
  },
};
```

---

## 📝 待完成的页面国际化

以下页面仍需添加国际化支持：

### 高优先级（核心功能）

1. **Question Page** (`app/question/page.tsx`)
   - 题目生成器界面
   - 预计需要更新 50+ 处文本

2. **Research Page** (`app/research/page.tsx`)
   - 深度研究界面
   - 预计需要更新 60+ 处文本

3. **Guide Page** (`app/guide/page.tsx`)
   - 引导学习界面
   - 预计需要更新 40+ 处文本

### 中优先级（辅助功能）

4. **Co-Writer Page** (`app/co_writer/page.tsx`)
   - 智能写作界面
   - 预计需要更新 30+ 处文本

5. **IdeaGen Page** (`app/ideagen/page.tsx`)
   - 创意生成界面
   - 预计需要更新 35+ 处文本

6. **Notebook Page** (`app/notebook/page.tsx`)
   - 笔记本管理界面
   - 预计需要更新 40+ 处文本

7. **Knowledge Page** (`app/knowledge/page.tsx`)
   - 知识库管理界面
   - 预计需要更新 45+ 处文本

### 低优先级（次要功能）

8. **其他组件**
   - `AddToNotebookModal.tsx`
   - `NotebookImportModal.tsx`
   - 其他 UI 组件

---

## 🔧 实现模板

### 页面级国际化模板

```tsx
"use client";

import { useState } from "react";
import { useGlobal } from "@/context/GlobalContext";
import { getTranslation } from "@/lib/i18n";

export default function MyPage() {
  const { uiSettings } = useGlobal();
  const t = (key: string) => getTranslation(uiSettings.language, key);

  const [data, setData] = useState("");

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">
        {t("Page Title")}
      </h1>

      <p className="text-slate-600 mb-4">
        {t("Page description goes here")}
      </p>

      <button className="btn-primary">
        {t("Submit")}
      </button>

      {data && (
        <div className="mt-4">
          <p>{t("Results")}: {data}</p>
        </div>
      )}
    </div>
  );
}
```

### 组件级国际化模板

```tsx
"use client";

import { useGlobal } from "@/context/GlobalContext";
import { getTranslation } from "@/lib/i18n";

interface MyComponentProps {
  title?: string;
}

export default function MyComponent({ title }: MyComponentProps) {
  const { uiSettings } = useGlobal();
  const t = (key: string) => getTranslation(uiSettings.language, key);

  return (
    <div className="component">
      <h2>{title || t("Default Title")}</h2>
      <button>{t("Action")}</button>
    </div>
  );
}
```

---

## 🧪 测试指南

### 手动测试步骤

#### 1. 语言切换测试

```bash
# 1. 启动开发服务器
cd /Users/berton/Github/DeepTutor/web
npm run dev

# 2. 在浏览器中访问
open http://localhost:3782

# 3. 测试步骤
# - 点击语言切换器按钮
# - 验证所有文本立即切换
# - 刷新页面，验证语言设置保持
# - 测试不同页面的语言一致性
```

#### 2. 翻译完整性测试

- [ ] Sidebar 所有菜单项
- [ ] Dashboard 页面
- [ ] Settings 页面
- [ ] Solver 页面
- [ ] Question 页面
- [ ] Research 页面
- [ ] Guide 页面
- [ ] Co-Writer 页面
- [ ] IdeaGen 页面
- [ ] Notebook 页面
- [ ] Knowledge 页面

#### 3. 边缘情况测试

- [ ] 长文本翻译是否正确换行
- [ ] 按钮文本翻译后布局是否正常
- [ ] 表单验证消息是否翻译
- [ ] 错误提示是否翻译
- [ ] 加载状态是否翻译

---

## 📊 翻译覆盖率统计

### 当前状态

| 模块 | 翻译条目 | 页面更新 | 覆盖率 |
|------|---------|---------|--------|
| **翻译文件** | 400+ | - | 100% |
| **语言切换器** | - | ✅ | 100% |
| **Sidebar** | 15 | ✅ | 100% |
| **Dashboard** | 25 | ✅ | 100% |
| **Settings** | 55 | ✅ | 100% |
| **Solver** | 30 | ⚠️ 部分完成 | ~30% |
| **Question** | 40 | ❌ 待完成 | 0% |
| **Research** | 40 | ❌ 待完成 | 0% |
| **Guide** | 30 | ❌ 待完成 | 0% |
| **Co-Writer** | 25 | ❌ 待完成 | 0% |
| **IdeaGen** | 25 | ❌ 待完成 | 0% |
| **Notebook** | 25 | ❌ 待完成 | 0% |
| **Knowledge** | 30 | ❌ 待完成 | 0% |

**总体进度**: ~35%

---

## 🎯 下一步计划

### 短期目标（1-2周）

1. ✅ **完成核心翻译文件** - 已完成
2. ✅ **创建语言切换器组件** - 已完成
3. ✅ **更新 Sidebar** - 已完成
4. ⚠️ **完成 Solver 页面国际化** - 部分完成
5. ❌ **完成 Question 页面国际化**
6. ❌ **完成 Research 页面国际化**

### 中期目标（3-4周）

7. ❌ **完成所有主要页面国际化**
8. ❌ **添加翻译遗漏检查脚本**
9. ❌ **创建翻译管理工具**

### 长期目标（未来增强）

10. ❌ **支持更多语言**（日语、韩语等）
11. ❌ **添加 RTL 语言支持**
12. ❌ **实现自动翻译工具集成**

---

## 🔗 相关资源

- **项目路径**: `/Users/berton/Github/DeepTutor/web`
- **翻译文件**: `/Users/berton/Github/DeepTutor/web/lib/i18n.ts`
- **语言切换器**: `/Users/berton/Github/DeepTutor/web/components/LanguageSwitcher.tsx`
- **全局状态**: `/Users/berton/Github/DeepTutor/web/context/GlobalContext.tsx`

---

## 💡 最佳实践

### 1. 翻译键命名

```typescript
// ✅ 推荐：清晰、描述性强
"Generate Ideas": "生成创意",
"Generating ideas...": "正在生成创意...",

// ❌ 避免：模糊、无意义
"action1": "生成",
"loading": "生成中",
```

### 2. 保持一致性

```typescript
// ✅ 统一使用相同术语
"Generate Questions" → "生成题目"
"Generate Ideas" → "生成创意"
"Generate Report" → "生成报告"

// ❌ 避免不一致的翻译
"Generate Questions" → "生成问题"
"Generate Ideas" → "创意生成"
"Generate Report" → "产生报告"
```

### 3. 处理变量

```typescript
// ✅ 使用模板字符串
const message = t("Hello") + ", " + username + "!";

// 或创建动态翻译
t("Welcome user").replace("{user}", username);

// 在翻译文件中
"Welcome user": "欢迎 {user}",
```

### 4. 复数形式

```typescript
// ✅ 根据数量选择翻译
const count = items.length;
const text = count === 1 ? t("1 item") : t(`${count} items`);

// 在翻译文件中
"1 item": "1 个项目",
"2 items": "2 个项目",
// 或使用通用形式
"items": "个项目"
```

---

## ❓ 常见问题

### Q1: 为什么不使用 next-intl？

**答**: 项目已经有一个简单有效的自定义 i18n 实现，使用现有的实现可以：
- 避免引入额外的依赖
- 保持代码简洁
- 更好地控制翻译逻辑
- 减少包体积

### Q2: 如何添加新的语言？

**答**:
1. 在 `lib/i18n.ts` 中添加新的语言对象
2. 更新 `Language` 类型定义
3. 在 `LanguageSwitcher.tsx` 中添加新语言的切换逻辑
4. 为所有现有翻译添加新语言的翻译

### Q3: 翻译缺失会怎样？

**答**: 翻译函数 `getTranslation()` 会回退到返回键名本身，这样：
- 不会出现空白或错误
- 用户能看到原始的英文键名
- 便于发现遗漏的翻译

### Q4: 如何处理动态内容？

**答**:
```typescript
// 方法 1: 字符串拼接
const text = t("Total") + ": " + count;

// 方法 2: 模板替换
const text = t("Total: {count}").replace("{count}", count);

// 方法 3: 多个翻译键
const text = count > 0 ? t("Has items") : t("No items");
```

---

## 📞 联系与支持

如有问题或建议，请：
- 提交 GitHub Issue
- 联系项目维护者
- 参考项目文档

---

*最后更新: 2025年1月4日*
*维护者: DeepTutor 开发团队*
