from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional
import requests
import os

app = FastAPI()
router = APIRouter()


class VisualizeRequest(BaseModel):
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


def calculateChunkStats(chunks):
    stats = {
        "total_chunks": len(chunks),
    }
    total_chars = 0

    for chunk in chunks:
        if chunk.get("text") and len(chunk["text"]) > 0:
            total_chars += len(chunk["text"])
            if (not stats.get("largest_char_count")) or (
                len(chunk["text"]) > stats["largest_char_count"]
            ):
                stats["largest_char_count"] = len(chunk["text"])
                stats["largest_text"] = chunk["text"]
            if (not stats.get("smallest_char_count")) or (
                len(chunk["text"]) < stats["smallest_char_count"]
            ):
                stats["smallest_char_count"] = len(chunk["text"])
                stats["smallest_text"] = chunk["text"]

    stats["avg_chars"] = total_chars / stats["total_chunks"]

    return stats


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/visualize")
def visualize(request: VisualizeRequest):
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

        stats = calculateChunkStats(chunks)

        # # Prepare the request for the visualization service
        # visualization_payload = {"chunks": chunks}

        # # Send chunks to visualization service
        # visualization_response = requests.post(
        #     f"{VISUALIZATION_SERVICE_URL}/visualization", json=visualization_payload
        # )
        # visualization_response.raise_for_status()

        # Return a success message to client, return HTML content in real implementation
        return {"stats": stats, "html": "<><>"}

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
