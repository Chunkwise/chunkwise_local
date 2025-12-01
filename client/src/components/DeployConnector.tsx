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
import ErrorMessage from "./ErrorMessage";

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
    setEvents((previous) => {
      if (event.type === "jobs-updated") {
        return [...previous.filter(event => event.type !== "jobs-updated"), event];
      }
      return [...previous, event];
    });

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
      case "batch-error":
        return "Batch error";
      case "jobs-updated":
        return "Jobs Status";
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
        return `Instance ${event.data.db_instance_identifier}`;
      case "s3-connected":
        return `Verified bucket ${event.data.bucket}`;
      case "jobs-updated":
        return `${event.data.statuses.succeeded} succeeded and ${event.data.statuses.failed} failed out of ${event.data.statuses.total} total jobs.`
      case "batch-error":
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

  const getStatusIcon = (currentStatus: typeof status): string => {
    switch (currentStatus) {
      case "running":
        return "sync";
      case "success":
        return "check_circle";
      case "error":
        return "error";
      default:
        return "info";
    }
  };

  return (
    <div className="section">
      <h2 className="section-header">
        <span className="icon">cloud_upload</span>
        <span className="title-md">Deploy</span>
      </h2>
      <div className="card">
        <div className="text-muted">
          <span className="icon icon-sm">storage</span>
          Connect your Amazon S3 bucket to import and deploy chunked data.
        </div>

        <div className={`text-muted mt-2 flex items-center gap-1 ${status === "running" ? "spinner" : ""}`}>
          <span className={`icon icon-sm ${status === "running" ? "spinner" : ""}`}>
            {getStatusIcon(status)}
          </span>
          {statusCopy[status]}
        </div>

        <button
          className="btn btn-primary mt-3"
          type="button"
          onClick={handleToggleForm}
          disabled={!hasChunkingStrategy || isSubmitting}
        >
          <span className="icon icon-sm">link</span>
          Connect to Amazon S3
        </button>

        {!hasChunkingStrategy && (
          <div className="text-muted mt-2">
            <span className="icon icon-sm">warning</span>
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

        {error && <ErrorMessage message={error} />}

        {s3Details && (
          <div className="deploy-summary">
            <div className="text-muted flex items-center gap-1">
              <span className="icon icon-sm">check_circle</span>
              Verified bucket <strong>{s3Details.bucket}</strong>
            </div>
          </div>
        )}

        {rdsDetails && (
          <div className="mt-4">
            <RDSConnectionDetails details={rdsDetails} />
          </div>
        )}

        {events.length > 0 && (
          <div className="deploy-log">
            <div className="deploy-log-title">
              <span className="icon icon-sm">terminal</span>
              Live deployment log
            </div>
            <ul className="deploy-log-list">
              {events.map((event, index) => (
                <li key={`${event.type}-${index}`} className="deploy-log-item">
                  <div className="deploy-log-item-title">
                    <span className="icon icon-sm">arrow_right</span>
                    {describeEventTitle(event)}
                  </div>
                  <div className="text-muted">{describeEventDetails(event)}</div>
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
