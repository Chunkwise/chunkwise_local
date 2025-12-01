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
    <div className="tabs">
      <div className="tab-nav">
        <button
          className={`tab-btn ${activeTab === "visualization" ? "active" : ""}`}
          onClick={() => setActiveTab("visualization")}
        >
          <span className="icon icon-sm">bar_chart</span>
          Visualization
        </button>
        <button
          className={`tab-btn ${activeTab === "evaluation" ? "active" : ""}`}
          onClick={() => setActiveTab("evaluation")}
          disabled={!hasEvaluation}
        >
          <span className="icon icon-sm">analytics</span>
          Evaluation
        </button>
        <button
          className={`tab-btn ${activeTab === "deploy" ? "active" : ""}`}
          onClick={() => setActiveTab("deploy")}
        >
          <span className="icon icon-sm">cloud_upload</span>
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
