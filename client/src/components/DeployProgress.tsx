import type { RDSReadyPayload, JobsStatus } from "../types";

interface DeployProgressProps {
  rdsDetails: RDSReadyPayload | null;
  s3Bucket: string | null;
  jobsStatus: JobsStatus | null;
  noDocuments: boolean;
  isComplete: boolean;
  error: string | null;
}

const DeployProgress = ({
  rdsDetails,
  s3Bucket,
  jobsStatus,
  noDocuments,
  isComplete,
  error,
}: DeployProgressProps) => {
  const getStepClass = (isSuccess: boolean, isRunning: boolean) =>
    isSuccess ? "success" : isRunning ? "running" : "pending";

  const getIconClass = (isSuccess: boolean, isRunning: boolean) =>
    `icon icon-sm deploy-step-icon ${getStepClass(isSuccess, isRunning)}${
      isRunning ? " spinner" : ""
    }`;

  const getIcon = (isSuccess: boolean, isRunning: boolean) =>
    isSuccess ? "check_circle" : isRunning ? "sync" : "radio_button_unchecked";

  return (
    <div className="deploy-progress">
      <div className="deploy-steps">
        <div
          className={`deploy-step ${getStepClass(!!rdsDetails, !rdsDetails)}`}
        >
          <span className={getIconClass(!!rdsDetails, !rdsDetails)}>
            {getIcon(!!rdsDetails, !rdsDetails)}
          </span>
          <span className="deploy-step-label">Database ready</span>
          {rdsDetails && (
            <span className="deploy-step-detail">
              {rdsDetails.db_instance_identifier}
            </span>
          )}
        </div>
        <div
          className={`deploy-step ${getStepClass(
            !!s3Bucket,
            !!rdsDetails && !s3Bucket
          )}`}
        >
          <span className={getIconClass(!!s3Bucket, !!rdsDetails && !s3Bucket)}>
            {getIcon(!!s3Bucket, !!rdsDetails && !s3Bucket)}
          </span>
          <span className="deploy-step-label">S3 bucket verified</span>
          {s3Bucket && <span className="deploy-step-detail">{s3Bucket}</span>}
        </div>

        {noDocuments ? (
          <div className="deploy-step success">
            <span className="icon icon-sm deploy-step-icon success">
              check_circle
            </span>
            <span className="deploy-step-label">No documents found</span>
            <span className="deploy-step-detail">
              No .txt or .md files in bucket
            </span>
          </div>
        ) : (
          <div
            className={`deploy-step ${getStepClass(
              isComplete,
              !!s3Bucket && !isComplete
            )}`}
          >
            <span
              className={getIconClass(isComplete, !!s3Bucket && !isComplete)}
            >
              {getIcon(isComplete, !!s3Bucket && !isComplete)}
            </span>
            <span className="deploy-step-label">Processing documents</span>
            {jobsStatus && (
              <span className="deploy-step-detail">
                {jobsStatus.succeeded}/{jobsStatus.total} complete
                {jobsStatus.failed > 0 && `, ${jobsStatus.failed} failed`}
              </span>
            )}
          </div>
        )}
      </div>

      {error && (
        <div className="deploy-error mt-3">
          <span className="icon icon-sm">error</span>
          <span>{error}</span>
        </div>
      )}

      {isComplete && (
        <div className="deploy-complete mt-3">
          <span className="icon icon-sm">
            {noDocuments ? "info" : "check_circle"}
          </span>
          <span>
            {noDocuments
              ? "Deployment complete. Add documents to your S3 bucket to process them."
              : "Deployment complete!"}
          </span>
        </div>
      )}
    </div>
  );
};

export default DeployProgress;
