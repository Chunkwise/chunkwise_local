import { useEffect, useReducer, useState } from "react";
import type { Workflow, Chunker, Stage } from "./types";
import type { State } from "./reducers/workflowReducer";
import Header from "./components/Header";
import WorkflowList from "./components/WorkflowList";
import WorkflowDetails from "./components/WorkflowDetails";
import WorkflowComparison from "./components/WorkflowComparison";
import { getChunkers } from "./services/chunkers";
import { getFiles } from "./services/documents";
import {
  getWorkflows,
  createWorkflow as createWorkflowAPI,
  updateWorkflow as updateWorkflowAPI,
  deleteWorkflow as deleteWorkflowAPI,
} from "./services/workflows";
import {
  workflowReducer,
  setWorkflowsAction,
  createWorkflowAction,
  selectWorkflowAction,
  updateWorkflowAction,
  deleteWorkflowAction,
} from "./reducers/workflowReducer";
import {
  comparisonReducer,
  enterComparisonModeAction,
  exitComparisonModeAction,
  toggleWorkflowSelectionAction,
} from "./reducers/comparisonReducer";

// Compute workflow stage based on its properties
function computeStage(workflow: Workflow): Stage {
  if (workflow.evaluation_metrics) {
    return "Evaluated";
  }
  if (workflow.chunking_strategy) {
    return "Configured";
  }
  return "Draft";
}

export default function App() {
  const [workflowState, workflowDispatch] = useReducer(workflowReducer, {
    workflows: [],
    selectedWorkflowId: undefined,
  } as State);
  const [comparisonState, comparisonDispatch] = useReducer(comparisonReducer, {
    isComparing: false,
    selectedWorkflowIds: [],
  });
  const [chunkers, setChunkers] = useState<Chunker[]>([]);
  const [availableFiles, setAvailableFiles] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Load workflows on mount
  useEffect(() => {
    getWorkflows()
      .then((workflows) => {
        const workflowsWithStage = workflows.map((workflow) => ({
          ...workflow,
          stage: computeStage(workflow),
        }));
        workflowDispatch(setWorkflowsAction(workflowsWithStage));
      })
      .catch((error) => {
        console.error("Failed to load workflows:", error);
        setError("Failed to load workflows from the server");
      });
  }, []);

  // Load chunkers on mount
  useEffect(() => {
    getChunkers()
      .then((data) => setChunkers(data))
      .catch((error) => {
        console.error("Failed to load chunkers:", error);
        setError("Failed to load chunkers from the server");
      });
  }, []);

  // Load available files on mount
  useEffect(() => {
    getFiles()
      .then((files) => setAvailableFiles([...files]))
      .catch((error) => {
        console.error("Failed to load files:", error);
        setError("Failed to load files from the server");
      });
  }, []);

  // Derive selected workflow
  const selectedWorkflow = workflowState.workflows.find(
    (workflow) => workflow.id === workflowState.selectedWorkflowId
  );

  // Derive compared workflows
  const comparedWorkflows = workflowState.workflows.filter((workflow) =>
    comparisonState.selectedWorkflowIds.includes(workflow.id)
  );

  // Handlers for workflow actions
  const handleCreateWorkflow = async (name: string) => {
    try {
      const newWorkflow = await createWorkflowAPI(name);
      const workflowWithStage = {
        ...newWorkflow,
        stage: computeStage(newWorkflow),
      };
      workflowDispatch(createWorkflowAction(workflowWithStage));
    } catch (error) {
      console.error("Failed to create workflow:", error);
      setError("Failed to create workflow");
    }
  };

  const handleSelectWorkflow = (id: string) => {
    workflowDispatch(selectWorkflowAction(id));
  };

  const handleUpdateWorkflow = async (id: string, patch: Partial<Workflow>) => {
    try {
      const updatedWorkflow = await updateWorkflowAPI(id, patch);
      const workflowWithStage = {
        ...updatedWorkflow,
        stage: computeStage(updatedWorkflow),
      };
      workflowDispatch(updateWorkflowAction(id, workflowWithStage));
    } catch (error) {
      console.error("Failed to update workflow:", error);
      setError("Failed to update workflow");
    }
  };

  const handleDeleteWorkflow = async (id: string) => {
    try {
      await deleteWorkflowAPI(id);
      workflowDispatch(deleteWorkflowAction(id));
    } catch (error) {
      console.error("Failed to delete workflow:", error);
      setError("Failed to delete workflow");
    }
  };

  // Handlers for comparison actions
  const handleEnterComparison = () => {
    comparisonDispatch(enterComparisonModeAction());
  };

  const handleExitComparison = () => {
    comparisonDispatch(exitComparisonModeAction());
  };

  const handleToggleWorkflowComparison = (id: string) => {
    comparisonDispatch(toggleWorkflowSelectionAction(id));
  };

  return (
    <div className="app-root">
      <Header />

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button
            className="error-close"
            onClick={() => setError(null)}
            aria-label="Dismiss error"
          >
            x
          </button>
        </div>
      )}

      <div className="main-layout">
        <aside className="sidebar">
          <WorkflowList
            workflows={workflowState.workflows}
            selectedId={workflowState.selectedWorkflowId}
            isComparing={comparisonState.isComparing}
            comparedWorkflowIds={comparisonState.selectedWorkflowIds}
            onCreateWorkflow={handleCreateWorkflow}
            onSelectWorkflow={handleSelectWorkflow}
            onDeleteWorkflow={handleDeleteWorkflow}
            onEnterComparison={handleEnterComparison}
            onExitComparison={handleExitComparison}
            onToggleWorkflowComparison={handleToggleWorkflowComparison}
          />
        </aside>

        <main className="main-content">
          {comparisonState.isComparing ? (
            <WorkflowComparison
              workflows={comparedWorkflows}
            />
          ) : (
            <WorkflowDetails
              chunkers={chunkers}
              availableFiles={availableFiles}
              workflow={selectedWorkflow}
              onUpdateWorkflow={(patch) =>
                handleUpdateWorkflow(selectedWorkflow!.id, patch)
              }
              onLocalUpdateWorkflow={(patch) => {
                const updatedWorkflow = { ...selectedWorkflow!, ...patch };
                const workflowWithStage = {
                  ...updatedWorkflow,
                  stage: computeStage(updatedWorkflow as Workflow),
                };
                workflowDispatch(
                  updateWorkflowAction(selectedWorkflow!.id, workflowWithStage)
                );
              }}
            />
          )}
        </main>
      </div>
    </div>
  );
}
