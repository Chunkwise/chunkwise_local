from dotenv import load_dotenv
import os
import time
from fastapi import FastAPI, Body, HTTPException, UploadFile, File
from typing import List, Dict, Any
from pydantic import BaseModel
from chunking_evaluation.evaluation_framework.base_evaluation import BaseEvaluation
import chromadb.utils.embedding_functions as embedding_functions
from chonkie.chunker.token import TokenChunker
from chonkie.chunker.recursive import RecursiveChunker
from chonkie.types import RecursiveRules
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter

load_dotenv()

app = FastAPI()

# Initialize BaseEvaluation
evaluation = BaseEvaluation(
    questions_csv_path='data/sample_queries_large.csv',
    corpora_id_paths={'data/sample_document_large.txt': 'data/sample_document_large.txt'}
)

# Create an embedding function (using OpenAI as an example)
API_KEY = os.getenv('OPENAI_API_KEY')
embedding_func = embedding_functions.OpenAIEmbeddingFunction(
    api_key=API_KEY,
    model_name="text-embedding-3-large"
)

# Create a LangChain recursive chunker
lc_recursive_chunker = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=50
)

# Create a Chonkie recursive chunker
ck_recursive_chunker = RecursiveChunker(
    tokenizer="character",
    chunk_size=200,
    rules=RecursiveRules(),
    min_characters_per_chunk=24,
)

# Create a LangChain token chunker
lc_token_chunker = TokenTextSplitter(
    chunk_size=400,
    chunk_overlap=50
)

# Create a Chonkie token chunker
ck_token_chunker = TokenChunker(
    chunk_size=400,
    chunk_overlap=50
)

CHUNKERS: Dict[str, Any] = {
    'LangChain Recursive': lc_recursive_chunker,
    'Chonkie Recursive': ck_recursive_chunker,
    'Chonkie Token': ck_token_chunker,
    'LangChain Token': lc_token_chunker,
}

all_results = []

# Run evaluation
for name, chunker in CHUNKERS.items():
    print(f"\nEvaluating chunker: {name}")

    start_time = time.time()
    results = evaluation.run(chunker, embedding_function=embedding_func)
    end_time = time.time()
    elapsed_time = end_time - start_time

    results['chunker'] = name
    results['elapsed_time'] = elapsed_time
    all_results.append(results)

    # Print results
    print("\n=== Evaluation Results ===")
    print(f"Chunker: {name}")
    print(f"Elapsed Time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
    print(f"IoU Mean: {results['iou_mean']:.3f}")
    print(f"Recall Mean: {results['recall_mean']:.3f}")
    print(f"Precision Mean: {results['precision_mean']:.3f}")
    print(f"Precision Omega Mean: {results['precision_omega_mean']:.3f}")   


# ~~~~~~~~~~~~~~ small file 4kb ~~~~~~~~~~~~~~
# === Evaluation Results ===
# Chunker: LangChain Recursive
# IoU Mean: 0.210
# Recall Mean: 0.773
# Precision Mean: 0.229
# Precision Omega Mean: 0.609

# === Evaluation Results ===
# Chunker: Chonkie Recursive
# IoU Mean: 0.211
# Recall Mean: 0.784
# Precision Mean: 0.229
# Precision Omega Mean: 0.614

# === Evaluation Results ===
# Chunker: LangChain Token
# IoU Mean: 0.270
# Recall Mean: 1.000
# Precision Mean: 0.270
# Precision Omega Mean: 0.270

# === Evaluation Results ===
# Chunker: Chonkie Token
# IoU Mean: 0.242
# Recall Mean: 1.000
# Precision Mean: 0.242
# Precision Omega Mean: 0.541


# ~~~~~~~~~~~~~~ large file 123kb ~~~~~~~~~~~~~~
# === Evaluation Results ===
# Chunker: LangChain Recursive
# Elapsed Time: 3.87 seconds (0.06 minutes)
# IoU Mean: 0.166
# Recall Mean: 0.397
# Precision Mean: 0.193
# Precision Omega Mean: 0.777

# === Evaluation Results ===
# Chunker: Chonkie Recursive
# Elapsed Time: 5.10 seconds (0.08 minutes)
# IoU Mean: 0.132
# Recall Mean: 0.326
# Precision Mean: 0.152
# Precision Omega Mean: 0.697

# === Evaluation Results ===
# Chunker: Chonkie Token
# Elapsed Time: 1.61 seconds (0.03 minutes)
# IoU Mean: 0.113
# Recall Mean: 0.667
# Precision Mean: 0.113
# Precision Omega Mean: 0.437

# === Evaluation Results ===
# Chunker: LangChain Token
# Elapsed Time: 1.19 seconds (0.02 minutes)
# IoU Mean: 0.039
# Recall Mean: 1.000
# Precision Mean: 0.039
# Precision Omega Mean: 0.196

class ChunkerResult(BaseModel):
    iou_mean: float
    recall_mean: float
    precision_mean: float
    precision_omega_mean: float

class EvaluateResponse(BaseModel):
    embedding_model: str
    document_id: str
    chunkers_evaluated: List[str]
    results: Dict[str, ChunkerResult]

@app.post("/manual_evaluate")
async def evaluate_chunking(
    # document: UploadFile = File(),
    # questions: UploadFile = File(),
    chunkers: list[str] = ["LangChain Recursive", "Chonkie Recursive", "LangChain Token", "Chonkie Token"]
):

    invalid_chunkers = [c for c in chunkers if c not in CHUNKERS]
    if invalid_chunkers:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid chunkers specified: {invalid_chunkers}"
        )  
    
    try:
        # Initialize BaseEvaluation
        evaluation = BaseEvaluation(
            questions_csv_path='data/sample_queries.csv',
            corpora_id_paths={'data/sample_document.txt': 'data/sample_document.txt'}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error initializing BaseEvaluation: {str(e)}"
        )
    
    results = {}
    for name in chunkers:
        try:
            chunker = CHUNKERS[name]
            metrics = evaluation.run(chunker, embedding_function=embedding_func)
            results[name] = ChunkerResult(**metrics)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error evaluating chunker {name}: {str(e)}"
            )   
    return EvaluateResponse(
        embedding_model="text-embedding-3-large",
        document_id="sample_document.txt",
        chunkers_evaluated=chunkers,
        results=results
    )


