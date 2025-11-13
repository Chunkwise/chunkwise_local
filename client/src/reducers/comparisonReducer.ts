export type ComparisonState = {
  isComparing: boolean;
  selectedWorkflowIds: string[];
};

export type ComparisonAction =
  | { type: "ENTER_COMPARISON_MODE" }
  | { type: "EXIT_COMPARISON_MODE" }
  | { type: "TOGGLE_WORKFLOW_SELECTION"; payload: string };

const MAX_SELECTIONS = 4;

export const comparisonReducer = (
  state: ComparisonState,
  action: ComparisonAction
): ComparisonState => {
  switch (action.type) {
    case "ENTER_COMPARISON_MODE":
      return {
        ...state,
        isComparing: true,
        selectedWorkflowIds: [],
      };
    case "EXIT_COMPARISON_MODE":
      return {
        isComparing: false,
        selectedWorkflowIds: [],
      };
    case "TOGGLE_WORKFLOW_SELECTION": {
      const id = action.payload;
      const isCurrentlySelected = state.selectedWorkflowIds.includes(id);

      if (isCurrentlySelected) {
        return {
          ...state,
          selectedWorkflowIds: state.selectedWorkflowIds.filter(
            (workflowId) => workflowId !== id
          ),
        };
      } else {
        if (state.selectedWorkflowIds.length >= MAX_SELECTIONS) {
          return state;
        }
        return {
          ...state,
          selectedWorkflowIds: [...state.selectedWorkflowIds, id],
        };
      }
    }
    default:
      return state;
  }
};

export const enterComparisonModeAction = (): ComparisonAction => ({
  type: "ENTER_COMPARISON_MODE",
});

export const exitComparisonModeAction = (): ComparisonAction => ({
  type: "EXIT_COMPARISON_MODE",
});

export const toggleWorkflowSelectionAction = (
  id: string
): ComparisonAction => ({
  type: "TOGGLE_WORKFLOW_SELECTION",
  payload: id,
});
