from llama_index.vector_stores.postgres import PGVectorStore
from config.Config import config


class VectorStoreSingleton:
    _instances = {}

    @classmethod
    def get_instance(cls, db_table):
        if db_table not in cls._instances:
            cls._instances[db_table] = PGVectorStore.from_params(
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                table_name=db_table,
                embed_dim=config.EMBEDDING_DIM,
                hnsw_kwargs={
                    "hnsw_m": 16,
                    "hnsw_ef_construction": 64,
                    "hnsw_ef_search": 40,
                    "hnsw_dist_method": "vector_cosine_ops",
                },
            )
        return cls._instances[db_table]
