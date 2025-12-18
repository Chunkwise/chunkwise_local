import { useState, useEffect } from "react";
import type { Tab } from "../types";

interface TabViewProps {
  workflowId?: string;
  hasEvaluation: boolean;
  switchToEvaluation?: boolean;
  switchToVisualization?: boolean;
  isDeployDisabled?: boolean;
  children: {
    visualization: React.ReactNode;
    evaluation: React.ReactNode;
    deploy: React.ReactNode;
  };
}

const TabView = ({
  workflowId,
  hasEvaluation,
  switchToEvaluation = false,
  switchToVisualization = false,
  isDeployDisabled = false,
  children,
}: TabViewProps) => {
  const [activeTab, setActiveTab] = useState<Tab>("visualization");

  // Reset to visualization
  useEffect(() => {
    setActiveTab("visualization");
  }, [workflowId]);

  // Switch to evaluation
  useEffect(() => {
    if (switchToEvaluation) {
      setActiveTab("evaluation");
    }
  }, [switchToEvaluation]);

  // Switch to visualization
  useEffect(() => {
    if (switchToVisualization) {
      setActiveTab("visualization");
    }
  }, [switchToVisualization]);

  return (
    <div className="tabs">
      <div className="tab-nav">
        <button
          className={`tab-btn ${activeTab === "visualization" ? "active" : ""}`}
          onClick={() => setActiveTab("visualization")}
        >
          <span className="icon icon-sm">bar_chart</span>
          Visualization
        </button>
        {!hasEvaluation ? (
          <div
            title="Run evaluation to see performance metrics"
            style={{ display: "inline-block" }}
          >
            <button
              className={`tab-btn ${
                activeTab === "evaluation" ? "active" : ""
              }`}
              disabled={true}
              style={{ pointerEvents: "none" }}
            >
              <span className="icon icon-sm">analytics</span>
              Evaluation
            </button>
          </div>
        ) : (
          <button
            className={`tab-btn ${activeTab === "evaluation" ? "active" : ""}`}
            onClick={() => setActiveTab("evaluation")}
          >
            <span className="icon icon-sm">analytics</span>
            Evaluation
          </button>
        )}
        {isDeployDisabled ? (
          <div
            title="Slumber Chunker is too expensive to deploy"
            style={{ display: "inline-block" }}
          >
            <button
              className={`tab-btn ${activeTab === "deploy" ? "active" : ""}`}
              disabled={true}
              style={{ pointerEvents: "none" }}
            >
              <span className="icon icon-sm">cloud_upload</span>
              Deploy
            </button>
          </div>
        ) : (
          <button
            className={`tab-btn ${activeTab === "deploy" ? "active" : ""}`}
            onClick={() => setActiveTab("deploy")}
          >
            <span className="icon icon-sm">cloud_upload</span>
            Deploy
          </button>
        )}
      </div>
      <div className="tab-content">
        {activeTab === "visualization"
          ? children.visualization
          : activeTab === "evaluation"
          ? children.evaluation
          : children.deploy}
      </div>
    </div>
  );
};

export default TabView;
