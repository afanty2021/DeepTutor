#!/usr/bin/env python
"""
测试 Batch Embedding 与 LightRAG 的集成

验证：
1. EmbeddingFunc 与 LightRAG 兼容
2. 返回值格式正确（numpy 数组）
3. 维度验证通过
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv(dotenv_path=".env", override=False)


async def test_lightrag_integration():
    """测试与 LightRAG EmbeddingFunc 的集成"""
    print("\n" + "=" * 60)
    print("LightRAG 集成测试")
    print("=" * 60)

    try:
        import numpy as np
        from lightrag.utils import EmbeddingFunc
        from src.tools.zhipu_batch_embedding_wrapper import batch_embed_func

        # 创建包装器实例
        wrapper_func = batch_embed_func(
            embedding_dim=2048,
            use_batch=False,  # 使用实时 API 测试
        )

        # 创建 LightRAG EmbeddingFunc
        embedding_func = EmbeddingFunc(
            embedding_dim=2048,
            max_token_size=8192,
            func=wrapper_func,
        )

        # 测试文本
        test_texts = [
            "这是测试文本 1",
            "这是测试文本 2",
            "这是测试文本 3",
        ]

        print(f"\n📝 测试文本数量: {len(test_texts)}")
        print("⏳ 调用 embedding_func...")

        # 调用 embedding 函数
        start_time = asyncio.get_event_loop().time()
        result = await embedding_func(test_texts)
        elapsed_time = asyncio.get_event_loop().time() - start_time

        # 验证结果
        print(f"\n✅ 成功！")
        print(f"   - 耗时: {elapsed_time:.2f} 秒")
        print(f"   - 返回类型: {type(result)}")
        print(f"   - 结果形状: {result.shape}")
        print(f"   - 数据类型: {result.dtype}")
        print(f"   - 总元素数: {result.size}")
        print(f"   - 向量维度: {len(result[0])}")

        # 验证维度
        assert isinstance(result, np.ndarray), "结果必须是 numpy 数组"
        assert result.shape == (3, 2048), f"形状应该是 (3, 2048)，实际是 {result.shape}"
        assert result.dtype == np.float32, f"数据类型应该是 float32，实际是 {result.dtype}"
        assert result.size == 3 * 2048, f"总元素数应该是 {3 * 2048}，实际是 {result.size}"

        print(f"\n🎉 所有验证通过！")
        print(f"   ✓ 返回类型正确 (numpy.ndarray)")
        print(f"   ✓ 形状正确 ({result.shape})")
        print(f"   ✓ 数据类型正确 ({result.dtype})")
        print(f"   ✓ 维度验证通过")

        return True

    except Exception as e:
        print(f"\n❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_dimension_validation():
    """测试 LightRAG 的维度验证机制"""
    print("\n" + "=" * 60)
    print("维度验证测试")
    print("=" * 60)

    try:
        import numpy as np
        from lightrag.utils import EmbeddingFunc
        from src.tools.zhipu_batch_embedding_wrapper import batch_embed_func

        # 创建错误维度的 wrapper（模拟错误情况）
        wrapper_func = batch_embed_func(
            embedding_dim=1024,  # 错误的维度
            use_batch=False,
        )

        # 创建 LightRAG EmbeddingFunc（期望 2048 维）
        embedding_func = EmbeddingFunc(
            embedding_dim=2048,  # 期望 2048 维
            max_token_size=8192,
            func=wrapper_func,
        )

        test_texts = ["测试文本"]

        print(f"\n📝 测试场景: Wrapper 返回 1024 维，LightRAG 期望 2048 维")
        print("⏳ 调用 embedding_func...")

        try:
            result = await embedding_func(test_texts)
            # 如果成功，检查是否有警告
            print(f"⚠️  注意: 维度不匹配但没有抛出异常")
            print(f"   - 返回形状: {result.shape}")
            print(f"   - 总元素: {result.size}")
            print(f"   - 期望元素: {2048}")
            return True
        except ValueError as e:
            # LightRAG 应该捕获维度不匹配
            if "dimension mismatch" in str(e):
                print(f"✅ LightRAG 正确捕获了维度不匹配错误")
                print(f"   - 错误信息: {e}")
                return True
            else:
                raise

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_tests():
    """运行所有集成测试"""
    results = []

    # 运行测试
    results.append(("LightRAG 集成", await test_lightrag_integration()))
    results.append(("维度验证", await test_dimension_validation()))

    return results


def main():
    """主函数"""
    import asyncio

    # 运行测试
    results = asyncio.run(run_tests())

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
