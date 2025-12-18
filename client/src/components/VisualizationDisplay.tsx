interface VisualizationDisplayProps {
  html: string;
}

const VisualizationDisplay = ({ html }: VisualizationDisplayProps) => {
  return (
    <div className="section">
      <h3 className="section-header">
        <span className="icon">preview</span>
        <span className="title-sm">Visualization</span>
      </h3>
      <div className="card">
        <div
          className="visualization"
          dangerouslySetInnerHTML={html ? { __html: html } : undefined}
        />
      </div>
    </div>
  );
};

export default VisualizationDisplay;
