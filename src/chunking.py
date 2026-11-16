def chunk_markdown(text: str, target_words: int = 200, overlap_words: int = 40) -> list[str]:
    """Split markdown into overlapping chunks along paragraph breaks.

    Paragraph-based rather than char-based so a chunk boundary doesn't land
    mid-sentence; overlap keeps a sentence near a boundary from losing
    context on either side.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_words = 0

    for paragraph in paragraphs:
        paragraph_words = paragraph.split()
        current.append(paragraph)
        current_words += len(paragraph_words)

        if current_words >= target_words:
            chunks.append("\n\n".join(current))
            overlap: list[str] = []
            overlap_count = 0
            for p in reversed(current):
                words = p.split()
                overlap.insert(0, p)
                overlap_count += len(words)
                if overlap_count >= overlap_words:
                    break
            current = overlap
            current_words = overlap_count

    if current and current_words > 0:
        chunks.append("\n\n".join(current))

    return chunks
