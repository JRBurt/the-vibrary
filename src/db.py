import psycopg
from pgvector.psycopg import register_vector

from src.config import DATABASE_URL, EMBEDDING_DIM

SCHEMA = f"""
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    id BIGSERIAL PRIMARY KEY,
    collection TEXT NOT NULL,
    source_path TEXT NOT NULL,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR({EMBEDDING_DIM}) NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source_path, chunk_index)
);

CREATE INDEX IF NOT EXISTS chunks_collection_idx ON chunks (collection);
CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks USING hnsw (embedding vector_cosine_ops);
"""


def get_connection() -> psycopg.Connection:
    conn = psycopg.connect(DATABASE_URL, autocommit=True)
    register_vector(conn)
    return conn


def init_schema() -> None:
    # CREATE EXTENSION must run before register_vector can look up the
    # "vector" type, so this connection skips registration.
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        conn.execute(SCHEMA)


def delete_source(conn: psycopg.Connection, source_path: str) -> None:
    conn.execute("DELETE FROM chunks WHERE source_path = %s", (source_path,))


def insert_chunks(
    conn: psycopg.Connection,
    collection: str,
    source_path: str,
    chunks: list[str],
    embeddings: list[list[float]],
) -> None:
    with conn.cursor() as cur:
        for i, (content, embedding) in enumerate(zip(chunks, embeddings)):
            cur.execute(
                """
                INSERT INTO chunks (collection, source_path, chunk_index, content, embedding)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (source_path, chunk_index)
                DO UPDATE SET content = EXCLUDED.content,
                              embedding = EXCLUDED.embedding,
                              updated_at = now()
                """,
                (collection, source_path, i, content, embedding),
            )


def search(
    conn: psycopg.Connection,
    query_embedding: list[float],
    collection: str | None = None,
    top_k: int = 5,
) -> list[dict]:
    if collection:
        rows = conn.execute(
            """
            SELECT collection, source_path, chunk_index, content,
                   1 - (embedding <=> %s::vector) AS score
            FROM chunks
            WHERE collection = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (query_embedding, collection, query_embedding, top_k),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT collection, source_path, chunk_index, content,
                   1 - (embedding <=> %s::vector) AS score
            FROM chunks
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (query_embedding, query_embedding, top_k),
        ).fetchall()

    return [
        {
            "collection": r[0],
            "source_path": r[1],
            "chunk_index": r[2],
            "content": r[3],
            "score": float(r[4]),
        }
        for r in rows
    ]


def list_collections(conn: psycopg.Connection) -> list[str]:
    rows = conn.execute("SELECT DISTINCT collection FROM chunks ORDER BY collection").fetchall()
    return [r[0] for r in rows]
