import type { RDSReadyPayload, JobsStatus, DeploySummary } from "../types";

interface DeployProgressProps {
  status: "idle" | "running" | "success" | "error";
  rdsDetails: RDSReadyPayload | null;
  s3Bucket: string | null;
  jobsStatus: JobsStatus | null;
  summary: DeploySummary | null;
  noDocuments: boolean;
  error: string | null;
}

interface StepProps {
  label: string;
  detail?: string;
  status: "pending" | "running" | "success" | "error";
}

const StepItem = ({ label, detail, status }: StepProps) => {
  const getIcon = () => {
    switch (status) {
      case "success":
        return <span className="icon icon-sm deploy-step-icon success">check_circle</span>;
      case "error":
        return <span className="icon icon-sm deploy-step-icon error">cancel</span>;
      case "running":
        return <span className="icon icon-sm deploy-step-icon running spinner">sync</span>;
      default:
        return <span className="icon icon-sm deploy-step-icon pending">radio_button_unchecked</span>;
    }
  };

  return (
    <div className={`deploy-step ${status}`}>
      {getIcon()}
      <span className="deploy-step-label">{label}</span>
      {detail && <span className="deploy-step-detail">{detail}</span>}
    </div>
  );
};

const DeployProgress = ({
  status,
  rdsDetails,
  s3Bucket,
  jobsStatus,
  summary,
  noDocuments,
  error,
}: DeployProgressProps) => {
  const getStepStatus = (
    completed: boolean,
    hasError: boolean
  ): StepProps["status"] => {
    if (hasError) return "error";
    if (completed) return "success";
    if (status === "running") return "running";
    return "pending";
  };

  const isRdsComplete = rdsDetails !== null;
  const isS3Complete = s3Bucket !== null;
  const isJobsComplete = status === "success" || noDocuments;
  const hasError = status === "error";

  // Determine which step has the error
  const rdsError = hasError && !isRdsComplete;
  const s3Error = hasError && isRdsComplete && !isS3Complete;
  const jobsError = hasError && isRdsComplete && isS3Complete && !isJobsComplete;

  return (
    <div className="deploy-progress">
      <div className="deploy-steps">
        <StepItem
          label="Database ready"
          detail={isRdsComplete ? rdsDetails.db_instance_identifier : undefined}
          status={getStepStatus(isRdsComplete, rdsError)}
        />

        <StepItem
          label="S3 bucket verified"
          detail={isS3Complete ? s3Bucket : undefined}
          status={getStepStatus(isS3Complete, s3Error)}
        />

        {noDocuments ? (
          <StepItem
            label="No documents found"
            detail="No .txt or .md files in bucket"
            status="success"
          />
        ) : (
          <StepItem
            label="Processing documents"
            detail={
              jobsStatus
                ? `${jobsStatus.succeeded}/${jobsStatus.total} complete${
                    jobsStatus.failed > 0 ? `, ${jobsStatus.failed} failed` : ""
                  }`
                : undefined
            }
            status={getStepStatus(isJobsComplete, jobsError)}
          />
        )}
      </div>

      {error && (
        <div className="deploy-error mt-3">
          <span className="icon icon-sm">error</span>
          <span>{error}</span>
        </div>
      )}

      {status === "success" && summary && (
        <div className="deploy-complete mt-3">
          <span className="icon icon-sm">check_circle</span>
          <span>
            Deployed {summary.documents_processed} document
            {summary.documents_processed !== 1 ? "s" : ""} to{" "}
            <strong>{summary.table}</strong>
          </span>
        </div>
      )}

      {status === "success" && noDocuments && (
        <div className="deploy-complete mt-3">
          <span className="icon icon-sm">info</span>
          <span>Deployment complete. Add documents to your S3 bucket to process them.</span>
        </div>
      )}
    </div>
  );
};

export default DeployProgress;
