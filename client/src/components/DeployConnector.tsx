import { useRef, useState, useCallback } from "react";
import type { Workflow } from "../types";
import type {
  DeployWorkflowEvent,
  S3Credentials,
  RDSReadyPayload,
  JobsStatus,
  DeploySummary,
} from "../types";
import { deployWorkflow } from "../services/deploy";
import S3CredentialsForm from "./S3CredentialsForm";
import RDSConnectionDetails from "./RDSConnectionDetails";
import DeployProgress from "./DeployProgress";

type DeployStatus = "idle" | "running" | "success" | "error";

interface DeployState {
  status: DeployStatus;
  error: string | null;
  rdsDetails: RDSReadyPayload | null;
  s3Bucket: string | null;
  jobsStatus: JobsStatus | null;
  summary: DeploySummary | null;
  noDocuments: boolean;
}

const initialState: DeployState = {
  status: "idle",
  error: null,
  rdsDetails: null,
  s3Bucket: null,
  jobsStatus: null,
  summary: null,
  noDocuments: false,
};

interface DeployConnectorProps {
  workflow: Workflow;
}

const DeployConnector = ({ workflow }: DeployConnectorProps) => {
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [state, setState] = useState<DeployState>(initialState);
  const controllerRef = useRef<AbortController | null>(null);

  const hasChunkingStrategy = Boolean(workflow.chunking_strategy);

  const handleEvent = useCallback((event: DeployWorkflowEvent) => {
    switch (event.type) {
      case "rds-ready":
        setState((prev) => ({ ...prev, rdsDetails: event.data }));
        break;
      case "s3-connected":
        setState((prev) => ({ ...prev, s3Bucket: event.data.bucket }));
        break;
      case "no-documents":
        setState((prev) => ({ ...prev, noDocuments: true }));
        break;
      case "jobs-updated":
        setState((prev) => ({ ...prev, jobsStatus: event.data.statuses }));
        break;
      case "done":
        setState((prev) => ({
          ...prev,
          status: "success",
          summary: event.data.summary ?? null,
        }));
        break;
      case "s3-error":
      case "batch-error":
      case "error":
        setState((prev) => ({
          ...prev,
          status: "error",
          error: event.data.error,
        }));
        break;
    }
  }, []);

  const handleConnect = async (credentials: S3Credentials) => {
    if (!workflow.chunking_strategy) {
      setState((prev) => ({
        ...prev,
        error: "Select a chunker before deploying this workflow.",
      }));
      return;
    }

    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;

    setIsSubmitting(true);
    setIsFormVisible(false);
    setState({ ...initialState, status: "running" });

    try {
      await deployWorkflow({
        workflowId: workflow.id,
        credentials,
        signal: controller.signal,
        onEvent: handleEvent,
      });
    } catch (connectionError) {
      const errorMessage =
        (connectionError as Error).name === "AbortError"
          ? "Deployment was cancelled."
          : (connectionError as Error).message ||
            "Unable to deploy workflow. Please verify the credentials.";
      setState((prev) => ({ ...prev, status: "error", error: errorMessage }));
    } finally {
      setIsSubmitting(false);
      controllerRef.current = null;
    }
  };

  const handleToggleForm = () => {
    if (!hasChunkingStrategy) return;
    setIsFormVisible((prev) => !prev);
    if (state.error) {
      setState((prev) => ({ ...prev, error: null }));
    }
  };

  const handleCancel = () => {
    setIsFormVisible(false);
  };

  const handleDismissError = () => {
    setState((prev) => ({ ...prev, error: null }));
  };

  const isDeploymentActive = state.status === "running" || state.status === "success";

  return (
    <div className="section">
      <h2 className="section-header">
        <span className="icon">cloud_upload</span>
        <span className="title-md">Deploy</span>
      </h2>

      <div className="card">
        {!isDeploymentActive && (
          <>
            <p className="text-muted">
              <span className="icon icon-sm">storage</span>
              Connect your Amazon S3 bucket to deploy chunked documents to your vector database.
            </p>

            <button
              className="btn btn-primary mt-3"
              type="button"
              onClick={handleToggleForm}
              disabled={!hasChunkingStrategy || isSubmitting}
            >
              <span className="icon icon-sm">link</span>
              {isSubmitting ? "Connecting..." : "Connect to Amazon S3"}
            </button>

            {!hasChunkingStrategy && (
              <p className="text-muted mt-2">
                <span className="icon icon-sm">warning</span>
                Configure a chunker before setting up deployment.
              </p>
            )}

            {isFormVisible && (
              <S3CredentialsForm
                onSubmit={handleConnect}
                onCancel={handleCancel}
                isSubmitting={isSubmitting}
              />
            )}

            {state.error && (
              <div className="deploy-error mt-3">
                <span className="icon icon-sm">close</span>
                <span>{state.error}</span>
                <button
                  className="btn btn-icon btn-sm"
                  onClick={handleDismissError}
                  aria-label="Dismiss error"
                >
                  <span className="icon icon-sm">close</span>
                </button>
              </div>
            )}
          </>
        )}

        {isDeploymentActive && (
          <DeployProgress
            status={state.status}
            rdsDetails={state.rdsDetails}
            s3Bucket={state.s3Bucket}
            jobsStatus={state.jobsStatus}
            summary={state.summary}
            noDocuments={state.noDocuments}
            error={state.error}
          />
        )}

        {state.rdsDetails && state.status === "success" && (
          <RDSConnectionDetails details={state.rdsDetails} />
        )}
      </div>
    </div>
  );
};

export default DeployConnector;
