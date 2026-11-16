"""Walk VIBRARY_DATA_DIR/<collection>/**/*.md, chunk, embed, and upsert into pgvector.

Usage:
    python -m src.ingest

Re-running after editing a file re-embeds and replaces that file's chunks
(delete-then-insert), so stale content never lingers in the index.
"""

from src import db
from src.chunking import chunk_markdown
from src.config import DATA_DIR
from src.embeddings import embed


def ingest() -> None:
    db.init_schema()

    if not DATA_DIR.exists():
        print(f"No data directory at {DATA_DIR}, nothing to ingest.")
        return

    with db.get_connection() as conn:
        for collection_dir in sorted(p for p in DATA_DIR.iterdir() if p.is_dir()):
            collection = collection_dir.name
            md_files = sorted(collection_dir.rglob("*.md"))

            for md_file in md_files:
                source_path = str(md_file.relative_to(DATA_DIR))
                text = md_file.read_text(encoding="utf-8")
                chunks = chunk_markdown(text)

                if not chunks:
                    continue

                vectors = embed(chunks)

                db.delete_source(conn, source_path)
                db.insert_chunks(conn, collection, source_path, chunks, vectors)

                print(f"[{collection}] {source_path}: {len(chunks)} chunks")


if __name__ == "__main__":
    ingest()
