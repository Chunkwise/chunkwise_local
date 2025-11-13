import { useEffect, useReducer, useState } from "react";
import type { Workflow, Chunker, Stage } from "./types";
import Header from "./components/Header";
import WorkflowList from "./components/WorkflowList";
import WorkflowDetails from "./components/WorkflowDetails";
import type { State } from "./reducers/workflowReducer";
import { getChunkers } from "./services/chunkers";
import { getFiles } from "./services/documents";
import {
  getWorkflows,
  createWorkflow as createWorkflowAPI,
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

  console.log(state.workflows);

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
    console.log("Useffect called - loading files");
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

  const handleUpdateWorkflow = (id: string, patch: Partial<Workflow>) => {
    dispatch(updateWorkflowAction(id, patch));
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
              state.selectedWorkflowId &&
              handleUpdateWorkflow(state.selectedWorkflowId, patch)
            }
          />
        </main>
      </div>
    </div>
  );
}
