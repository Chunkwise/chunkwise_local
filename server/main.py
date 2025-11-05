from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional
import requests
import os
from utils import calculate_chunk_stats, normalize_document

app = FastAPI()
router = APIRouter()


class EitherRequest(BaseModel):
    chunker_type: Literal["recursive", "token"]
    provider: Literal["langchain", "chonkie"]
    chunk_size: str
    chunk_overlap: str
    text: str


class Chunk(BaseModel):
    text: str
    start_index: int
    end_index: int
    token_count: Optional[int] = None


CHUNKING_SERVICE_URL = os.getenv("CHUNKING_SERVICE_URL", "http://localhost:8001")
VISUALIZATION_SERVICE_URL = os.getenv(
    "VISUALIZATION_SERVICE_URL", "http://localhost:8002"
)
EVALUATION_SERVICE_URL = os.getenv("EVALUATION_SERVICE_URL", "http://localhost:8003")


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/visualize")
def visualize(request: EitherRequest):
    """
    Receives chunking parameters and text from client, sends them to the chunking service,
    then sends the chunks to the visualization service and returns the HTML.
    """
    try:
        # Prepare the request for the chunking service
        chunking_payload = {
            "chunker_type": request.chunker_type,
            "provider": request.provider,
            "chunk_size": int(request.chunk_size),
            "chunk_overlap": int(request.chunk_overlap),
            "text": request.text,
        }

        # Send request to chunking service
        chunking_response = requests.post(
            f"{CHUNKING_SERVICE_URL}/chunks", json=chunking_payload
        )
        chunking_response.raise_for_status()
        chunks = chunking_response.json()

        # Get chunk related stats
        stats = calculate_chunk_stats(chunks)

        # Send chunks to visualization service
        visualization_response = requests.post(
            f"{VISUALIZATION_SERVICE_URL}/visualization", json=chunks
        )
        visualization_response.raise_for_status()

        # Get the text from the response
        visualization_html = visualization_response.text

        # Return dict with stats and HTML
        return {"stats": stats, "html": visualization_html}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid input")

    except requests.RequestException as e:
        response = getattr(e, "response", None)
        if response is not None:
            if response.status_code in (400, 401, 403, 404):
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Upstream service returned a client error",
                )
            else:
                raise HTTPException(status_code=502, detail="Upstream service error")
        else:
            raise HTTPException(
                status_code=503, detail="Unable to reach upstream service"
            )

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/evaluate")
def evaluate(request: EitherRequest):
    try:
        request_body = {
            "chunking_configs": {
                "chunker_type": request.chunker_type,
                "provider": request.provider,
                "chunk_size": request.chunk_size,
                "chunk_overlap": request.chunk_overlap,
            },
            "document": normalize_document(request.text),
        }

        # Send request to chunking service
        evaluation_response = requests.post(
            f"{EVALUATION_SERVICE_URL}/evaluate", json=request_body
        )
        evaluation_response.raise_for_status()
        metrics = evaluation_response.json()

        return metrics

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid input")

    except requests.RequestException as e:
        response = getattr(e, "response", None)
        if response is not None:
            if response.status_code in (400, 401, 403, 404):
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Upstream service returned a client error",
                )
            else:
                raise HTTPException(status_code=502, detail="Upstream service error")
        else:
            raise HTTPException(
                status_code=503, detail="Unable to reach upstream service"
            )

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


app.include_router(router, prefix="/api")
