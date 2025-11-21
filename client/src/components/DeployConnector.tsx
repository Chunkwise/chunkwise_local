import { useEffect, useRef, useState } from "react";
import type { Workflow } from "../types";
import {
  deployWorkflow,
  type DeployWorkflowEvent,
  type S3Credentials,
  type RDSReadyPayload,
  type S3ConnectedPayload,
} from "../services/deploy";
import S3CredentialsForm from "./S3CredentialsForm";
import RDSConnectionDetails from "./RDSConnectionDetails";

interface DeployConnectorProps {
  workflow: Workflow;
}

const DeployConnector = ({ workflow }: DeployConnectorProps) => {
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [events, setEvents] = useState<DeployWorkflowEvent[]>([]);
  const [rdsDetails, setRdsDetails] = useState<RDSReadyPayload | null>(null);
  const [s3Details, setS3Details] = useState<S3ConnectedPayload | null>(null);
  const [status, setStatus] = useState<
    "idle" | "running" | "success" | "error"
  >("idle");
  const controllerRef = useRef<AbortController | null>(null);

  const hasChunkingStrategy = Boolean(workflow.chunking_strategy);

  useEffect(() => {
    return () => {
      controllerRef.current?.abort();
    };
  }, []);

  const appendEvent = (event: DeployWorkflowEvent) => {
    setEvents((previous) => [...previous, event]);

    switch (event.type) {
      case "rds-ready":
        setRdsDetails(event.data);
        break;
      case "s3-connected":
        setS3Details(event.data);
        break;
      case "s3-error":
      case "error":
        setError(event.data.error);
        setStatus("error");
        break;
      case "done":
        setStatus("success");
        break;
      default:
        break;
    }
  };

  const handleToggleForm = () => {
    if (!hasChunkingStrategy) return;
    setIsFormVisible((previous) => !previous);
    setError(null);
  };

  const handleCancel = () => {
    setIsFormVisible(false);
    setError(null);
  };

  const handleConnect = async (credentials: S3Credentials) => {
    if (!workflow.chunking_strategy) {
      setError("Select a chunker before deploying this workflow.");
      return;
    }

    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;

    setIsSubmitting(true);
    setError(null);
    setEvents([]);
    setRdsDetails(null);
    setS3Details(null);
    setIsFormVisible(false);
    setStatus("running");

    try {
      await deployWorkflow({
        workflowId: workflow.id,
        credentials,
        signal: controller.signal,
        onEvent: appendEvent,
      });
    } catch (connectionError) {
      if ((connectionError as Error).name === "AbortError") {
        setError("Deployment was cancelled.");
      } else {
        setError(
          (connectionError as Error).message ||
            "Unable to deploy workflow. Please verify the credentials."
        );
        console.error("Failed to deploy workflow", connectionError);
      }
      setStatus("error");
    } finally {
      setIsSubmitting(false);
      controllerRef.current = null;
    }
  };

  const describeEventTitle = (event: DeployWorkflowEvent): string => {
    switch (event.type) {
      case "rds-ready":
        return "RDS ready";
      case "s3-connected":
        return "S3 connected";
      case "s3-error":
        return "S3 error";
      case "error":
        return "Deployment error";
      case "done":
        return "Done";
      default:
        return "Update";
    }
  };

  const describeEventDetails = (event: DeployWorkflowEvent): string => {
    switch (event.type) {
      case "rds-ready":
        return `Instance ${event.data.db_instance_identifier} at ${event.data.endpoint}:${event.data.port}`;
      case "s3-connected":
        return `Verified bucket ${event.data.bucket}`;
      case "s3-error":
      case "error":
        return `${event.data.stage}: ${event.data.error}`;
      case "done":
        return "Deployment pipeline is ready to use.";
      default:
        return typeof event.data === "string"
          ? event.data
          : "Deployment update received.";
    }
  };

  const statusCopy = {
    idle: "Provide AWS credentials to deploy this workflow.",
    running: "Connecting to RDS and S3...",
    success: "Deployment completed successfully.",
    error: "Deployment could not be completed.",
  } as const;

  return (
    <div className="details-row">
      <h2 className="section-title">Deploy</h2>
      <div className="box">
        <div className="muted">
          Connect your Amazon S3 bucket to import and deploy chunked data.
        </div>

        <div className="muted" style={{ margin: "8px 0" }}>
          {statusCopy[status]}
        </div>

        <button
          className="btn btn-primary"
          type="button"
          onClick={handleToggleForm}
          disabled={!hasChunkingStrategy || isSubmitting}
        >
          Connect to Amazon S3
        </button>

        {!hasChunkingStrategy && (
          <div className="muted">
            Configure a chunker before setting up deployment.
          </div>
        )}

        {isFormVisible && (
          <S3CredentialsForm
            onSubmit={handleConnect}
            onCancel={handleCancel}
            isSubmitting={isSubmitting}
          />
        )}

        {error && <div className="error">{error}</div>}

        {s3Details && (
          <div className="deployment-summary" style={{ marginTop: "16px" }}>
            <div className="muted">
              Verified bucket <strong>{s3Details.bucket}</strong>
            </div>
          </div>
        )}

        {rdsDetails && (
          <div style={{ marginTop: "16px" }}>
            <RDSConnectionDetails details={rdsDetails} />
          </div>
        )}

        {events.length > 0 && (
          <div style={{ marginTop: "16px" }}>
            <div className="muted" style={{ marginBottom: "8px" }}>
              Live deployment log
            </div>
            <ul
              style={{
                listStyle: "none",
                padding: 0,
                margin: 0,
                display: "flex",
                flexDirection: "column",
                gap: "8px",
              }}
            >
              {events.map((event, index) => (
                <li
                  key={`${event.type}-${index}`}
                  style={{
                    border: "1px solid var(--border)",
                    borderRadius: "6px",
                    padding: "8px 12px",
                    background: "#f9fafb",
                  }}
                >
                  <div style={{ fontWeight: 600 }}>
                    {describeEventTitle(event)}
                  </div>
                  <div className="muted">{describeEventDetails(event)}</div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default DeployConnector;
