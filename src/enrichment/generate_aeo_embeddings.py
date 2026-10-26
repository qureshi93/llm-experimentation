import os

from openai import OpenAI
from pgvector.psycopg import register_vector

from src.db.client import get_pool

MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")  # 1536 dims
BATCH = 50


def run() -> int:
    client = OpenAI()
    total = 0
    with get_pool().connection() as conn:
        register_vector(conn)
        while True:
            rows = conn.execute(
                """SELECT id, raw_scraped_html_text FROM aeo_audits
                   WHERE embeddings IS NULL AND raw_scraped_html_text IS NOT NULL
                     AND raw_scraped_html_text <> '' LIMIT %s""", (BATCH,)).fetchall()
            if not rows:
                return total
            resp = client.embeddings.create(model=MODEL, input=[t[:30000] for _, t in rows])
            for (aid, _), item in zip(rows, resp.data):
                conn.execute("UPDATE aeo_audits SET embeddings = %s WHERE id = %s", (item.embedding, aid))
            conn.commit()
            total += len(rows)


if __name__ == "__main__":
    print(f"embedded {run()} audits")
