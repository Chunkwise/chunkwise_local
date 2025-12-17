import { useRef, useState, useEffect } from "react";
import type { 
  Workflow, 
  DeployWorkflowEvent, 
  S3Credentials, 
  RDSReadyPayload, 
  JobsStatus, 
  DeploySummary 
} from "../types";
import { deployWorkflow } from "../services/deploy";
import { getRdsSecretArn, setRdsSecretArn } from "../utils/storage";
import S3CredentialsForm from "./S3CredentialsForm";
import RDSConnectionDetails from "./RDSConnectionDetails";
import DeployProgress from "./DeployProgress";

interface DeployConnectorProps {
  workflow: Workflow;
  onWorkflowUpdate: (updates: Partial<Workflow>) => void;
  isAnyDeploying: boolean;
  onDeploymentChange: (isDeploying: boolean) => void;
}

const DeployConnector = ({ 
  workflow, 
  onWorkflowUpdate,
  isAnyDeploying,
  onDeploymentChange 
}: DeployConnectorProps) => {
  const [showForm, setShowForm] = useState(false);
  const [isDeploying, setIsDeploying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rdsDetails, setRdsDetails] = useState<RDSReadyPayload | null>(null);
  const [s3Bucket, setS3Bucket] = useState<string | null>(null);
  const [jobsStatus, setJobsStatus] = useState<JobsStatus | null>(null);
  const [summary, setSummary] = useState<DeploySummary | null>(null);
  const [noDocuments, setNoDocuments] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const controllerRef = useRef<AbortController | null>(null);
  const hasChunkingStrategy = Boolean(workflow.chunking_strategy);
  const isDeployed = Boolean(workflow.deploy_table_name);
  const storedArn = getRdsSecretArn();

  // Load existing RDS details if workflow is already deployed
  useEffect(() => {
    if (isDeployed && storedArn) {
      setRdsDetails({
        ok: true,
        stage: "rds-ready",
        endpoint: "",
        port: 5432,
        database: "",
        table_name: workflow.deploy_table_name!,
        secret_arn: storedArn,
        db_instance_identifier: "",
      });
    }
  }, [isDeployed, storedArn, workflow.deploy_table_name]);

  const handleEvent = (event: DeployWorkflowEvent) => {
    switch (event.type) {
      case "rds-ready":
        setRdsDetails(event.data);
        setRdsSecretArn(event.data.secret_arn);
        break;
      case "s3-connected":
        setS3Bucket(event.data.bucket);
        break;
      case "no-documents":
        setNoDocuments(true);
        break;
      case "jobs-updated":
        setJobsStatus(event.data.statuses);
        break;
      case "done":
        setSummary(event.data.summary ?? null);
        setIsComplete(true);
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
        setError(event.data.error);
        break;
    }
  };

  const handleConnect = async (credentials: S3Credentials) => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;

    setShowForm(false);
    setIsDeploying(true);
    onDeploymentChange(true);
    setError(null);
    setRdsDetails(null);
    setS3Bucket(null);
    setJobsStatus(null);
    setSummary(null);
    setNoDocuments(false);
    setIsComplete(false);

    try {
      await deployWorkflow({
        workflowId: workflow.id,
        credentials,
        signal: controller.signal,
        onEvent: handleEvent,
      });
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setError((err as Error).message || "Deployment failed");
      }
    } finally {
      setIsDeploying(false);
      onDeploymentChange(false);
      controllerRef.current = null;
    }
  };

  const isActive = isDeploying || isComplete;
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
              Connect your Amazon S3 bucket to deploy chunked documents to your vector database.
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
              summary={summary}
              noDocuments={noDocuments}
              isComplete={isComplete}
              error={error}
            />

            {rdsDetails && (
              <RDSConnectionDetails details={rdsDetails} />
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
          </>
        )}
      </div>
    </div>
  );
};

export default DeployConnector;
