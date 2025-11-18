// import axios from "axios";
// import type { ChunkingStrategy } from "../types";
//
// export interface S3Credentials {
//   access_key: string;
//   secret_key: string;
//   bucket_name: string;
// }
//
// interface DeployRequestPayload {
//   workflowId: string;
//   credentials: S3Credentials;
//   chunkingStrategy: ChunkingStrategy;
// }
//
// interface DeployResponse {
//   bucket_name: string;
// }
//
// export const connectToS3 = async ({
//   workflowId,
//   credentials,
//   chunkingStrategy,
// }: DeployRequestPayload): Promise<DeployResponse> => {
//   const response = await axios.post(
//     `/api/workflows/${workflowId}/deploy`,
//     {
//       chunking_strategy: chunkingStrategy,
//       credentials,
//     }
//   );
//
//   return response.data;
// };

// Mock service for local development
import type { ChunkingStrategy } from "../types";

export interface S3Credentials {
  access_key: string;
  secret_key: string;
  bucket_name: string;
}

interface DeployRequestPayload {
  workflowId: string;
  credentials: S3Credentials;
  chunkingStrategy: ChunkingStrategy;
}

interface DeployResponse {
  bucket_name: string;
  rds_endpoint: string;
}

export const connectToS3 = async ({
  workflowId,
  credentials,
  chunkingStrategy,
}: DeployRequestPayload): Promise<DeployResponse> => {
  await new Promise((resolve) => setTimeout(resolve, 1200));

  const provider = (chunkingStrategy.provider || "chunkwise").toString();
  const chunker = (chunkingStrategy.chunker_type || "strategy").toString();
  const sanitizedBucket = credentials.bucket_name.replace(/\s+/g, "-");
  const endpointHost = `${sanitizedBucket}.${chunker}.${provider}`
    .toLowerCase()
    .replace(/[^a-z0-9.-]/g, "-");

  return {
    bucket_name: credentials.bucket_name,
    rds_endpoint: `postgres://${workflowId}.${endpointHost}.rds.local`,
  };
};
