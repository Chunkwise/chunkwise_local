import type { ChunkerSelection, RequestBody } from "../types/types";

function isValidRequestBody(body: Partial<RequestBody>): body is RequestBody {
  if (
    "chunker_type" in body &&
    typeof body.chunker_type === "string" &&
    "provider" in body &&
    typeof body.provider === "string" &&
    "chunk_size" in body &&
    typeof body.chunk_size === "number" &&
    "chunk_overlap" in body &&
    typeof body.chunk_overlap === "number" &&
    "text" in body &&
    typeof body.text === "string"
  ) {
    return true;
  } else {
    return false;
  }
}

export default function createRequestBody({
  chunker,
  size,
  overlap,
  text,
  min_characters_per_chunk,
  tokenizer,
}: {
  chunker: ChunkerSelection;
  size: number;
  overlap: number;
  text: string;
  min_characters_per_chunk?: number;
  tokenizer?: string;
}): RequestBody {
  const body: Partial<RequestBody> = {
    chunk_size: size,
    chunk_overlap: overlap,
    text: text,
    min_characters_per_chunk: min_characters_per_chunk,
    tokenizer: tokenizer,
  };

  // Don't know the exact naming format but this should make it easy to have whatever we like
  switch (chunker) {
    case "Chonkie Token":
      body.provider = "chonkie";
      body.chunker_type = "token";
      break;
    case "Chonkie Recursive":
      body.provider = "chonkie";
      body.chunker_type = "recursive";
      break;
    case "LangChain Token":
      body.provider = "langchain";
      body.chunker_type = "token";
      break;
    case "LangChain Recursive":
      body.provider = "langchain";
      body.chunker_type = "recursive";
      break;
    default:
      throw new Error("Unhandled chunker selected");
  }

  if (isValidRequestBody(body)) {
    return body;
  } else {
    throw new Error("Invalid request body created");
  }
}
