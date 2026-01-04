#!/usr/bin/env python
"""
智谱 Batch API Embedding 包装器

提供与 LightRAG 兼容的 embedding 函数，支持：
1. 实时 API 模式（小批量）
2. Batch API 模式（大批量，无并发限制，50% 成本节省）

使用方式：
    from src.tools.zhipu_batch_embedding_wrapper import batch_embed_func

    # 使用 Batch API
    embedding_func = batch_embed_func(
        embedding_dim=2048,
        api_key="your-api-key",
        model="embedding-3",
        use_batch=True,  # 启用 Batch 模式
        batch_threshold=100,  # 超过 100 条文本时使用 Batch
    )

    vectors = embedding_func(["文本1", "文本2", ...])
"""

import os
from typing import Any

from lightrag.utils import EmbeddingFunc
from openai import OpenAI

from src.core.core import get_embedding_config


class BatchEmbeddingWrapper:
    """
    智谱 Batch Embedding 包装器

    提供与 LightRAG EmbeddingFunc 兼容的接口，自动选择：
    - 实时 API：文本数量 < batch_threshold
    - Batch API：文本数量 >= batch_threshold
    """

    def __init__(
        self,
        embedding_dim: int,
        api_key: str,
        base_url: str,
        model: str,
        max_token_size: int = 8192,
        use_batch: bool = True,
        batch_threshold: int = 100,
    ):
        """
        初始化 Batch Embedding 包装器

        Args:
            embedding_dim: Embedding 向量维度
            api_key: 智谱 AI API Key
            base_url: API 基础 URL
            model: Embedding 模型名称
            max_token_size: 最大 token 数
            use_batch: 是否启用 Batch API
            batch_threshold: Batch API 触发阈值
        """
        self.embedding_dim = embedding_dim
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.max_token_size = max_token_size
        self.use_batch = use_batch
        self.batch_threshold = batch_threshold

        # 初始化 OpenAI 客户端（用于实时 API）
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        # 延迟导入 Batch API 客户端（仅在需要时）
        self._batch_client = None

    @property
    def batch_client(self):
        """延迟加载 Batch API 客户端"""
        if self._batch_client is None:
            try:
                from src.tools.zhipu_batch_embedding import BatchEmbeddingClient

                self._batch_client = BatchEmbeddingClient(
                    api_key=self.api_key,
                    batch_threshold=self.batch_threshold,
                )
            except ImportError as e:
                print(f"⚠️ 无法导入 Batch API 客户端: {e}")
                print("将使用实时 API 作为备用方案")
                self._batch_client = False  # 标记为不可用
        return self._batch_client

    def __call__(self, texts: list[str]) -> list[list[float]]:
        """
        对文本列表进行 Embedding

        Args:
            texts: 待 Embedding 的文本列表

        Returns:
            向量列表
        """
        # 空列表处理
        if not texts:
            return []

        # 决定使用哪种 API
        use_batch_api = (
            self.use_batch
            and len(texts) >= self.batch_threshold
            and self.batch_client is not False
        )

        if use_batch_api:
            return self._embed_batch(texts)
        else:
            return self._embed_realtime(texts)

    def _embed_realtime(self, texts: list[str]) -> list[list[float]]:
        """使用实时 API 进行 Embedding"""
        embeddings = []

        # 智谱 API 支持批量请求（最多 64 条）
        batch_size = 64

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                )

                # 提取向量
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)

            except Exception as e:
                print(f"⚠️ 实时 API Embedding 失败: {e}")
                # 返回零向量作为备用方案
                embeddings.extend([[0.0] * self.embedding_dim] * len(batch))

        return embeddings

    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        """使用 Batch API 进行 Embedding"""
        if self.batch_client is False:
            # Batch 客户端不可用，回退到实时 API
            print("⚠️ Batch API 不可用，使用实时 API")
            return self._embed_realtime(texts)

        try:
            print(f"📦 使用 Batch API 处理 {len(texts)} 条文本...")
            embeddings = self.batch_client.embed_texts(
                texts=texts,
                model=self.model,
            )
            return embeddings
        except Exception as e:
            print(f"⚠️ Batch API 失败: {e}，回退到实时 API")
            return self._embed_realtime(texts)


def batch_embed_func(
    embedding_dim: int = 2048,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    max_token_size: int = 8192,
    use_batch: bool = True,
    batch_threshold: int = 100,
) -> EmbeddingFunc:
    """
    创建支持 Batch API 的 Embedding 函数

    Args:
        embedding_dim: Embedding 向量维度
        api_key: 智谱 AI API Key（如果为 None，从环境变量读取）
        base_url: API 基础 URL（如果为 None，从环境变量读取）
        model: Embedding 模型名称（如果为 None，从环境变量读取）
        max_token_size: 最大 token 数
        use_batch: 是否启用 Batch API
        batch_threshold: Batch API 触发阈值

    Returns:
        LightRAG 兼容的 EmbeddingFunc 对象

    Example:
        >>> from src.tools.zhipu_batch_embedding_wrapper import batch_embed_func
        >>>
        >>> # 使用 Batch 模式
        >>> embedding_func = batch_embed_func(
        ...     embedding_dim=2048,
        ...     use_batch=True,
        ...     batch_threshold=100,
        ... )
        >>>
        >>> vectors = embedding_func(["文本1", "文本2"])
    """
    # 从环境变量读取配置（如果未提供）
    if api_key is None or base_url is None or model is None:
        config = get_embedding_config()
        if api_key is None:
            api_key = config["api_key"]
        if base_url is None:
            base_url = config["base_url"]
        if model is None:
            model = config["model"]
        if embedding_dim == 2048 and "dim" in config:
            embedding_dim = config["dim"]

    # 创建包装器实例
    wrapper = BatchEmbeddingWrapper(
        embedding_dim=embedding_dim,
        api_key=api_key,
        base_url=base_url,
        model=model,
        max_token_size=max_token_size,
        use_batch=use_batch,
        batch_threshold=batch_threshold,
    )

    # 创建 LightRAG 兼容的 EmbeddingFunc
    return EmbeddingFunc(
        embedding_dim=embedding_dim,
        max_token_size=max_token_size,
        func=wrapper,
    )


def create_embedding_func_from_config(
    config: dict[str, Any],
    use_batch: bool = True,
    batch_threshold: int = 100,
) -> EmbeddingFunc:
    """
    从配置字典创建 Embedding 函数

    Args:
        config: 配置字典（从 get_embedding_config() 获取）
        use_batch: 是否启用 Batch API
        batch_threshold: Batch API 触发阈值

    Returns:
        LightRAG 兼容的 EmbeddingFunc 对象
    """
    return batch_embed_func(
        embedding_dim=config.get("dim", 2048),
        api_key=config.get("api_key"),
        base_url=config.get("base_url"),
        model=config.get("model"),
        max_token_size=config.get("max_tokens", 8192),
        use_batch=use_batch,
        batch_threshold=batch_threshold,
    )


__all__ = [
    "batch_embed_func",
    "create_embedding_func_from_config",
    "BatchEmbeddingWrapper",
]
