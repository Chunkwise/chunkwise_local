import { useState, useEffect } from "react";
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
  resetDeploymentAction,
} from "../reducers/deploymentReducer";
import { deployWorkflow } from "../services/deploy";
import { getRdsSecretArn, setRdsSecretArn } from "../utils/storage";
import S3CredentialsForm from "./S3CredentialsForm";
import RDSConnectionDetails from "./RDSConnectionDetails";
import DeployProgress from "./DeployProgress";

interface DeployConnectorProps {
  workflow: Workflow;
  onWorkflowUpdate: (updates: Partial<Workflow>) => void;
  deploymentState?: DeploymentState;
  deploymentDispatch: React.Dispatch<DeploymentAction>;
  isAnyDeploying: boolean;
}

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

  // Load existing RDS details if workflow is already deployed
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

  const handleConnect = async (credentials: S3Credentials) => {
    setShowForm(false);
    deploymentDispatch(startDeploymentAction(workflow.id));

    try {
      await deployWorkflow({
        workflowId: workflow.id,
        credentials,
        onEvent: handleEvent,
      });
    } catch (err) {
      deploymentDispatch(
        setErrorAction(
          workflow.id,
          (err as Error).message || "Deployment failed"
        )
      );
    }
  };

  const handleRedeploy = () => {
    deploymentDispatch(resetDeploymentAction(workflow.id));
    setShowForm(true);
  };

  const isActive = isDeploying;
  const canDeploy = hasChunkingStrategy && !isAnyDeploying;

  return (
    <div className="section">
      <h2 className="section-header">
        <span className="icon">cloud_upload</span>
        <span className="title-md">Deploy</span>
      </h2>

      <div className="card">
        {!isActive && !isDeployed && (
          <>
            <p className="text-muted">
              <span className="icon icon-sm">storage</span>
              Connect your Amazon S3 bucket to deploy chunked documents to your
              vector database.
            </p>

            <button
              className="btn btn-primary mt-3"
              onClick={() => setShowForm(!showForm)}
              disabled={!canDeploy}
            >
              <span className="icon icon-sm">link</span>
              Connect to Amazon S3
            </button>

            {!hasChunkingStrategy && (
              <p className="text-muted mt-2">
                <span className="icon icon-sm">warning</span>
                Configure a chunker before setting up deployment.
              </p>
            )}

            {isAnyDeploying && hasChunkingStrategy && (
              <p className="text-muted mt-2">
                <span className="icon icon-sm">info</span>
                Another workflow is currently being deployed.
              </p>
            )}

            {showForm && (
              <S3CredentialsForm
                onSubmit={handleConnect}
                onCancel={() => setShowForm(false)}
              />
            )}

            {error && (
              <div className="deploy-error mt-3">
                <span className="icon icon-sm">error</span>
                <span>{error}</span>
              </div>
            )}
          </>
        )}

        {isActive && (
          <>
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
                <button
                  className="btn btn-primary mt-3"
                  onClick={handleRedeploy}
                  disabled={!canDeploy}
                >
                  <span className="icon icon-sm">refresh</span>
                  Redeploy Workflow
                </button>

                {isAnyDeploying && (
                  <p className="text-muted mt-2">
                    <span className="icon icon-sm">info</span>
                    Another workflow is currently being deployed.
                  </p>
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
        )}

        {isDeployed && !isActive && rdsDetails && (
          <>
            <div className="deploy-status-badge">
              <span className="icon icon-sm">check_circle</span>
              <span>Workflow Deployed</span>
            </div>
            <RDSConnectionDetails details={rdsDetails} />

            <button
              className="btn btn-primary mt-3"
              onClick={handleRedeploy}
              disabled={!canDeploy}
            >
              <span className="icon icon-sm">refresh</span>
              Redeploy Workflow
            </button>

            {isAnyDeploying && (
              <p className="text-muted mt-2">
                <span className="icon icon-sm">info</span>
                Another workflow is currently being deployed.
              </p>
            )}

            {showForm && (
              <S3CredentialsForm
                onSubmit={handleConnect}
                onCancel={() => setShowForm(false)}
              />
            )}

            {error && (
              <div className="deploy-error mt-3">
                <span className="icon icon-sm">error</span>
                <span>{error}</span>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default DeployConnector;
