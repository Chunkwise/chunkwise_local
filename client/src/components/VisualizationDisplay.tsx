interface VisualizationDisplayProps {
  html: string;
}

const VisualizationDisplay = ({ html }: VisualizationDisplayProps) => {
  return (
    <div className="details-row">
      <h2 className="section-title">Visualization</h2>
      <div className="box">
        <div
          className="visualization-container"
          dangerouslySetInnerHTML={html ? { __html: html } : undefined}
        />
      </div>
    </div>
  );
};

export default VisualizationDisplay;
