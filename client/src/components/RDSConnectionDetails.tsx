import { useState } from "react";
import type { RDSReadyPayload } from "../types";

interface RDSConnectionDetailsProps {
  details: RDSReadyPayload;
}

const RDSConnectionDetails = ({ details }: RDSConnectionDetailsProps) => {
  const [copied, setCopied] = useState<string | null>(null);
  const connectionString = `postgres://${details.endpoint}:${details.port}/${details.database}`;

  const copyToClipboard = async (text: string, label: string) => {
    await navigator.clipboard.writeText(text);
    setCopied(label);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="deploy-details-card mt-4">
      <h3 className="deploy-details-title">
        <span className="icon icon-sm">database</span>
        Connection Details
      </h3>

      <div className="deploy-connection">
        <code className="deploy-connection-string">{connectionString}</code>
        <button
          className="btn btn-sm"
          type="button"
          onClick={() => copyToClipboard(connectionString, "connection")}
          title="Copy connection string"
        >
          <span className="icon icon-sm">
            {copied === "connection" ? "check" : "content_copy"}
          </span>
        </button>
      </div>

      <dl className="deploy-details">
        <div className="deploy-detail-row">
          <dt>Endpoint</dt>
          <dd>{details.endpoint}</dd>
        </div>
        <div className="deploy-detail-row">
          <dt>Port</dt>
          <dd>{details.port}</dd>
        </div>
        <div className="deploy-detail-row">
          <dt>Database</dt>
          <dd>{details.database}</dd>
        </div>
        <div className="deploy-detail-row">
          <dt>Table</dt>
          <dd>{details.table_name}</dd>
        </div>
        <div className="deploy-detail-row">
          <dt>Secret ARN</dt>
          <dd className="deploy-detail-arn">
            <span>{details.secret_arn}</span>
            <button
              className="btn btn-sm btn-icon"
              type="button"
              onClick={() => copyToClipboard(details.secret_arn, "secret")}
              title="Copy secret ARN"
            >
              <span className="icon icon-sm">
                {copied === "secret" ? "check" : "content_copy"}
              </span>
            </button>
          </dd>
        </div>
      </dl>
    </div>
  );
};

export default RDSConnectionDetails;
