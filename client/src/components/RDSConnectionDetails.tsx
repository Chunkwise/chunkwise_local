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
        RDS instance is online.
      </div>
      <div className="text-muted mt-2">
        Use the connection string below for psql-compatible clients:
      </div>
      <div className="deploy-connection">
        <div className="deploy-connection-string">
          {connectionString}
        </div>
        <button
          className="btn btn-sm"
          type="button"
          onClick={() => copyValue(connectionString, "connection")}
        >
          <span className="icon icon-sm">content_copy</span>
          Copy
        </button>
      </div>

      <dl className="deploy-details">
        <dt className="text-muted">
          <span className="icon icon-sm">language</span> Endpoint
        </dt>
        <dd>{details.endpoint}</dd>

        <dt className="text-muted">
          <span className="icon icon-sm">tag</span> Port
        </dt>
        <dd>{details.port}</dd>

        <dt className="text-muted">
          <span className="icon icon-sm">storage</span> Database
        </dt>
        <dd>{details.database}</dd>

        <dt className="text-muted">
          <span className="icon icon-sm">table_chart</span> Table
        </dt>
        <dd>{details.table_name}</dd>

        <dt className="text-muted">
          <span className="icon icon-sm">vpn_key</span> Secret ARN
        </dt>
        <dd>
          <div className="flex items-center gap-2" style={{ flexWrap: "wrap" }}>
            <span style={{ wordBreak: "break-all" }}>
              {details.secret_arn}
            </span>
            <button
              className="btn btn-sm"
              type="button"
              onClick={() => copyValue(details.secret_arn, "secret")}
            >
              <span className="icon icon-sm">content_copy</span>
              Copy
            </button>
          </div>
        </dd>
      </dl>

      {details.notes && (
        <div className="text-muted mt-3">
          <span className="icon icon-sm">info</span>
          {details.notes}
        </div>
      )}

      {copyState === "error" && (
        <div className="error-text mt-3">
          <span className="icon icon-sm">error</span>
          Could not copy automatically. Please copy the value manually.
        </div>
      )}
      {copyState && copyState !== "error" && (
        <div className="text-muted mt-2" style={{ color: "var(--color-success)" }}>
          <span className="icon icon-sm">check_circle</span>
          Copied {copyState === "connection" ? "connection string" : "secret ARN"}
        </div>
      )}
    </div>
  );
};

export default RDSConnectionDetails;
