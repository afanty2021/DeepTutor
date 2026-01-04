#!/usr/bin/env python
"""
测试智谱 Batch API Embedding 实现

这个脚本测试：
1. Batch Embedding 客户端基本功能
2. Batch API vs 实时 API 性能对比
3. 不同配置下的行为验证

使用方式:
    # 运行测试
    python tests/test_batch_embedding.py

    # 测试 Batch API（需要 zhipuai SDK）
    python tests/test_batch_embedding.py --test-batch

    # 仅测试实时 API
    python tests/test_batch_embedding.py --test-realtime
"""

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv(dotenv_path=".env", override=False)


def test_batch_embedding_basic():
    """测试 Batch Embedding 基本功能"""
    print("\n" + "=" * 60)
    print("测试 1: Batch Embedding 基本功能")
    print("=" * 60)

    try:
        from src.tools.zhipu_batch_embedding import BatchEmbeddingClient

        api_key = os.getenv("EMBEDDING_BINDING_API_KEY")
        if not api_key:
            print("❌ 错误: 未设置 EMBEDDING_BINDING_API_KEY")
            return False

        client = BatchEmbeddingClient(api_key=api_key)

        # 测试少量文本（应该使用实时 API）
        test_texts = ["测试文本1", "测试文本2", "测试文本3"]

        print(f"\n📝 测试文本数量: {len(test_texts)}")
        print("⏳ 开始 Embedding...")

        start_time = time.time()
        embeddings = client.embed_texts(test_texts, model="embedding-3")
        elapsed_time = time.time() - start_time

        print(f"✅ 成功！")
        print(f"   - 耗时: {elapsed_time:.2f} 秒")
        print(f"   - 向量数量: {len(embeddings)}")
        print(f"   - 向量维度: {len(embeddings[0]) if embeddings else 0}")

        return True

    except ImportError as e:
        print(f"⚠️  跳过: zhipuai SDK 未安装")
        print(f"   安装命令: pip install zhipuai")
        return False
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False


def test_batch_embedding_large():
    """测试大规模 Batch Embedding"""
    print("\n" + "=" * 60)
    print("测试 2: 大规模 Batch Embedding（100+ 文本）")
    print("=" * 60)

    try:
        from src.tools.zhipu_batch_embedding import BatchEmbeddingClient

        api_key = os.getenv("EMBEDDING_BINDING_API_KEY")
        if not api_key:
            print("❌ 错误: 未设置 EMBEDDING_BINDING_API_KEY")
            return False

        client = BatchEmbeddingClient(
            api_key=api_key,
            batch_threshold=100,  # 超过 100 条使用 Batch API
        )

        # 生成测试文本
        test_texts = [
            f"这是测试文本 {i}，用于测试大规模 Batch Embedding 功能。"
            for i in range(1, 151)  # 150 条文本
        ]

        print(f"\n📝 测试文本数量: {len(test_texts)}")
        print("⏳ 开始 Embedding（预计使用 Batch API）...")

        start_time = time.time()
        embeddings = client.embed_texts(test_texts, model="embedding-3")
        elapsed_time = time.time() - start_time

        print(f"✅ 成功！")
        print(f"   - 耗时: {elapsed_time:.2f} 秒")
        print(f"   - 向量数量: {len(embeddings)}")
        print(f"   - 向量维度: {len(embeddings[0]) if embeddings else 0}")
        print(f"   - 平均速度: {len(test_texts) / elapsed_time:.1f} 条/秒")

        return True

    except ImportError as e:
        print(f"⚠️  跳过: zhipuai SDK 未安装")
        return False
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_wrapper_function():
    """测试 Embedding 包装器函数"""
    print("\n" + "=" * 60)
    print("测试 3: Embedding 包装器函数")
    print("=" * 60)

    try:
        import numpy as np
        from src.tools.zhipu_batch_embedding_wrapper import batch_embed_func

        # 创建 embedding 函数
        embedding_func = batch_embed_func(
            embedding_dim=2048,
            use_batch=True,
            batch_threshold=100,
        )

        # 测试少量文本
        test_texts_small = ["测试1", "测试2", "测试3"]
        print(f"\n📝 小批量测试: {len(test_texts_small)} 条文本")

        start_time = time.time()
        embeddings_small = await embedding_func(test_texts_small)
        elapsed_small = time.time() - start_time

        print(f"✅ 小批量成功！")
        print(f"   - 耗时: {elapsed_small:.2f} 秒")
        print(f"   - 向量维度: {len(embeddings_small[0]) if embeddings_small.size > 0 else 0}")

        # 测试大量文本
        test_texts_large = [f"测试文本 {i}" for i in range(1, 101)]
        print(f"\n📝 大批量测试: {len(test_texts_large)} 条文本")

        start_time = time.time()
        embeddings_large = await embedding_func(test_texts_large)
        elapsed_large = time.time() - start_time

        print(f"✅ 大批量成功！")
        print(f"   - 耗时: {elapsed_large:.2f} 秒")
        print(f"   - 向量维度: {len(embeddings_large[0]) if embeddings_large.size > 0 else 0}")

        return True

    except ImportError as e:
        print(f"⚠️  跳过: Batch API 包装器未找到")
        return False
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_realtime_only():
    """测试仅使用实时 API（不使用 Batch API）"""
    print("\n" + "=" * 60)
    print("测试 4: 实时 API 模式（Batch API 禁用）")
    print("=" * 60)

    try:
        import numpy as np
        from src.tools.zhipu_batch_embedding_wrapper import batch_embed_func

        # 创建禁用 Batch API 的函数
        embedding_func = batch_embed_func(
            embedding_dim=2048,
            use_batch=False,  # 禁用 Batch API
        )

        test_texts = ["测试1", "测试2", "测试3", "测试4", "测试5"]
        print(f"\n📝 测试文本数量: {len(test_texts)}")
        print("⚡ 使用实时 API 模式...")

        start_time = time.time()
        embeddings = await embedding_func(test_texts)
        elapsed_time = time.time() - start_time

        print(f"✅ 成功！")
        print(f"   - 耗时: {elapsed_time:.2f} 秒")
        print(f"   - 向量数量: {len(embeddings)}")
        print(f"   - 向量维度: {len(embeddings[0]) if embeddings.size > 0 else 0}")

        return True

    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_tests(args):
    """运行所有测试（异步）"""
    results = []

    # 运行测试
    if args.all or args.test_batch:
        results.append(("Batch Embedding 基本", test_batch_embedding_basic()))
        results.append(("大规模 Batch Embedding", test_batch_embedding_large()))

    if args.all or args.test_realtime:
        results.append(("实时 API 模式", await test_realtime_only()))

    if args.all or args.test_wrapper:
        results.append(("包装器函数", await test_wrapper_function()))

    return results


def main():
    parser = argparse.ArgumentParser(description="测试智谱 Batch API Embedding")
    parser.add_argument(
        "--test-batch",
        action="store_true",
        help="测试 Batch API（需要 zhipuai SDK）",
    )
    parser.add_argument(
        "--test-realtime",
        action="store_true",
        help="仅测试实时 API",
    )
    parser.add_argument(
        "--test-wrapper",
        action="store_true",
        help="测试包装器函数",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="运行所有测试",
    )

    args = parser.parse_args()

    # 默认运行基本测试
    if not any([args.test_batch, args.test_realtime, args.test_wrapper, args.all]):
        args.test_batch = True
        args.test_wrapper = True

    # 运行异步测试
    results = asyncio.run(run_tests(args))

    # 打印测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {test_name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
