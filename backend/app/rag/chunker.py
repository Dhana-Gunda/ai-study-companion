import re
from typing import List, Dict, Any

class TranscriptChunker:
    """Dialogue-aware transcript chunker preserving speaker attribution and timestamps."""

    def __init__(self, target_chunk_size: int = 600, overlap: int = 100):
        self.target_chunk_size = target_chunk_size # in words (~750 tokens)
        self.overlap = overlap

    def chunk_transcript(
        self,
        text: str,
        episode_title: str,
        guest_name: str,
        episode_slug: str
    ) -> List[Dict[str, Any]]:
        # Split text into paragraphs or speaker turns
        paragraphs = re.split(r'\n\s*\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        chunks = []
        current_chunk_words = []
        current_timestamp = None
        chunk_idx = 0

        timestamp_regex = re.compile(r'\(?(\d{1,2}:\d{2}(?::\d{2})?)\)?')

        for para in paragraphs:
            # Check for timestamp in paragraph
            ts_match = timestamp_regex.search(para)
            if ts_match and not current_timestamp:
                current_timestamp = ts_match.group(1)

            para_words = para.split()
            if len(current_chunk_words) + len(para_words) > self.target_chunk_size and current_chunk_words:
                # Flush current chunk
                chunk_body = " ".join(current_chunk_words)
                token_count = int(len(current_chunk_words) * 1.3) # Approximate tokens
                
                # Context prefix
                prefix = f"[Episode: {episode_title} | Guest: {guest_name}"
                if current_timestamp:
                    prefix += f" | Timestamp: {current_timestamp}"
                prefix += "]\n"

                chunks.append({
                    "episode_slug": episode_slug,
                    "episode_title": episode_title,
                    "guest_name": guest_name,
                    "timestamp_ref": current_timestamp or "General Discussion",
                    "chunk_index": chunk_idx,
                    "chunk_text": prefix + chunk_body,
                    "token_count": token_count
                })
                chunk_idx += 1

                # Keep overlap from the end of current chunk
                overlap_words = current_chunk_words[-self.overlap:] if len(current_chunk_words) > self.overlap else current_chunk_words
                current_chunk_words = list(overlap_words) + para_words
                # Reset timestamp for next block
                current_timestamp = ts_match.group(1) if ts_match else None
            else:
                current_chunk_words.extend(para_words)

        # Flush any remaining words
        if current_chunk_words:
            chunk_body = " ".join(current_chunk_words)
            token_count = int(len(current_chunk_words) * 1.3)
            prefix = f"[Episode: {episode_title} | Guest: {guest_name}"
            if current_timestamp:
                prefix += f" | Timestamp: {current_timestamp}"
            prefix += "]\n"

            chunks.append({
                "episode_slug": episode_slug,
                "episode_title": episode_title,
                "guest_name": guest_name,
                "timestamp_ref": current_timestamp or "General Discussion",
                "chunk_index": chunk_idx,
                "chunk_text": prefix + chunk_body,
                "token_count": token_count
            })

        return chunks

chunker = TranscriptChunker()
