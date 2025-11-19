import { useState } from "react";
import type { RDSReadyPayload } from "../services/deploy";

interface RDSConnectionDetailsProps {
  details: RDSReadyPayload;
}

type CopyTarget = "connection" | "secret";

const RDSConnectionDetails = ({ details }: RDSConnectionDetailsProps) => {
  const [copyState, setCopyState] = useState<CopyTarget | "error" | null>(null);
  const connectionString = `postgres://${details.endpoint}:${details.port}/${details.database}`;

  const copyValue = async (value: string, target: CopyTarget) => {
    try {
      await navigator.clipboard.writeText(value);
      setCopyState(target);
      setTimeout(() => setCopyState(null), 2000);
    } catch (error) {
      console.error("Failed to copy deployment detail", error);
      setCopyState("error");
      setTimeout(() => setCopyState(null), 2000);
    }
  };

  return (
    <div className="deployment-summary" aria-live="polite">
      <div className="muted">
        RDS instance <strong>{details.db_instance_identifier}</strong> is
        online.
      </div>
      <div className="muted" style={{ marginTop: "8px" }}>
        Use the connection string below for psql-compatible clients:
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
          {connectionString}
        </div>
        <button
          className="btn btn-sm"
          type="button"
          onClick={() => copyValue(connectionString, "connection")}
        >
          Copy connection
        </button>
      </div>

      <dl
        style={{
          display: "grid",
          gridTemplateColumns: "150px 1fr",
          gap: "8px 12px",
          marginTop: "16px",
        }}
      >
        <dt className="muted">Endpoint</dt>
        <dd style={{ margin: 0 }}>{details.endpoint}</dd>

        <dt className="muted">Port</dt>
        <dd style={{ margin: 0 }}>{details.port}</dd>

        <dt className="muted">Database</dt>
        <dd style={{ margin: 0 }}>{details.database}</dd>

        <dt className="muted">Table</dt>
        <dd style={{ margin: 0 }}>{details.table_name}</dd>

        <dt className="muted">Secret ARN</dt>
        <dd style={{ margin: 0 }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              flexWrap: "wrap",
            }}
          >
            <span style={{ wordBreak: "break-all" }}>
              {details.username_secret_arn}
            </span>
            <button
              className="btn btn-xs"
              type="button"
              onClick={() => copyValue(details.username_secret_arn, "secret")}
            >
              Copy
            </button>
          </div>
        </dd>
      </dl>

      {details.notes && (
        <div className="muted" style={{ marginTop: "12px" }}>
          {details.notes}
        </div>
      )}

      {copyState === "error" && (
        <div className="error" style={{ marginTop: "12px" }}>
          Could not copy automatically. Please copy the value manually.
        </div>
      )}
      {copyState && copyState !== "error" && (
        <div className="muted" style={{ color: "#2b6cb0", marginTop: "8px" }}>
          Copied{" "}
          {copyState === "connection" ? "connection string" : "secret ARN"}
        </div>
      )}
    </div>
  );
};

export default RDSConnectionDetails;
