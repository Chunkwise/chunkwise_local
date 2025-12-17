import type { S3Credentials, DeployWorkflowEvent } from "../types";

interface DeployWorkflowOptions {
  workflowId: string;
  credentials: S3Credentials;
  signal?: AbortSignal;
  onEvent: (event: DeployWorkflowEvent) => void;
}

export const deployWorkflow = async ({
  workflowId,
  credentials,
  signal,
  onEvent,
}: DeployWorkflowOptions): Promise<void> => {
  const response = await fetch(`/api/workflows/${workflowId}/deploy`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      s3_access_key: credentials.access_key,
      s3_secret_key: credentials.secret_key,
      s3_bucket: credentials.bucket_name,
    }),
    signal,
  });

  if (!response.ok) {
    throw new Error(`Deployment failed with status ${response.status}`);
  }

  if (!response.body) {
    throw new Error("Response stream not available");
  }

  const reader = response.body.getReader();
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
          onEvent({
            type: eventType as DeployWorkflowEvent["type"],
            data: JSON.parse(data),
          } as DeployWorkflowEvent);
        }
      }

      boundary = buffer.indexOf("\n\n");
    }
  }
};
