import { useEffect, useReducer, useState } from "react";
import { ZodError } from "zod";
import type { Workflow, Chunker } from "./types";
import type { State } from "./reducers/workflowReducer";
import Header from "./components/Header";
import WorkflowList from "./components/WorkflowList";
import WorkflowDetails from "./components/WorkflowDetails";
import WorkflowComparison from "./components/WorkflowComparison";
import ErrorMessage from "./components/ErrorMessage";
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
  patchWorkflowAction,
  deleteWorkflowAction,
  computeWorkflowStage,
} from "./reducers/workflowReducer";
import {
  comparisonReducer,
  enterComparisonModeAction,
  exitComparisonModeAction,
  toggleWorkflowSelectionAction,
} from "./reducers/comparisonReducer";

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
  const [isLoadingWorkflows, setIsLoadingWorkflows] = useState(true);
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);
  const [availableFiles, setAvailableFiles] = useState<string[]>([]);
  const [isDeploymentActive, setIsDeploymentActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load workflows on mount
  useEffect(() => {
    setIsLoadingWorkflows(true);
    getWorkflows()
      .then((workflows) => {
        const workflowsWithStage = workflows.map((workflow) => ({
          ...workflow,
          stage: computeWorkflowStage(workflow),
        }));
        workflowsWithStage.sort(
          (first, second) =>
            new Date(second.created_at).getTime() -
            new Date(first.created_at).getTime()
        );
        workflowDispatch(setWorkflowsAction(workflowsWithStage));
      })
      .catch((error: unknown) => {
        console.error("Failed to load workflows:", error);
        if (error instanceof ZodError) {
          setError("The server returned workflow data in an unexpected format");
        } else {
          setError("Failed to load workflows from the server");
        }
      })
      .finally(() => {
        setIsLoadingWorkflows(false);
      });
  }, []);

  // Load chunkers on mount
  useEffect(() => {
    getChunkers()
      .then((data) => setChunkers(data))
      .catch((error: unknown) => {
        console.error("Failed to load chunkers:", error);
        if (error instanceof ZodError) {
          setError("The server returned chunker data in an unexpected format");
        } else {
          setError("Failed to load chunkers from the server");
        }
      });
  }, []);

  // Load available files on mount
  useEffect(() => {
    setIsLoadingFiles(true);
    getFiles()
      .then((files) => setAvailableFiles([...files]))
      .catch((error: unknown) => {
        console.error("Failed to load files:", error);
        if (error instanceof ZodError) {
          setError(
            "The server returned file information in an unexpected format"
          );
        } else {
          setError("Failed to load files from the server");
        }
      })
      .finally(() => {
        setIsLoadingFiles(false);
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
    const tempId = `temp-${Date.now()}`;
    const optimisticWorkflow: Workflow = {
      id: tempId,
      title: name,
      created_at: new Date().toISOString(),
      stage: "Draft",
    };
    workflowDispatch(createWorkflowAction(optimisticWorkflow));

    try {
      const newWorkflow = await createWorkflowAPI(name);
      const workflowWithStage = {
        ...newWorkflow,
        stage: computeWorkflowStage(newWorkflow),
      };
      workflowDispatch(deleteWorkflowAction(tempId));
      workflowDispatch(createWorkflowAction(workflowWithStage));
    } catch (error: unknown) {
      workflowDispatch(deleteWorkflowAction(tempId));
      console.error("Failed to create workflow:", error);
      if (error instanceof ZodError) {
        setError(
          "The server returned the created workflow in an unexpected format"
        );
      } else {
        setError("Failed to create workflow");
      }
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
        stage: computeWorkflowStage(updatedWorkflow),
      };
      workflowDispatch(updateWorkflowAction(id, workflowWithStage));
    } catch (error: unknown) {
      console.error("Failed to update workflow:", error);
      if (error instanceof ZodError) {
        setError(
          "The server returned the updated workflow in an unexpected format"
        );
      } else {
        setError("Failed to update workflow");
      }
    }
  };

  const handlePatchWorkflow = async (id: string, patch: Partial<Workflow>) => {
    workflowDispatch(patchWorkflowAction(id, patch));
  };

  const handleDeleteWorkflow = async (id: string) => {
    try {
      await deleteWorkflowAPI(id);
      workflowDispatch(deleteWorkflowAction(id));
    } catch (error: unknown) {
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
    <div className="app">
      <Header />

      {error && (
        <ErrorMessage
          message={error}
          variant="banner"
          onDismiss={() => setError(null)}
        />
      )}

      <div className="layout">
        <aside className="sidebar">
          <WorkflowList
            isLoadingWorkflows={isLoadingWorkflows}
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

        <main className="content">
          {comparisonState.isComparing ? (
            <WorkflowComparison
              chunkers={chunkers}
              workflows={comparedWorkflows}
            />
          ) : (
            <WorkflowDetails
              chunkers={chunkers}
              isLoadingFiles={isLoadingFiles}
              availableFiles={availableFiles}
              workflow={selectedWorkflow}
              onUpdateWorkflow={(patch) =>
                handleUpdateWorkflow(selectedWorkflow!.id, patch)
              }
              onPatchWorkflow={(patch) =>
                handlePatchWorkflow(selectedWorkflow!.id, patch)
              }
              isAnyDeploying={isDeploymentActive}
              onDeploymentChange={setIsDeploymentActive}
            />
          )}
        </main>
      </div>
    </div>
  );
}
