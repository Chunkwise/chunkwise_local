adjustable_configs: {
    "ChonkieToken": {
        "chunk_size": {"type": "int", "default": 2048, "min": 1, "max": 8192},
        "chunk_overlap": {"type": "int", "default": 0, "min": 0, "max": 8192},
    },
    "ChonkieRecursive": {
        "chunk_size": {"type": "int", "default": 2048, "min": 1, "max": 8192},
        "min_characters_per_chunk": {
            "type": "int",
            "default": 24,
            "min": 1,
            "max": 8192,
        },
    },
    "LangChainToken": {
        "chunk_size": {"type": "int", "default": 2048, "min": 1, "max": 8192},
        "chunk_overlap": {"type": "int", "default": 0, "min": 0, "max": 8192},
    },
    "LangChainRecursive": {
        "chunk_size": {"type": "int", "default": 2048, "min": 1, "max": 8192},
        "chunk_overlap": {"type": "int", "default": 0, "min": 0, "max": 8192},
    },
}
