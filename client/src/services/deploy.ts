import axios from "axios";
import {
  DeployWorkflowEventSchema,
  type S3Credentials,
  type DeployWorkflowEvent,
} from "../types";

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
  const response = await axios.post(
    `/api/workflows/${workflowId}/deploy`,
    {
      s3_access_key: credentials.access_key,
      s3_secret_key: credentials.secret_key,
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
