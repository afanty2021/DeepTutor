#!/bin/bash
# ============================================================================
# Demo 知识库重新初始化脚本 - 使用 BGE-M3
# ============================================================================
# 此脚本将：
# 1. 删除旧的 Demo 知识库
# 2. 下载 Demo 数据包
# 3. 使用 BGE-M3 重新初始化
# ============================================================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "Demo 知识库重新初始化 - BGE-M3 版本"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ============================================================================
# Step 1: 检查环境
# ============================================================================
echo -e "${YELLOW}Step 1: 检查环境${NC}"
echo "----------------------------------------"

# 检查 Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 已安装${NC}"

# 检查 Ollama
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${RED}❌ Ollama 未运行${NC}"
    echo "请先启动 Ollama: ollama serve"
    exit 1
fi
echo -e "${GREEN}✅ Ollama 正在运行${NC}"

# 检查 BGE-M3 模型
if ! curl -s http://localhost:11434/api/tags | grep -q "bge-m3"; then
    echo -e "${YELLOW}⚠️  BGE-M3 模型未下载${NC}"
    echo "正在下载 BGE-M3..."
    ollama pull bge-m3:v2
    echo -e "${GREEN}✅ BGE-M3 下载完成${NC}"
else
    echo -e "${GREEN}✅ BGE-M3 模型已存在${NC}"
fi

echo ""

# ============================================================================
# Step 2: 删除旧的 Demo 知识库
# ============================================================================
echo -e "${YELLOW}Step 2: 清理旧的 Demo 知识库${NC}"
echo "----------------------------------------"

DEMO_DIR="./data/knowledge_bases"

# 删除旧的 Demo 知识库
if [ -d "$DEMO_DIR/ai_textbook" ]; then
    echo "删除旧的 ai_textbook 知识库..."
    rm -rf "$DEMO_DIR/ai_textbook"
    echo -e "${GREEN}✅ ai_textbook 已删除${NC}"
fi

if [ -d "$DEMO_DIR/research_papers" ]; then
    echo "删除旧的研究论文知识库..."
    rm -rf "$DEMO_DIR/research_papers"
    echo -e "${GREEN}✅ research_papers 已删除${NC}"
fi

echo ""

# ============================================================================
# Step 3: 下载 Demo 数据包
# ============================================================================
echo -e "${YELLOW}Step 3: 下载 Demo 数据包${NC}"
echo "----------------------------------------"

DEMO_ARCHIVE="./demo_data.zip"

if [ -f "$DEMO_ARCHIVE" ]; then
    echo -e "${YELLOW}⚠️  Demo 数据包已存在${NC}"
    read -p "是否重新下载? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "$DEMO_ARCHIVE"
    else
        echo "使用现有数据包"
    fi
fi

if [ ! -f "$DEMO_ARCHIVE" ]; then
    echo "Demo 数据包下载地址："
    echo "https://drive.google.com/drive/folders/1iWwfZXiTuQKQqUYb5fGDZjLCeTUP6DA6?usp=sharing"
    echo ""
    echo -e "${YELLOW}请手动下载并解压到 data/ 目录${NC}"
    echo ""
    echo "步骤："
    echo "1. 访问上面的 Google Drive 链接"
    echo "2. 下载 demo_data.zip"
    echo "3. 解压到项目根目录，得到 data/ 文件夹"
    echo "4. 运行此脚本继续"
    echo ""
    read -p "下载完成后按 Enter 继续..."
fi

# 检查 Demo 数据是否存在
if [ ! -d "./data/knowledge_bases/ai_textbook" ] && [ ! -d "./data/knowledge_bases/research_papers" ]; then
    echo -e "${RED}❌ 未找到 Demo 数据${NC}"
    echo "请确保已将 Demo 数据解压到 data/knowledge_bases/ 目录"
    exit 1
fi

echo -e "${GREEN}✅ Demo 数据已就绪${NC}"
echo ""

# ============================================================================
# Step 4: 重新初始化知识库
# ============================================================================
echo -e "${YELLOW}Step 4: 使用 BGE-M3 初始化知识库${NC}"
echo "----------------------------------------"

# 初始化 ai_textbook
if [ -d "./data/knowledge_bases/ai_textbook" ]; then
    echo "初始化 ai_textbook 知识库..."
    python -m src.knowledge.start_kb init ai_textbook --force
    echo -e "${GREEN}✅ ai_textbook 初始化完成${NC}"
fi

# 初始化 research_papers
if [ -d "./data/knowledge_bases/research_papers" ]; then
    echo "初始化 research_papers 知识库..."
    python -m src.knowledge.start_kb init research_papers --force
    echo -e "${GREEN}✅ research_papers 初始化完成${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Demo 知识库初始化完成！${NC}"
echo "=========================================="
echo ""
echo "知识库信息："
python -m src.knowledge.start_kb list
echo ""
echo "现在可以启动服务："
echo "  python scripts/start_web.py"
echo ""
