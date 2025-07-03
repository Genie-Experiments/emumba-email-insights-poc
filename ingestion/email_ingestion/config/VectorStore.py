from llama_index.vector_stores.postgres import PGVectorStore
import os
from dotenv import load_dotenv
load_dotenv()

class VectorStoreSingleton:
    _instances = {}

    @classmethod
    def get_instance(cls, db_table):
        if db_table not in cls._instances:
            cls._instances[db_table] = PGVectorStore.from_params(
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST'),
                port=int(os.getenv('DB_PORT')),
                database=os.getenv('DB_NAME'),
                table_name=db_table,
                embed_dim=int(os.getenv('EMBEDDING_DIM')),
                hnsw_kwargs={
                    "hnsw_m": 16,
                    "hnsw_ef_construction": 64,
                    "hnsw_ef_search": 40,
                    "hnsw_dist_method": "vector_cosine_ops",
                },
            )
        return cls._instances[db_table]
