def calculate_chunk_stats(chunks):
    try:
        if not isinstance(chunks, list):
            raise ValueError("chunks must be a list")

        stats = {
            "total_chunks": len(chunks),
        }
        total_chars = 0

        for i, chunk in enumerate(chunks):
            # Validate chunk has a non-empty text field
            if not isinstance(chunk, dict) or "text" not in chunk:
                raise ValueError(f"Chunk at index {i} is missing the 'text' property")
            if not isinstance(chunk["text"], str) or len(chunk["text"]) == 0:
                raise ValueError(f"Chunk at index {i} has empty 'text'")

            text_len = len(chunk["text"])
            total_chars += text_len

            if (not stats.get("largest_char_count")) or (
                text_len > stats["largest_char_count"]
            ):
                stats["largest_char_count"] = text_len
                stats["largest_text"] = chunk["text"]

            if (not stats.get("smallest_char_count")) or (
                text_len < stats["smallest_char_count"]
            ):
                stats["smallest_char_count"] = text_len
                stats["smallest_text"] = chunk["text"]

        stats["avg_chars"] = (
            total_chars / stats["total_chunks"] if stats["total_chunks"] > 0 else 0
        )

        return stats

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid input")
