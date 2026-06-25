import sys
from pathlib import Path

# 允许从项目根或 AI_disease_backend/ 跑都能 import config
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pymilvus import MilvusClient, DataType
from config.settings import settings

DB_NAME = settings.MILVUS_DB
COLLECTION_NAME = settings.MILVUS_COLLECTION

# 危险操作：drop_collection 之前必须人工确认（CLAUDE.md 红线）
if not (len(sys.argv) > 1 and sys.argv[1] == "--yes"):
    confirm = input(
        f"[危险] 将连接到 {settings.MILVUS_URI} 并 drop collection "
        f"'{DB_NAME}.{COLLECTION_NAME}'，确认请输入 YES: "
    )
    if confirm != "YES":
        print("已取消，未执行任何操作。")
        sys.exit(0)

client = MilvusClient(uri=settings.MILVUS_URI)
if DB_NAME not in client.list_databases():
    client.create_database(DB_NAME)
client.use_database(DB_NAME)
if client.has_collection(COLLECTION_NAME):
    client.drop_collection(COLLECTION_NAME)

#  1 创建 schema
schema = MilvusClient.create_schema(
    auto_id=True,
    enable_dynamic_field=True,
)
##  1.1 把字段加入到schema
schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=65535)
# 2 设置索引参数【可选】
index_params = client.prepare_index_params()
index_params.add_index(
    field_name="vector",
    index_type="AUTOINDEX",
    metric_type="COSINE" # 用余弦相似度计算向量相似度
)


# 3 创建集合
client.create_collection(
    collection_name=COLLECTION_NAME,
    schema=schema,
    index_params=index_params
)

res = client.get_load_state(
    collection_name=COLLECTION_NAME
)

print(res)