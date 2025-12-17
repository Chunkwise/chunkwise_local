import { useState, useEffect } from "react";
import S3CredentialsForm from "./S3CredentialsForm";
import RDSConnectionDetails from "./RDSConnectionDetails";
import DeployProgress from "./DeployProgress";
import { deployWorkflow } from "../services/deploy";
import { getRdsSecretArn, setRdsSecretArn } from "../utils/storage";
import type {
  Workflow,
  DeployWorkflowEvent,
  S3Credentials,
  DeploymentState,
} from "../types";
import type { DeploymentAction } from "../reducers/deploymentReducer";
import {
  startDeploymentAction,
  setRdsDetailsAction,
  setS3BucketAction,
  setNoDocumentsAction,
  setJobsStatusAction,
  setCompleteAction,
  setErrorAction,
} from "../reducers/deploymentReducer";

interface DeployConnectorProps {
  workflow: Workflow;
  onWorkflowUpdate: (updates: Partial<Workflow>) => void;
  deploymentState?: DeploymentState;
  deploymentDispatch: React.Dispatch<DeploymentAction>;
  isAnyDeploying: boolean;
}

// Sub-components
interface DeployMessageProps {
  icon: string;
  message: string;
  type?: "info" | "warning" | "error";
}

const DeployMessage = ({
  icon,
  message,
  type = "info",
}: DeployMessageProps) => (
  <p className={`text-muted mt-2 ${type === "error" ? "deploy-error" : ""}`}>
    <span className="icon icon-sm">{icon}</span>
    <span>{message}</span>
  </p>
);

interface DeployButtonProps {
  onClick: () => void;
  disabled: boolean;
  icon: string;
  label: string;
}

const DeployButton = ({
  onClick,
  disabled,
  icon,
  label,
}: DeployButtonProps) => (
  <button
    className="btn btn-primary mt-3"
    onClick={onClick}
    disabled={disabled}
  >
    <span className="icon icon-sm">{icon}</span>
    {label}
  </button>
);

interface DeployStatusBadgeProps {
  icon: string;
  text: string;
}

const DeployStatusBadge = ({ icon, text }: DeployStatusBadgeProps) => (
  <div className="deploy-status-badge">
    <span className="icon icon-sm">{icon}</span>
    <span>{text}</span>
  </div>
);

const DeployConnector = ({
  workflow,
  onWorkflowUpdate,
  deploymentState,
  deploymentDispatch,
  isAnyDeploying,
}: DeployConnectorProps) => {
  const [showForm, setShowForm] = useState(false);
  const hasChunkingStrategy = Boolean(workflow.chunking_strategy);
  const isDeployed = Boolean(workflow.deploy_table_name);
  const storedArn = getRdsSecretArn();

  const {
    isDeploying = false,
    rdsDetails = null,
    s3Bucket = null,
    jobsStatus = null,
    noDocuments = false,
    isComplete = false,
    error = null,
  } = deploymentState || {};

  const canDeploy = hasChunkingStrategy && !isAnyDeploying;

  useEffect(() => {
    if (isDeployed && storedArn && !rdsDetails) {
      deploymentDispatch(
        setRdsDetailsAction(workflow.id, {
          ok: true,
          stage: "rds-ready",
          endpoint: "",
          port: 5432,
          database: "",
          table_name: workflow.deploy_table_name!,
          secret_arn: storedArn,
          db_instance_identifier: "",
        })
      );
    }
  }, [
    isDeployed,
    storedArn,
    workflow.deploy_table_name,
    workflow.id,
    rdsDetails,
    deploymentDispatch,
  ]);

  // Handler for starting deployment
  const handleConnect = async (credentials: S3Credentials) => {
    setShowForm(false);
    deploymentDispatch(startDeploymentAction(workflow.id));

    try {
      await deployWorkflow({
        workflowId: workflow.id,
        credentials,
        onEvent: handleEvent,
      });
    } catch (error) {
      deploymentDispatch(
        setErrorAction(
          workflow.id,
          (error as Error).message || "Deployment failed"
        )
      );
    }
  };

  // Handler for deployment events
  const handleEvent = (event: DeployWorkflowEvent) => {
    switch (event.type) {
      case "rds-ready":
        deploymentDispatch(setRdsDetailsAction(workflow.id, event.data));
        setRdsSecretArn(event.data.secret_arn);
        break;
      case "s3-connected":
        deploymentDispatch(setS3BucketAction(workflow.id, event.data.bucket));
        break;
      case "no-documents":
        deploymentDispatch(setNoDocumentsAction(workflow.id));
        break;
      case "jobs-updated":
        deploymentDispatch(
          setJobsStatusAction(workflow.id, event.data.statuses)
        );
        break;
      case "done":
        deploymentDispatch(setCompleteAction(workflow.id));
        if (event.data.summary?.table) {
          onWorkflowUpdate({
            deploy_table_name: event.data.summary.table,
            stage: "Deployed",
          });
        }
        break;
      case "s3-error":
      case "batch-error":
      case "error":
        deploymentDispatch(setErrorAction(workflow.id, event.data.error));
        break;
    }
  };

  // Handler for redeploying workflow
  const handleRedeploy = () => {
    setShowForm(true);
  };

  // Render state for initial deployment
  const renderInitialState = () => (
    <>
      <p className="text-muted">
        Connect your Amazon S3 bucket to deploy chunked documents to your vector
        database.
      </p>

      <DeployButton
        onClick={() => setShowForm(!showForm)}
        disabled={!canDeploy}
        icon="link"
        label="Connect to Amazon S3"
      />

      {!hasChunkingStrategy && (
        <DeployMessage
          icon="warning"
          message="Configure a chunker before setting up deployment."
        />
      )}

      {isAnyDeploying && hasChunkingStrategy && (
        <DeployMessage
          icon="info"
          message="Another workflow is currently being deployed."
        />
      )}

      {showForm && (
        <S3CredentialsForm
          onSubmit={handleConnect}
          onCancel={() => setShowForm(false)}
        />
      )}

      {error && <DeployMessage icon="error" message={error} type="error" />}
    </>
  );

  // Render state for deploying workflow
  const renderDeployingState = () => (
    <>
      <div className="deploy-warning mb-3">
        <span className="icon icon-sm">warning</span>
        <span>
          <strong>Deployment in progress.</strong> Please do not close or reload
          this page until deployment is complete.
        </span>
      </div>

      <DeployProgress
        rdsDetails={rdsDetails}
        s3Bucket={s3Bucket}
        jobsStatus={jobsStatus}
        noDocuments={noDocuments}
        isComplete={isComplete}
        error={error}
      />

      {rdsDetails && <RDSConnectionDetails details={rdsDetails} />}

      {isComplete && (
        <>
          <DeployButton
            onClick={handleRedeploy}
            disabled={!canDeploy}
            icon="refresh"
            label="Redeploy Workflow"
          />

          {isAnyDeploying && (
            <DeployMessage
              icon="info"
              message="Another workflow is currently being deployed."
            />
          )}

          {showForm && (
            <S3CredentialsForm
              onSubmit={handleConnect}
              onCancel={() => setShowForm(false)}
            />
          )}
        </>
      )}
    </>
  );

  // Render state for deployed workflow
  const renderDeployedState = () => (
    <>
      <DeployStatusBadge icon="check_circle" text="Workflow Deployed" />

      {rdsDetails && <RDSConnectionDetails details={rdsDetails} />}

      <DeployButton
        onClick={handleRedeploy}
        disabled={!canDeploy}
        icon="refresh"
        label="Redeploy Workflow"
      />

      {isAnyDeploying && (
        <DeployMessage
          icon="info"
          message="Another workflow is currently being deployed."
        />
      )}

      {showForm && (
        <S3CredentialsForm
          onSubmit={handleConnect}
          onCancel={() => setShowForm(false)}
        />
      )}

      {error && <DeployMessage icon="error" message={error} type="error" />}
    </>
  );

  // Determine the state to render
  const renderContent = () => {
    if (isDeploying) {
      return renderDeployingState();
    }
    if (isDeployed) {
      return renderDeployedState();
    }
    return renderInitialState();
  };

  return (
    <div className="section">
      <h2 className="section-header">
        <span className="title-md">Deploy</span>
      </h2>

      <div className="card">{renderContent()}</div>
    </div>
  );
};

export default DeployConnector;
