"""一次性探针：直接看 Milvus 里某 query 的 top-k 真实相似度分数和命中文本。

不走 RAG chain，绕开 LLM 兜底话术的干扰。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pymilvus import MilvusClient

from app.utils.embeddings import DashScopeCompatibleEmbeddings
from config.settings import settings


def main():
    embeddings = DashScopeCompatibleEmbeddings()
    client = MilvusClient(uri=settings.MILVUS_URI, db_name=settings.MILVUS_DB)

    print(f"Milvus: {settings.MILVUS_URI} / {settings.MILVUS_DB}.{settings.MILVUS_COLLECTION}")
    print(f"Collection: {client.get_collection_stats(collection_name=settings.MILVUS_COLLECTION)}")

    for q in ["嘉瑟宜是什么", "嘉瑟宜", "嘉瑟宜 坎地沙坦酯", "嘉瑟宜 高血压"]:
        print("\n" + "=" * 80)
        print(f"QUERY: {q!r}")
        v = embeddings.embed_query(q)
        res = client.search(
            collection_name=settings.MILVUS_COLLECTION,
            data=[v],
            limit=5,
            output_fields=["text", "source"],
        )
        hits = res[0] if res else []
        if not hits:
            print("  (no hits)")
            continue
        for i, h in enumerate(hits):
            score = h.get("distance") or h.get("score")
            text = h["entity"].get("text", "")
            source = h["entity"].get("source", "")
            snippet = text[:120].replace("\n", " ")
            print(f"  #{i+1}  score={score:.4f}  source={source}")
            print(f"        text: {snippet}…")

    print("\n" + "=" * 80)
    print("整库扫 '嘉瑟宜' 是否真在库中（用 query + expr 验证）")
    try:
        expr_res = client.query(
            collection_name=settings.MILVUS_COLLECTION,
            filter='text like "%嘉瑟宜%"',
            output_fields=["text", "source"],
            limit=5,
        )
        print(f"  命中 {len(expr_res)} 条")
        for r in expr_res[:5]:
            print(f"    source={r['source']!r}")
            print(f"    text  ={r['text'][:120].replace(chr(10), ' ')}…")
    except Exception as e:
        print(f"  expr 查询失败: {e}")


if __name__ == "__main__":
    main()