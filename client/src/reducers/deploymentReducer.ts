import type { DeploymentState, RDSReadyPayload, JobsStatus } from "../types";

export type DeploymentStates = Record<string, DeploymentState>;

export type DeploymentAction =
  | { type: "START_DEPLOYMENT"; payload: { workflowId: string } }
  | {
      type: "SET_RDS_DETAILS";
      payload: { workflowId: string; rdsDetails: RDSReadyPayload };
    }
  | { type: "SET_S3_BUCKET"; payload: { workflowId: string; s3Bucket: string } }
  | { type: "SET_NO_DOCUMENTS"; payload: { workflowId: string } }
  | {
      type: "SET_JOBS_STATUS";
      payload: { workflowId: string; jobsStatus: JobsStatus };
    }
  | { type: "SET_COMPLETE"; payload: { workflowId: string } }
  | { type: "SET_ERROR"; payload: { workflowId: string; error: string } }
  | { type: "RESET_DEPLOYMENT"; payload: { workflowId: string } };

const getInitialDeploymentState = (): DeploymentState => ({
  isDeploying: false,
  rdsDetails: null,
  s3Bucket: null,
  jobsStatus: null,
  noDocuments: false,
  isComplete: false,
  error: null,
});

export const deploymentReducer = (
  state: DeploymentStates,
  action: DeploymentAction
): DeploymentStates => {
  const { workflowId } = action.payload;
  const currentState = state[workflowId] || getInitialDeploymentState();

  switch (action.type) {
    case "START_DEPLOYMENT":
      return {
        ...state,
        [workflowId]: {
          ...getInitialDeploymentState(),
          isDeploying: true,
        },
      };

    case "SET_RDS_DETAILS":
      return {
        ...state,
        [workflowId]: {
          ...currentState,
          rdsDetails: action.payload.rdsDetails,
        },
      };

    case "SET_S3_BUCKET":
      return {
        ...state,
        [workflowId]: {
          ...currentState,
          s3Bucket: action.payload.s3Bucket,
        },
      };

    case "SET_NO_DOCUMENTS":
      return {
        ...state,
        [workflowId]: {
          ...currentState,
          noDocuments: true,
        },
      };

    case "SET_JOBS_STATUS":
      return {
        ...state,
        [workflowId]: {
          ...currentState,
          jobsStatus: action.payload.jobsStatus,
        },
      };

    case "SET_COMPLETE":
      return {
        ...state,
        [workflowId]: {
          ...currentState,
          isComplete: true,
        },
      };

    case "SET_ERROR":
      return {
        ...state,
        [workflowId]: {
          ...currentState,
          error: action.payload.error,
        },
      };

    case "RESET_DEPLOYMENT":
      return {
        ...state,
        [workflowId]: getInitialDeploymentState(),
      };

    default:
      return state;
  }
};

// Action creators
export const startDeploymentAction = (
  workflowId: string
): DeploymentAction => ({
  type: "START_DEPLOYMENT",
  payload: { workflowId },
});

export const setRdsDetailsAction = (
  workflowId: string,
  rdsDetails: RDSReadyPayload
): DeploymentAction => ({
  type: "SET_RDS_DETAILS",
  payload: { workflowId, rdsDetails },
});

export const setS3BucketAction = (
  workflowId: string,
  s3Bucket: string
): DeploymentAction => ({
  type: "SET_S3_BUCKET",
  payload: { workflowId, s3Bucket },
});

export const setNoDocumentsAction = (workflowId: string): DeploymentAction => ({
  type: "SET_NO_DOCUMENTS",
  payload: { workflowId },
});

export const setJobsStatusAction = (
  workflowId: string,
  jobsStatus: JobsStatus
): DeploymentAction => ({
  type: "SET_JOBS_STATUS",
  payload: { workflowId, jobsStatus },
});

export const setCompleteAction = (workflowId: string): DeploymentAction => ({
  type: "SET_COMPLETE",
  payload: { workflowId },
});

export const setErrorAction = (
  workflowId: string,
  error: string
): DeploymentAction => ({
  type: "SET_ERROR",
  payload: { workflowId, error },
});

export const resetDeploymentAction = (
  workflowId: string
): DeploymentAction => ({
  type: "RESET_DEPLOYMENT",
  payload: { workflowId },
});
