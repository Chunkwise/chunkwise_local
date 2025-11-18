import { useEffect, useRef, useState } from "react";
import type { Workflow } from "../types";
import { connectToS3, type S3Credentials } from "../services/deploy";
import S3CredentialsForm from "./S3CredentialsForm";
import RDSConnectionDetails from "./RDSConnectionDetails";

interface DeployConnectorProps {
  workflow: Workflow;
}

type ConnectionInfo = {
  bucketName: string;
  rdsEndpoint: string;
};

const DeployConnector = ({ workflow }: DeployConnectorProps) => {
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [connectionInfo, setConnectionInfo] = useState<ConnectionInfo | null>(
    null
  );
  const progressTimerRef = useRef<number | null>(null);

  const hasChunkingStrategy = Boolean(workflow.chunking_strategy);

  useEffect(() => {
    return () => {
      if (progressTimerRef.current) {
        clearInterval(progressTimerRef.current);
      }
    };
  }, []);

  const startProgress = () => {
    if (progressTimerRef.current) {
      clearInterval(progressTimerRef.current);
    }
    setProgress(12);
    progressTimerRef.current = window.setInterval(() => {
      setProgress((previous) => {
        if (previous >= 90) {
          return previous;
        }
        const increment = Math.random() * 12;
        return Math.min(previous + increment, 92);
      });
    }, 180);
  };

  const finishProgress = (didSucceed: boolean) => {
    if (progressTimerRef.current) {
      clearInterval(progressTimerRef.current);
      progressTimerRef.current = null;
    }

    if (didSucceed) {
      setProgress(100);
      setTimeout(() => {
        setProgress(0);
      }, 600);
    } else {
      setProgress(0);
    }
  };

  const handleToggleForm = () => {
    if (!hasChunkingStrategy) return;
    setIsFormVisible((previous) => !previous);
    setError(null);
    if (!isFormVisible) {
      setConnectionInfo(null);
    }
  };

  const handleCancel = () => {
    setIsFormVisible(false);
    setError(null);
  };

  const handleConnect = async (credentials: S3Credentials) => {
    if (!workflow.chunking_strategy) {
      setError("Select a chunker before connecting to Amazon S3.");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setConnectionInfo(null);
    startProgress();

    try {
      const response = await connectToS3({
        credentials,
        chunkingStrategy: workflow.chunking_strategy,
        workflowId: workflow.id,
      });
      setConnectionInfo({
        bucketName: response.bucket_name,
        rdsEndpoint: response.rds_endpoint,
      });
      setIsFormVisible(false);
      finishProgress(true);
    } catch (connectionError) {
      console.error("Failed to connect to S3", connectionError);
      setError(
        "Unable to connect to Amazon S3. Please verify the credentials."
      );
      finishProgress(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="details-row">
      <h2 className="section-title">Deploy</h2>
      <div className="box">
        <div className="muted">
          Connect your Amazon S3 bucket to import and deploy chunked data.
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

        {isSubmitting || progress > 0 ? (
          <div className="progress-bar" aria-hidden={!isSubmitting}>
            <div
              className="progress-fill"
              style={{ width: `${progress}%`, background: "#2b6cb0" }}
            />
          </div>
        ) : null}

        {isFormVisible && (
          <S3CredentialsForm
            onSubmit={handleConnect}
            onCancel={handleCancel}
            isSubmitting={isSubmitting}
          />
        )}

        {error && <div className="error">{error}</div>}

        {connectionInfo && (
          <RDSConnectionDetails
            rdsEndpoint={connectionInfo.rdsEndpoint}
            bucketName={connectionInfo.bucketName}
          />
        )}
      </div>
    </div>
  );
};

export default DeployConnector;
