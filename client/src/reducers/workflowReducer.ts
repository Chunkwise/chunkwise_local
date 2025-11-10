import type { Workflow } from "../types";

export type State = {
  workflows: Workflow[];
  selectedWorkflowId?: string;
};

export type Action =
  | { type: "INIT"; workflows: Workflow[] }
  | { type: "CREATE_WORKFLOW"; workflow: Workflow }
  | { type: "SELECT_WORKFLOW"; id?: string }
  | { type: "UPDATE_WORKFLOW"; id: string; patch: Partial<Workflow> }
  | { type: "DELETE_WORKFLOW"; id: string };

export function workflowReducer(state: State, action: Action): State {
  switch (action.type) {
    case "INIT":
      return {
        ...state,
        workflows: action.workflows,
        selectedWorkflowId: action.workflows[0]?.id,
      };
    case "CREATE_WORKFLOW":
      return {
        ...state,
        workflows: [action.workflow, ...state.workflows],
        selectedWorkflowId: action.workflow.id,
      };
    case "SELECT_WORKFLOW":
      return { ...state, selectedWorkflowId: action.id };
    case "UPDATE_WORKFLOW":
      return {
        ...state,
        workflows: state.workflows.map((w) =>
          w.id === action.id ? { ...w, ...action.patch } : w
        ),
      };
    case "DELETE_WORKFLOW": {
      const remaining = state.workflows.filter((w) => w.id !== action.id);
      const selected =
        state.selectedWorkflowId === action.id
          ? remaining[0]?.id
          : state.selectedWorkflowId;
      return { workflows: remaining, selectedWorkflowId: selected };
    }
    default:
      return state;
  }
}
