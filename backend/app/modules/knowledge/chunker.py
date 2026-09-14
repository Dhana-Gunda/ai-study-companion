from typing import List, Dict, Any

class DocumentChunker:
    """Splits page text into overlapping semantic chunks with strict page provenance."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        chunk_idx = 0

        for page in pages:
            words = page["text"].split()
            if not words:
                continue

            start = 0
            while start < len(words):
                end = min(start + self.chunk_size, len(words))
                chunk_words = words[start:end]
                chunk_text = " ".join(chunk_words)

                chunks.append({
                    "chunk_index": chunk_idx,
                    "page_number": page["page_number"],
                    "content": chunk_text,
                    "token_count": len(chunk_words)
                })
                chunk_idx += 1
                if end == len(words):
                    break
                start += self.chunk_size - self.chunk_overlap

        return chunks
