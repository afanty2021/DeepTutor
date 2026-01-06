# DeepTutor 国际化快速使用指南

## 🚀 用户使用指南

### 如何切换语言

1. **在 Sidebar 中切换**
   - 找到左侧边栏顶部的语言切换器（显示 "EN" 或 "中文"）
   - 点击按钮即可切换
   - 切换后立即生效，无需刷新页面

2. **在设置中切换**
   - 导航到 "Settings"（设置）页面
   - 在 "Interface Preferences"（界面偏好）部分
   - 选择 "Language"（语言）：English 或 Chinese

### 默认语言

- 首次访问默认为英语
- 语言设置会自动保存
- 下次访问时保持您的选择

---

## 👨‍💻 开发者快速指南

### 为页面添加国际化

**3 步完成**：

#### 1. 导入依赖
```tsx
import { useGlobal } from "@/context/GlobalContext";
import { getTranslation } from "@/lib/i18n";
```

#### 2. 添加翻译函数
```tsx
export default function MyPage() {
  const { uiSettings } = useGlobal();
  const t = (key: string) => getTranslation(uiSettings.language, key);
```

#### 3. 替换文本
```tsx
// 之前
<h1>Welcome</h1>
<button>Submit</button>

// 之后
<h1>{t("Welcome")}</h1>
<button>{t("Submit")}</button>
```

### 添加新翻译

在 `/web/lib/i18n.ts` 中添加：

```typescript
export const translations = {
  en: {
    "My New Text": "My New Text",
  },
  zh: {
    "My New Text": "我的新文本",
  },
};
```

---

## 📋 已翻译的页面

| 页面 | 状态 | 翻译条目 |
|------|------|---------|
| Sidebar | ✅ 完成 | 15 |
| Dashboard | ✅ 完成 | 25 |
| Settings | ✅ 完成 | 50 |
| Solver | ⚠️ 部分 | 30 |
| Question | ⏳ 待完成 | 40 |
| Research | ⏳ 待完成 | 40 |
| Guide | ⏳ 待完成 | 30 |
| Co-Writer | ⏳ 待完成 | 25 |
| IdeaGen | ⏳ 待完成 | 25 |
| Notebook | ⏳ 待完成 | 25 |
| Knowledge | ⏳ 待完成 | 30 |

---

## 🔗 相关文件

- **翻译文件**: `/web/lib/i18n.ts`
- **语言切换器**: `/web/components/LanguageSwitcher.tsx`
- **实施指南**: `/web/docs/I18N_IMPLEMENTATION_GUIDE.md`
- **总结报告**: `/web/docs/I18N_SUMMARY.md`

---

## 💡 提示

### 翻译键命名规范

✅ **推荐**:
- "Generate Ideas": "生成创意"
- "Smart Solver": "智能解题"
- "Loading...": "加载中..."

❌ **避免**:
- "btn1": "生成"
- "txt": "文本"
- "loading": "加载中"

### 常用翻译

```typescript
// 通用操作
"Save": "保存"
"Cancel": "取消"
"Delete": "删除"
"Edit": "编辑"
"Create": "创建"
"Search": "搜索"
"Loading": "加载中..."
"Success": "成功"
"Error": "错误"

// 导航
"Dashboard": "仪表盘"
"Settings": "设置"
"Notebooks": "笔记本"
"Knowledge Bases": "知识库"
```

---

## 🧪 测试

启动开发服务器：
```bash
cd /Users/berton/Github/DeepTutor/web
npm run dev
```

访问：http://localhost:3000

测试步骤：
1. 点击语言切换器
2. 验证文本正确切换
3. 刷新页面，验证设置保持

---

*最后更新: 2025年1月4日*
