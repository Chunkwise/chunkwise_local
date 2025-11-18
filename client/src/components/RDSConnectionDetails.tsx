import { useState } from "react";

interface RDSConnectionDetailsProps {
  rdsEndpoint: string;
  bucketName: string;
}

const RDSConnectionDetails = ({
  rdsEndpoint,
  bucketName,
}: RDSConnectionDetailsProps) => {
  const [copyStatus, setCopyStatus] = useState<"idle" | "copied" | "error">(
    "idle"
  );

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(rdsEndpoint);
      setCopyStatus("copied");
      setTimeout(() => setCopyStatus("idle"), 2000);
    } catch (error) {
      console.error("Failed to copy RDS endpoint", error);
      setCopyStatus("error");
      setTimeout(() => setCopyStatus("idle"), 2000);
    }
  };

  return (
    <div className="deployment-summary" aria-live="polite">
      <div className="muted">
        Successfully connected to bucket <strong>{bucketName}</strong>.
      </div>
      <div className="muted" style={{ marginTop: "8px" }}>
        Use the RDS endpoint below to connect your downstream applications:
      </div>
      <div
        className="file-preview"
        style={{
          marginTop: "12px",
          alignItems: "stretch",
          gap: "12px",
          flexWrap: "wrap",
        }}
      >
        <div
          style={{
            flex: "1 1 260px",
            padding: "8px 10px",
            border: "1px solid var(--border)",
            borderRadius: "6px",
            background: "#f9fafb",
            fontFamily: "monospace",
            wordBreak: "break-all",
          }}
        >
          {rdsEndpoint}
        </div>
        <button className="btn btn-sm" type="button" onClick={handleCopy}>
          Copy link
        </button>
      </div>
      {copyStatus === "copied" && (
        <div className="muted" style={{ color: "#2b6cb0", marginTop: "8px" }}>
          Copied to clipboard
        </div>
      )}
      {copyStatus === "error" && (
        <div className="error" style={{ marginTop: "8px" }}>
          Could not copy automatically. Please copy the link manually.
        </div>
      )}
    </div>
  );
};

export default RDSConnectionDetails;
