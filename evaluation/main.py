import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from chunking_evaluation.evaluation_framework.base_evaluation import BaseEvaluation
from chromadb.utils import embedding_functions
from utils import normalize_document, generate_sample_queries
from chunkwise_core import (
    create_chunker,
    Evaluation,
    EvaluationRequest,
    EvaluationResponse,
)

load_dotenv()

app = FastAPI()

EMBEDDING_API_KEY = os.getenv("OPENAI_API_KEY")

# Create an embedding function (using OpenAI as an example)
embedding_func = embedding_functions.OpenAIEmbeddingFunction(
    api_key=EMBEDDING_API_KEY, model_name="text-embedding-3-large"
)

# Note: use this when returning/printing configs
# config = config.model_dump(exclude_none=True, exclude_unset=True, exclude_defaults=True)


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_chunking(request: EvaluationRequest):
    queries_generated = False
    final_queries_path = None
    num_queries_generated = None

    try:
        # Validate the document path
        if not os.path.exists(request.document_path):
            raise HTTPException(
                status_code=404,
                detail=f"Document not found at path: {request.document_path}",
            )

        # Check if file is readable
        if not os.path.isfile(request.document_path):
            raise HTTPException(
                status_code=400, detail=f"Path is not a file: {request.document_path}"
            )

        # Extract document ID from path
        document_id = os.path.basename(request.document_path)
        # Remove file extension for document name
        document_name = os.path.splitext(document_id)[0]

        # Normalize the document
        os.makedirs(
            request.queries_output_dir, exist_ok=True
        )  # Make sure output dir exists
        normalized_doc_path = normalize_document(
            request.document_path,
            os.path.join(request.queries_output_dir, f"{document_name}_normalized.txt"),
        )

        if request.queries_path:
            # Use existing queries
            if not os.path.exists(request.queries_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"Queries file not found at path: {request.queries_path}",
                )
            final_queries_path = request.queries_path
            queries_generated = False
            num_queries_generated = None
        else:
            # Generate queries using LLM
            llm_api_key = os.getenv("OPENAI_API_KEY")
            if not llm_api_key:
                raise HTTPException(
                    status_code=500,
                    detail="OPENAI_API_KEY environment variable is required for query generation",
                )

            # Determine output path for generated queries
            queries_filename = f"llm_queries_{document_name}.csv"
            queries_output_path = os.path.join(
                request.queries_output_dir, queries_filename
            )

            try:
                final_queries_path = generate_sample_queries(
                    openai_api_key=llm_api_key,
                    document_paths=[normalized_doc_path],
                    queries_output_path=queries_output_path,
                    num_rounds=request.num_rounds,
                    queries_per_corpus=request.queries_per_corpus,
                    approximate_excerpts=request.approximate_excerpts,
                    poor_reference_threshold=request.poor_reference_threshold,
                    duplicate_question_threshold=request.duplicate_question_threshold,
                )
                queries_generated = True
                # Count number of queries generated
                try:
                    with open(final_queries_path, "r", encoding="utf-8") as f:
                        num_queries_generated = sum(1 for _ in f) - 1  # Exclude header
                except Exception:
                    num_queries_generated = (
                        request.queries_per_corpus * request.num_rounds
                    )

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error generating sample queries: {str(e)}",
                )

        try:
            # Initialize BaseEvaluation using normalized document and provided queries path
            evaluation = BaseEvaluation(
                questions_csv_path=final_queries_path,
                corpora_id_paths={normalized_doc_path: normalized_doc_path},
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error initializing BaseEvaluation: {str(e)}"
            )

        results = []
        chunker_names = []

        for config in request.chunking_configs:
            try:
                chunker = create_chunker(config)
                metrics = evaluation.run(chunker, embedding_function=embedding_func)
                chunker_name = f"{config.chunker_type}"
                chunker_names.append(chunker_name)
                results.append(Evaluation(**metrics, chunker_config=config))
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error evaluating chunker {config.chunker_type}: {str(e)}",
                )

        return EvaluationResponse(
            embedding_model="text-embedding-3-large",
            document_id=document_id,
            document_path=request.document_path,
            queries_path=final_queries_path,
            queries_generated=queries_generated,
            num_queries=num_queries_generated,
            chunkers_evaluated=chunker_names,
            results=results,
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=500, detail=f"Unexpected error in evaluation pipeline: {str(e)}"
        )
