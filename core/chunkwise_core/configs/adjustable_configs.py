adjustable_configs = [
    {
        "name": "Chonkie Token",
        "chunk_size": {"type": "int", "default": 2048, "min": 1, "max": 8192},
        "chunk_overlap": {"type": "int", "default": 0, "min": 0, "max": 8192},
    },
    {
        "name": "Chonkie Recursive",
        "chunk_size": {"type": "int", "default": 2048, "min": 1, "max": 8192},
        "min_characters_per_chunk": {
            "type": "int",
            "default": 24,
            "min": 1,
            "max": 8192,
        },
    },
    {
        "name": "LangChain Token",
        "chunk_size": {"type": "int", "default": 2048, "min": 1, "max": 8192},
        "chunk_overlap": {"type": "int", "default": 0, "min": 0, "max": 8192},
    },
    {
        "name": "LangChain Recursive",
        "chunk_size": {"type": "int", "default": 2048, "min": 1, "max": 8192},
        "chunk_overlap": {"type": "int", "default": 0, "min": 0, "max": 8192},
    },
]
