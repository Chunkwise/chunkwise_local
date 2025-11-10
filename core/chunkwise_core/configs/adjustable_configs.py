adjustable_configs = [
    {
        "name": "Chonkie Token",
        "chunk_size": {"default": 2048, "min": 1, "max": 8192},
        "chunk_overlap": {"default": 0, "min": 0, "max": 4086},
    },
    {
        "name": "Chonkie Sentence",
        "chunk_size": {"default": 2048, "min": 1, "max": 8192},
        "chunk_overlap": {"default": 0, "min": 0, "max": 4086},
        "min_sentences_per_chunk": {
            "default": 1,
            "min": 1,
            "max": 100,
        },
        "min_characters_per_sentence": {
            "default": 12,
            "min": 1,
            "max": 100,
        },
    },
    {
        "name": "Chonkie Recursive",
        "chunk_size": {"default": 2048, "min": 1, "max": 8192},
        "min_characters_per_chunk": {
            "default": 24,
            "min": 1,
            "max": 100,
        },
    },
    {
        "name": "Chonkie Slumber",
        "chunk_size": {"default": 2048, "min": 1, "max": 8192},
        "min_characters_per_chunk": {
            "default": 24,
            "min": 1,
            "max": 100,
        },
    },
    {
        "name": "Chonkie Semantic",
        "chunk_size": {"default": 2048, "min": 1, "max": 8192},
        "threshold": {"default": 0.8, "min": 0, "max": 1},
        "similarity_window": {"default": 3, "min": 1, "max": 100},
        "min_sentences_per_chunk": {
            "default": 1,
            "min": 1,
            "max": 100,
        },
        "min_characters_per_sentence": {
            "default": 12,
            "min": 1,
            "max": 100,
        },
    },
    {
        "name": "LangChain Token",
        "chunk_size": {"default": 2048, "min": 1, "max": 8192},
        "chunk_overlap": {"default": 0, "min": 0, "max": 4086},
    },
    {
        "name": "LangChain Recursive",
        "chunk_size": {"default": 2048, "min": 1, "max": 8192},
        "chunk_overlap": {"default": 0, "min": 0, "max": 4086},
    },
    {
        "name": "LangChain Character",
        "chunk_size": {"default": 2048, "min": 1, "max": 8192},
        "chunk_overlap": {"default": 0, "min": 0, "max": 4086},
    },
]
