export interface S3Credentials {
  access_key: string;
  secret_key: string;
  bucket_name: string;
}

export interface RDSReadyPayload {
  ok: boolean;
  stage: "rds-ready";
  db_instance_identifier: string;
  endpoint: string;
  port: number;
  database: string;
  username_secret_arn: string;
  table_name: string;
  notes?: string;
}

export interface S3ConnectedPayload {
  ok: boolean;
  stage: "s3-connected";
  bucket: string;
}

export interface DeployErrorPayload {
  ok: false;
  stage: string;
  error: string;
  trace?: string;
}

export interface DeployDonePayload {
  ok: true;
  stage: "done";
}

export type DeployWorkflowEvent =
  | { type: "rds-ready"; data: RDSReadyPayload }
  | { type: "s3-connected"; data: S3ConnectedPayload }
  | { type: "s3-error"; data: DeployErrorPayload }
  | { type: "error"; data: DeployErrorPayload }
  | { type: "done"; data: DeployDonePayload }
  | { type: "message"; data: unknown };

interface DeployWorkflowOptions {
  workflowId: string;
  credentials: S3Credentials;
  signal?: AbortSignal;
  onEvent: (event: DeployWorkflowEvent) => void;
}

const parseSseChunk = (
  chunk: string
): { event: string; data: unknown } | null => {
  const lines = chunk.split(/\r?\n/);
  let eventName = "message";
  const dataLines: string[] = [];

  for (const line of lines) {
    if (line.startsWith("event:")) {
      eventName = line.slice(6).trim();
    } else if (line.startsWith("data:")) {
      dataLines.push(line.slice(5).trim());
    }
  }

  if (dataLines.length === 0) {
    return null;
  }

  const dataPayload = dataLines.join("\n");
  try {
    return { event: eventName, data: JSON.parse(dataPayload) };
  } catch {
    return { event: eventName, data: dataPayload };
  }
};

const mapEvent = (eventName: string): DeployWorkflowEvent["type"] => {
  switch (eventName) {
    case "rds-ready":
      return "rds-ready";
    case "s3-connected":
      return "s3-connected";
    case "s3-error":
      return "s3-error";
    case "error":
      return "error";
    case "done":
      return "done";
    default:
      return "message";
  }
};

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
    throw new Error("Deployment response stream is not available");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });

    let boundary = buffer.indexOf("\n\n");
    while (boundary !== -1) {
      const chunk = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      const parsed = parseSseChunk(chunk);
      if (parsed) {
        onEvent({
          type: mapEvent(parsed.event),
          data: parsed.data,
        } as DeployWorkflowEvent);
      }
      boundary = buffer.indexOf("\n\n");
    }
  }

  buffer += decoder.decode();

  if (buffer.trim().length > 0) {
    const parsed = parseSseChunk(buffer);
    if (parsed) {
      onEvent({
        type: mapEvent(parsed.event),
        data: parsed.data,
      } as DeployWorkflowEvent);
    }
  }
};
