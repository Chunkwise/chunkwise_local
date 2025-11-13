import type { Workflow } from "../types";

export type State = {
  workflows: Workflow[];
  selectedWorkflowId?: string;
};

export type Action =
  | { type: "SET_WORKFLOWS"; payload: Workflow[] }
  | { type: "CREATE_WORKFLOW"; payload: Workflow }
  | { type: "SELECT_WORKFLOW"; payload: string }
  | {
      type: "UPDATE_WORKFLOW";
      payload: { id: string; patch: Partial<Workflow> };
    }
  | { type: "DELETE_WORKFLOW"; payload: string };

export const workflowReducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "SET_WORKFLOWS":
      return {
        ...state,
        workflows: action.payload,
      };
    case "CREATE_WORKFLOW":
      return {
        workflows: [action.payload, ...state.workflows],
        selectedWorkflowId: action.payload.id,
      };
    case "SELECT_WORKFLOW":
      return { ...state, selectedWorkflowId: action.payload };
    case "UPDATE_WORKFLOW":
      return {
        ...state,
        workflows: state.workflows.map((workflow) =>
          workflow.id === action.payload.id
            ? { ...workflow, ...action.payload.patch }
            : workflow
        ),
      };
    case "DELETE_WORKFLOW": {
      const remaining = state.workflows.filter(
        (workflow) => workflow.id !== action.payload
      );
      const selected =
        state.selectedWorkflowId === action.payload
          ? remaining[0]?.id
          : state.selectedWorkflowId;
      return { workflows: remaining, selectedWorkflowId: selected };
    }
    default:
      return state;
  }
};

export const setWorkflowsAction = (workflows: Workflow[]): Action => ({
  type: "SET_WORKFLOWS",
  payload: workflows,
});

export const createWorkflowAction = (workflow: Workflow): Action => ({
  type: "CREATE_WORKFLOW",
  payload: workflow,
});

export const selectWorkflowAction = (id: string): Action => ({
  type: "SELECT_WORKFLOW",
  payload: id,
});

export const updateWorkflowAction = (
  id: string,
  patch: Partial<Workflow>
): Action => ({
  type: "UPDATE_WORKFLOW",
  payload: { id, patch },
});

export const deleteWorkflowAction = (id: string): Action => ({
  type: "DELETE_WORKFLOW",
  payload: id,
});
