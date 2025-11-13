import { useEffect, useReducer, useState } from "react";
import type { Workflow, Chunker, Stage } from "./types";
import type { State } from "./reducers/workflowReducer";
import Header from "./components/Header";
import WorkflowList from "./components/WorkflowList";
import WorkflowDetails from "./components/WorkflowDetails";
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
  const [state, dispatch] = useReducer(workflowReducer, {
    workflows: [],
    selectedWorkflowId: undefined,
  } as State);
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
        dispatch(setWorkflowsAction(workflowsWithStage));
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

  const selectedWorkflow = state.workflows.find(
    (workflow) => workflow.id === state.selectedWorkflowId
  );

  const handleCreateWorkflow = async (name: string) => {
    try {
      const newWorkflow = await createWorkflowAPI(name);
      const workflowWithStage = {
        ...newWorkflow,
        stage: computeStage(newWorkflow),
      };
      dispatch(createWorkflowAction(workflowWithStage));
    } catch (error) {
      console.error("Failed to create workflow:", error);
      setError("Failed to create workflow");
    }
  };

  const handleSelectWorkflow = (id: string) => {
    dispatch(selectWorkflowAction(id));
  };

  const handleUpdateWorkflow = async (id: string, patch: Partial<Workflow>) => {
    try {
      const updatedWorkflow = await updateWorkflowAPI(id, patch);
      const workflowWithStage = {
        ...updatedWorkflow,
        stage: computeStage(updatedWorkflow),
      };
      dispatch(updateWorkflowAction(id, workflowWithStage));
    } catch (error) {
      console.error("Failed to update workflow:", error);
      setError("Failed to update workflow");
    }
  };

  const handleDeleteWorkflow = async (id: string) => {
    try {
      await deleteWorkflowAPI(id);
      dispatch(deleteWorkflowAction(id));
    } catch (error) {
      console.error("Failed to delete workflow:", error);
      setError("Failed to delete workflow");
    }
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
            workflows={state.workflows}
            selectedId={state.selectedWorkflowId}
            onCreateWorkflow={handleCreateWorkflow}
            onSelectWorkflow={handleSelectWorkflow}
            onDeleteWorkflow={handleDeleteWorkflow}
          />
        </aside>

        <main className="main-content">
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
              dispatch(
                updateWorkflowAction(selectedWorkflow!.id, workflowWithStage)
              );
            }}
          />
        </main>
      </div>
    </div>
  );
}
