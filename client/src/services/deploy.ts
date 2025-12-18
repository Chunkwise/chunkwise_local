import axios from "axios";
import { encryptCredentials } from "../utils/encrypt";
import {
  DeployWorkflowEventSchema,
  type S3Credentials,
  type DeployWorkflowEvent,
} from "../types";

type EphemeralKeyResponse = {
  token: string;
  public_key_pem: string;
  expires_in: number;
};

async function getEphemeralKey(): Promise<EphemeralKeyResponse> {
  const response = await axios.post<EphemeralKeyResponse>(
    "/api/ephemeral-key",
    {},
    { timeout: 5000 }
  );
  return response.data;
}

interface DeployWorkflowOptions {
  workflowId: string;
  credentials: S3Credentials;
  onEvent: (event: DeployWorkflowEvent) => void;
}

export const deployWorkflow = async ({
  workflowId,
  credentials,
  onEvent,
}: DeployWorkflowOptions): Promise<void> => {
  // Fetch ephemeral key
  const { token, public_key_pem } = await getEphemeralKey();

  // Encrypt credentials
  const encrypted = await encryptCredentials(
    public_key_pem,
    credentials.access_key,
    credentials.secret_key
  );

  const response = await axios.post(
    `/api/workflows/${workflowId}/deploy`,
    {
      crypto_token: token,
      encrypted_credentials_b64: encrypted,
      s3_bucket: credentials.bucket_name,
    },
    {
      headers: {
        "Content-Type": "application/json",
      },
      responseType: "stream",
      adapter: "fetch",
    }
  );

  // Immediate client-side cleanup
  credentials.access_key = "";
  credentials.secret_key = "";

  if (!response.data) {
    throw new Error("Response stream not available");
  }

  const reader = response.data.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    let boundary = buffer.indexOf("\n\n");
    while (boundary !== -1) {
      const chunk = buffer.slice(0, boundary).trim();
      buffer = buffer.slice(boundary + 2);

      if (chunk) {
        const lines = chunk.split("\n");
        let eventType = "";
        let data = "";

        for (const line of lines) {
          if (line.startsWith("event:")) {
            eventType = line.slice(6).trim();
          } else if (line.startsWith("data:")) {
            data = line.slice(5).trim();
          }
        }

        if (eventType && data) {
          const parsedData = JSON.parse(data);
          const rawEvent = {
            type: eventType,
            data: parsedData,
          };
          onEvent(DeployWorkflowEventSchema.parse(rawEvent));
        }
      }

      boundary = buffer.indexOf("\n\n");
    }
  }
};
