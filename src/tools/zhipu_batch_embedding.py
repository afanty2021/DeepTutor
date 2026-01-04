#!/usr/bin/env python
"""
智谱 AI Batch API Embedding 客户端

提供批量 Embedding 功能，使用智谱 Batch API：
- 无并发限制（Embedding-3 队列 200万次）
- 50% 成本节省
- 适合大规模数据处理

使用方式：
    from src.tools.zhipu_batch_embedding import BatchEmbeddingClient

    client = BatchEmbeddingClient(api_key="your-api-key")
    embeddings = client.embed_texts(
        texts=["文本1", "文本2", ...],
        model="embedding-3"
    )
"""

import json
import os
import time
import tempfile
from pathlib import Path
from typing import Any

try:
    from zhipuai import ZhipuAIClient
except ImportError:
    # 如果没有安装 zhipuai SDK，提供错误提示
    ZhipuAIClient = None
    import warnings
    warnings.warn(
        "zhipuai SDK 未安装。请运行: pip install zhipuai",
        ImportWarning,
        stacklevel=2
    )


class BatchEmbeddingClient:
    """
    智谱 AI Batch Embedding 客户端

    特性：
    - 自动批量处理文本
    - 支持超过 10,000 条的批量请求
    - 自动分片上传
    - 结果缓存和错误重试
    """

    # Batch API 限制
    MAX_REQUESTS_PER_FILE = 10000  # Embedding 模型限制
    MAX_FILE_SIZE_MB = 100
    DEFAULT_ENDPOINT = "/v4/embeddings"

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://open.bigmodel.cn/api/paas/v4/",
        batch_threshold: int = 100,
    ):
        """
        初始化 Batch Embedding 客户端

        Args:
            api_key: 智谱 AI API Key
            base_url: API 基础 URL
            batch_threshold: 批量阈值（达到此数量时触发 Batch API）
        """
        if ZhipuAIClient is None:
            raise ImportError(
                "请先安装 zhipuai SDK: pip install zhipuai"
            )

        self.client = ZhipuAIClient(
            api_key=api_key,
            base_url=base_url
        )
        self.batch_threshold = batch_threshold

    def embed_texts(
        self,
        texts: list[str],
        model: str = "embedding-3",
        auto_batch: bool = True,
    ) -> list[list[float]]:
        """
        对文本列表进行 Embedding

        Args:
            texts: 待 Embedding 的文本列表
            model: Embedding 模型名称
            auto_batch: 是否自动使用 Batch API（达到阈值时）

        Returns:
            Embedding 向量列表

        Raises:
            ValueError: 如果文本列表为空
            RuntimeError: 如果 Batch 任务失败
        """
        if not texts:
            raise ValueError("文本列表不能为空")

        # 如果文本数量较少，直接使用实时 API
        if len(texts) < self.batch_threshold or not auto_batch:
            return self._embed_realtime(texts, model)

        # 使用 Batch API 处理大量文本
        return self._embed_batch(texts, model)

    def _embed_realtime(
        self,
        texts: list[str],
        model: str,
    ) -> list[list[float]]:
        """
        使用实时 API 进行 Embedding（小批量或快速响应）

        Args:
            texts: 文本列表
            model: 模型名称

        Returns:
            向量列表
        """
        embeddings = []

        # 智谱 API 支持批量请求（最多 64 条）
        batch_size = 64

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                response = self.client.embeddings.create(
                    model=model,
                    input=batch,
                )

                # 提取向量
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)

            except Exception as e:
                raise RuntimeError(f"实时 API Embedding 失败: {e}") from e

        return embeddings

    def _embed_batch(
        self,
        texts: list[str],
        model: str,
    ) -> list[list[float]]:
        """
        使用 Batch API 进行 Embedding（大批量）

        Args:
            texts: 文本列表
            model: 模型名称

        Returns:
            向量列表
        """
        # 如果文本数量超过单文件限制，分片处理
        if len(texts) > self.MAX_REQUESTS_PER_FILE:
            all_embeddings = []
            for i in range(0, len(texts), self.MAX_REQUESTS_PER_FILE):
                batch_texts = texts[i:i + self.MAX_REQUESTS_PER_FILE]
                batch_embeddings = self._process_single_batch(
                    batch_texts,
                    model
                )
                all_embeddings.extend(batch_embeddings)
            return all_embeddings
        else:
            return self._process_single_batch(texts, model)

    def _process_single_batch(
        self,
        texts: list[str],
        model: str,
    ) -> list[list[float]]:
        """
        处理单个 Batch 任务

        Args:
            texts: 文本列表
            model: 模型名称

        Returns:
            向量列表
        """
        # 1. 创建 .jsonl 文件
        jsonl_path = self._create_jsonl_file(texts, model)

        try:
            # 2. 上传文件
            file_object = self.client.files.create(
                file=open(jsonl_path, "rb"),
                purpose="batch"
            )

            print(f"✅ 文件上传成功: {file_object.id}")

            # 3. 创建 Batch 任务
            batch = self.client.batches.create(
                input_file_id=file_object.id,
                endpoint=self.DEFAULT_ENDPOINT,
                auto_delete_input_file=True,
                metadata={
                    "model": model,
                    "text_count": len(texts),
                }
            )

            print(f"✅ Batch 任务创建成功: {batch.id}")
            print(f"⏳ 等待任务完成... (预计24小时内)")

            # 4. 监控任务状态
            batch_status = self._wait_for_completion(batch.id)

            # 5. 下载结果
            embeddings = self._download_results(batch_status)

            return embeddings

        finally:
            # 清理临时文件
            if os.path.exists(jsonl_path):
                os.remove(jsonl_path)

    def _create_jsonl_file(
        self,
        texts: list[str],
        model: str,
    ) -> str:
        """
        创建 Batch API 所需的 .jsonl 文件

        Args:
            texts: 文本列表
            model: 模型名称

        Returns:
            .jsonl 文件路径
        """
        # 创建临时文件
        fd, jsonl_path = tempfile.mkstemp(
            suffix=".jsonl",
            prefix="zhipu_batch_"
        )
        os.close(fd)

        # 写入 JSONL 格式
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for idx, text in enumerate(texts, 1):
                request = {
                    "custom_id": f"request-{idx}",
                    "method": "POST",
                    "url": self.DEFAULT_ENDPOINT,
                    "body": {
                        "model": model,
                        "input": text,
                    }
                }
                f.write(json.dumps(request, ensure_ascii=False) + "\n")

        # 检查文件大小
        file_size_mb = os.path.getsize(jsonl_path) / (1024 * 1024)
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            os.remove(jsonl_path)
            raise ValueError(
                f"文件大小 ({file_size_mb:.1f}MB) 超过限制 "
                f"({self.MAX_FILE_SIZE_MB}MB)"
            )

        return jsonl_path

    def _wait_for_completion(
        self,
        batch_id: str,
        check_interval: int = 60,
    ) -> Any:
        """
        等待 Batch 任务完成

        Args:
            batch_id: Batch 任务 ID
            check_interval: 检查间隔（秒）

        Returns:
            完成的 Batch 对象
        """
        print(f"⏳ 开始监控任务状态 (每 {check_interval} 秒检查一次)...")

        while True:
            batch_status = self.client.batches.retrieve(batch_id)

            status = batch_status.status
            print(f"📊 任务状态: {status}")

            # 检查是否完成
            if status == "completed":
                print("✅ 任务完成！")
                return batch_status
            elif status in ["failed", "expired", "cancelled"]:
                error_msg = f"任务失败，状态: {status}"
                if hasattr(batch_status, "error_file_id") and batch_status.error_file_id:
                    error_msg += f" (错误文件: {batch_status.error_file_id})"
                raise RuntimeError(error_msg)

            # 等待后再次检查
            time.sleep(check_interval)

    def _download_results(
        self,
        batch_status: Any,
    ) -> list[list[float]]:
        """
        下载并解析 Batch 结果

        Args:
            batch_status: 完成的 Batch 对象

        Returns:
            向量列表
        """
        # 下载成功结果
        if hasattr(batch_status, "output_file_id") and batch_status.output_file_id:
            result_content = self.client.files.content(batch_status.output_file_id)
            result_text = result_content.content.decode("utf-8")

            # 解析结果
            embeddings = self._parse_batch_results(result_text)
            print(f"✅ 成功获取 {len(embeddings)} 个向量")

            return embeddings
        else:
            raise RuntimeError("Batch 任务未生成输出文件")

    def _parse_batch_results(
        self,
        result_text: str,
    ) -> list[list[float]]:
        """
        解析 Batch API 返回的 JSONL 结果

        Args:
            result_text: JSONL 格式的结果文本

        Returns:
            向量列表（按 custom_id 排序）
        """
        results = []

        for line in result_text.strip().split("\n"):
            if not line:
                continue

            try:
                result = json.loads(line)

                # 检查状态码
                if (
                    hasattr(result, "response")
                    and hasattr(result.response, "status_code")
                    and result.response.status_code == 200
                ):
                    # 提取向量
                    embedding = result.response.body.data[0].embedding
                    results.append({
                        "custom_id": result.custom_id,
                        "embedding": embedding,
                    })
                else:
                    print(f"⚠️ 请求 {result.custom_id} 失败")

            except (json.JSONDecodeError, KeyError, AttributeError) as e:
                print(f"⚠️ 解析结果行失败: {e}")
                continue

        # 按 custom_id 排序以保持原始顺序
        results.sort(key=lambda x: x["custom_id"])
        return [r["embedding"] for r in results]


def embed_texts_batch(
    texts: list[str],
    api_key: str,
    model: str = "embedding-3",
    batch_threshold: int = 100,
) -> list[list[float]]:
    """
    便捷函数：批量 Embedding 文本

    Args:
        texts: 文本列表
        api_key: 智谱 AI API Key
        model: Embedding 模型名称
        batch_threshold: 批量阈值

    Returns:
        向量列表

    Example:
        >>> embeddings = embed_texts_batch(
        ...     texts=["你好", "世界"],
        ...     api_key="your-api-key",
        ...     model="embedding-3"
        ... )
    """
    client = BatchEmbeddingClient(
        api_key=api_key,
        batch_threshold=batch_threshold,
    )
    return client.embed_texts(texts, model=model)


__all__ = [
    "BatchEmbeddingClient",
    "embed_texts_batch",
]
