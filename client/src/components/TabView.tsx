import { useState, useEffect } from "react";
import type { Tab } from "../types";

interface TabViewProps {
  workflowId?: string;
  hasEvaluation: boolean;
  switchToEvaluation?: boolean;
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

  return (
    <div className="tab-view">
      <div className="tab-nav">
        <button
          className={`tab-button ${
            activeTab === "visualization" ? "active" : ""
          }`}
          onClick={() => setActiveTab("visualization")}
        >
          Visualization
        </button>
        <button
          className={`tab-button ${activeTab === "evaluation" ? "active" : ""}`}
          onClick={() => setActiveTab("evaluation")}
          disabled={!hasEvaluation}
        >
          Evaluation
        </button>
        <button
          className={`tab-button ${activeTab === "deploy" ? "active" : ""}`}
          onClick={() => setActiveTab("deploy")}
        >
          Deploy
        </button>
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
