from dotenv import load_dotenv
import os
from chunking_evaluation.evaluation_framework.base_evaluation import BaseEvaluation
import chromadb.utils.embedding_functions as embedding_functions
from chonkie.chunker.token import TokenChunker
from chonkie.chunker.recursive import RecursiveChunker
from chonkie.types import RecursiveRules
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter

load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize BaseEvaluation
evaluation = BaseEvaluation(
    questions_csv_path='data/questions.csv',
    corpora_id_paths={'sample_document.txt': 'data/sample_document.txt'}
)

# Create an embedding function (using OpenAI as an example)
embedding_func = embedding_functions.OpenAIEmbeddingFunction(
    api_key=API_KEY,
    model_name="text-embedding-3-large"
)

# Create a LangChain recursive chunker
lc_recursive_chunker = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=50
)

# Create a LangChain token chunker
lc_token_chunker = TokenTextSplitter(
    chunk_size=400,
    chunk_overlap=50
)

# # Create a Chonkie recursive chunker
# ck_recursive_chunker = RecursiveChunker(
#     tokenizer="character",
#     chunk_size=400,
#     rules=RecursiveRules(),
#     min_characters_per_chunk=24,
# )

# # Create a Chonkie token chunker
# ck_token_chunker = TokenChunker(
#     chunk_size=400,
#     chunk_overlap=50
# )

chunkers = {
    'LangChain Recursive': lc_recursive_chunker,
    'LangChain Token': lc_token_chunker,
    # 'Chonkie Recursive': ck_recursive_chunker,
    # 'Chonkie Token': ck_token_chunker
}

# Run evaluation
for name, chunker in chunkers.items():
    results = evaluation.run(chunker, embedding_function=embedding_func)

    # Print results
    print("\n=== Evaluation Results ===")
    print(f"Chunker: {name}:")
    print(f"IoU Mean: {results['iou_mean']:.3f}")
    print(f"Recall Mean: {results['recall_mean']:.3f}")
    print(f"Precision Mean: {results['precision_mean']:.3f}")
    print(f"Precision Omega Mean: {results['precision_omega_mean']:.3f}")   


# === Evaluation Results ===
# Chunker: LangChain Recursive:
# IoU Mean: 0.210
# Recall Mean: 0.773
# Precision Mean: 0.229
# Precision Omega Mean: 0.609

# === Evaluation Results ===
# Chunker: LangChain Token:
# IoU Mean: 0.270
# Recall Mean: 1.000
# Precision Mean: 0.270
# Precision Omega Mean: 0.270