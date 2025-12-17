import type { RDSReadyPayload, JobsStatus, DeploySummary } from "../types";

interface DeployProgressProps {
  rdsDetails: RDSReadyPayload | null;
  s3Bucket: string | null;
  jobsStatus: JobsStatus | null;
  summary: DeploySummary | null;
  noDocuments: boolean;
  isComplete: boolean;
  error: string | null;
}

const DeployProgress = ({
  rdsDetails,
  s3Bucket,
  jobsStatus,
  summary,
  noDocuments,
  isComplete,
  error,
}: DeployProgressProps) => {
  return (
    <div className="deploy-progress">
      <div className="deploy-steps">
        <div className={`deploy-step ${rdsDetails ? "success" : "running"}`}>
          <span className={`icon icon-sm deploy-step-icon ${rdsDetails ? "success" : "running spinner"}`}>
            {rdsDetails ? "check_circle" : "sync"}
          </span>
          <span className="deploy-step-label">Database ready</span>
          {rdsDetails && (
            <span className="deploy-step-detail">{rdsDetails.db_instance_identifier}</span>
          )}
        </div>

        <div className={`deploy-step ${s3Bucket ? "success" : rdsDetails ? "running" : "pending"}`}>
          <span className={`icon icon-sm deploy-step-icon ${s3Bucket ? "success" : rdsDetails ? "running spinner" : "pending"}`}>
            {s3Bucket ? "check_circle" : rdsDetails ? "sync" : "radio_button_unchecked"}
          </span>
          <span className="deploy-step-label">S3 bucket verified</span>
          {s3Bucket && <span className="deploy-step-detail">{s3Bucket}</span>}
        </div>

        {noDocuments ? (
          <div className="deploy-step success">
            <span className="icon icon-sm deploy-step-icon success">check_circle</span>
            <span className="deploy-step-label">No documents found</span>
            <span className="deploy-step-detail">No .txt or .md files in bucket</span>
          </div>
        ) : (
          <div className={`deploy-step ${isComplete ? "success" : s3Bucket ? "running" : "pending"}`}>
            <span className={`icon icon-sm deploy-step-icon ${isComplete ? "success" : s3Bucket ? "running spinner" : "pending"}`}>
              {isComplete ? "check_circle" : s3Bucket ? "sync" : "radio_button_unchecked"}
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

      {isComplete && summary && (
        <div className="deploy-complete mt-3">
          <span className="icon icon-sm">check_circle</span>
          <span>
            Deployed {summary.documents_processed} document{summary.documents_processed !== 1 ? "s" : ""} to <strong>{summary.table}</strong>
          </span>
        </div>
      )}

      {isComplete && noDocuments && (
        <div className="deploy-complete mt-3">
          <span className="icon icon-sm">info</span>
          <span>Deployment complete. Add documents to your S3 bucket to process them.</span>
        </div>
      )}
    </div>
  );
};

export default DeployProgress;
