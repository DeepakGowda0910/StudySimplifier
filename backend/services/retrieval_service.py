import functools
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.content_chunk import ContentChunk


@functools.lru_cache(maxsize=1)
def _get_embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def _cosine(a: list, b: list) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


async def get_grounding_context(
    db: AsyncSession, course: str, subject: str, chapter: str, query: str, k: int = 4
) -> str:
    """Return the top-k most relevant stored NCERT chunks for this exact chapter, re-ranked
    by embedding similarity to the query (e.g. the tool type + topic). Metadata narrows the
    scope first; the vector search picks the most relevant passages within it."""
    result = await db.execute(
        select(ContentChunk).where(
            ContentChunk.course == course,
            ContentChunk.subject == subject,
            ContentChunk.chapter == chapter,
        )
    )
    rows = result.scalars().all()
    if not rows:
        return ""

    embedder = _get_embedder()
    query_vec = embedder.encode(query).tolist()

    scored = []
    for row in rows:
        chunk_vec = [float(x) for x in row.embedding_json.split(",")]
        score = _cosine(query_vec, chunk_vec)
        scored.append((score, row.content))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_chunks = [content for _, content in scored[:k]]
    return "\n\n".join(top_chunks)
