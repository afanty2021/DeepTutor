#!/usr/bin/env python
"""
重新处理剩余文档并插入到 LightRAG

处理 chapter7, chapter8, raganything, videorag 这 4 个文档
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

load_dotenv(dotenv_path=".env", override=False)

from src.core.logging import LightRAGLogContext, get_logger
from src.core.core import get_embedding_config, get_llm_config, get_vision_config

logger = get_logger("ReprocessDocs")

# 导入 RAGAnything
try:
    from raganything import RAGAnything, RAGAnythingConfig
except ImportError:
    raganything_path = project_root.parent / "rag-anything"
    if raganything_path.exists():
        sys.path.insert(0, str(raganything_path))
        from raganything import RAGAnything, RAGAnythingConfig
    else:
        logger.error("❌ RAGAnything not found!")
        sys.exit(1)


async def main():
    """主处理函数"""
    kb_name = "my_kb"
    kb_dir = Path("data/knowledge_bases") / kb_name

    if not kb_dir.exists():
        logger.error(f"❌ 知识库不存在: {kb_dir}")
        sys.exit(1)

    # 配置路径
    raw_dir = kb_dir / "raw"
    rag_storage_dir = kb_dir / "rag_storage"
    content_list_dir = kb_dir / "content_list"

    # 确保目录存在
    content_list_dir.mkdir(parents=True, exist_ok=True)

    # 要处理的文档列表
    docs_to_process = [
        "chapter7.pdf",
        "chapter8.pdf",
        "raganything.pdf",
        "videorag.pdf",
    ]

    # 验证文档存在
    existing_docs = []
    for doc_name in docs_to_process:
        doc_path = raw_dir / doc_name
        if doc_path.exists():
            existing_docs.append(doc_path)
            logger.info(f"✓ 找到文档: {doc_name}")
        else:
            logger.warning(f"⚠️ 文档不存在: {doc_name}")

    if not existing_docs:
        logger.error("❌ 没有找到需要处理的文档")
        sys.exit(1)

    logger.info(f"\n🔄 准备处理 {len(existing_docs)} 个文档")

    # 获取配置
    embedding_cfg = get_embedding_config()
    llm_cfg = get_llm_config()
    vision_cfg = get_vision_config()

    # 创建 RAGAnything 配置
    config = RAGAnythingConfig(
        working_dir=str(rag_storage_dir),
        parser_output_dir=str(content_list_dir),
        parse_method="auto",
        max_concurrent_files=1,  # 序列处理避免 API 限制
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
    )

    # API key 和 base URL
    api_key = llm_cfg.get("api_key", "")
    base_url = llm_cfg.get("base_url", "https://api.openai.com/v1")
    model = llm_cfg.get("model", "gpt-4o")

    # 定义 LLM 模型函数
    def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        from lightrag.llm.openai import openai_complete_if_cache
        return openai_complete_if_cache(
            model,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )

    # 定义视觉模型函数
    def vision_model_func(
        prompt,
        system_prompt=None,
        history_messages=[],
        image_data=None,
        messages=None,
        **kwargs,
    ):
        from lightrag.llm.openai import openai_complete_if_cache

        use_vision_model = image_data is not None and vision_cfg
        if use_vision_model:
            model_to_use = vision_cfg.get("model", model)
            api_key_to_use = vision_cfg.get("api_key", api_key)
            base_url_to_use = vision_cfg.get("base_url", base_url)
        else:
            model_to_use = model
            api_key_to_use = api_key
            base_url_to_use = base_url

        if messages:
            clean_kwargs = {
                k: v
                for k, v in kwargs.items()
                if k not in ["messages", "prompt", "system_prompt", "history_messages"]
            }
            return openai_complete_if_cache(
                model_to_use,
                prompt="",
                system_prompt=None,
                history_messages=[],
                messages=messages,
                api_key=api_key_to_use,
                base_url=base_url_to_use,
                **clean_kwargs,
            )

        if image_data:
            clean_kwargs = {
                k: v
                for k, v in kwargs.items()
                if k not in ["messages", "prompt", "system_prompt", "history_messages"]
            }
            return openai_complete_if_cache(
                model_to_use,
                prompt="",
                system_prompt=None,
                history_messages=[],
                messages=[
                    {"role": "system", "content": system_prompt} if system_prompt else None,
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                            },
                        ],
                    } if image_data else {"role": "user", "content": prompt},
                ],
                api_key=api_key_to_use,
                base_url=base_url_to_use,
                **clean_kwargs,
            )
        return llm_model_func(prompt, system_prompt, history_messages, **kwargs)

    # 定义 embedding 函数
    from lightrag.utils import EmbeddingFunc
    embedding_api_key = embedding_cfg.get("api_key", api_key)
    embedding_base_url = embedding_cfg.get("base_url", base_url)
    embedding_func = EmbeddingFunc(
        embedding_dim=embedding_cfg.get("dim", 1536),
        max_token_size=embedding_cfg.get("max_tokens", 8191),
        func=lambda texts: openai_embed.func(
            texts,
            model=embedding_cfg.get("model", "text-embedding-3-small"),
            api_key=embedding_api_key,
            base_url=embedding_base_url,
            embedding_dim=embedding_cfg.get("dim", 1536),
        ),
    )

    # 初始化 RAGAnything
    logger.info("📦 初始化 RAGAnything...")

    with LightRAGLogContext(scene="reprocess_docs"):
        rag = RAGAnything(
            config=config,
            llm_model_func=llm_model_func,
            vision_model_func=vision_model_func,
            embedding_func=embedding_func,
        )

        # 确保加载已有知识库
        logger.info("📦 加载已有知识库...")
        await rag._ensure_lightrag_initialized()
        logger.info("✓ 已加载现有知识库")

        # 处理每个文档
        for idx, doc_path in enumerate(existing_docs, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"🚀 处理文档 [{idx}/{len(existing_docs)}]: {doc_path.name}")
            logger.info(f"{'='*60}")

            try:
                # 使用 process_document_complete 完整处理文档
                await rag.process_document_complete(
                    file_path=str(doc_path),
                    output_dir=str(content_list_dir),
                    parse_method="auto",
                )

                logger.info(f"✅ 成功处理: {doc_path.name}")

            except Exception as e:
                logger.error(f"❌ 处理失败 {doc_path.name}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                continue

        logger.info(f"\n{'='*60}")
        logger.info("✅ 所有文档处理完成!")
        logger.info(f"{'='*60}")


if __name__ == "__main__":
    with LightRAGLogContext():
        asyncio.run(main())
