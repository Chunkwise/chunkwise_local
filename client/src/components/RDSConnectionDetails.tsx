import { useState } from "react";
import type { RDSReadyPayload } from "../types";

interface RDSConnectionDetailsProps {
  details: RDSReadyPayload;
}

const RDSConnectionDetails = ({ details }: RDSConnectionDetailsProps) => {
  const [copied, setCopied] = useState<string | null>(null);

  const copyToClipboard = async (text: string, label: string) => {
    await navigator.clipboard.writeText(text);
    setCopied(label);
    setTimeout(() => setCopied(null), 2000);
  };

  const awsCommand = `aws secretsmanager get-secret-value \\
  --secret-id ${details.secret_arn} \\
  --query SecretString \\
  --output text`;

  const psqlCommand = `PGPASSWORD=$(aws secretsmanager get-secret-value \\
  --secret-id ${details.secret_arn} \\
  --query SecretString \\
  --output text | jq -r .password) \\
psql -h ${details.endpoint} \\
  -p ${details.port} \\
  -U $(aws secretsmanager get-secret-value \\
  --secret-id ${details.secret_arn} \\
  --query SecretString \\
  --output text | jq -r .username) \\
  -d ${details.database}`;

  return (
    <div className="deploy-details-card mt-4">
      <h3 className="deploy-details-title">
        <span className="icon icon-sm">database</span>
        Database Connection
      </h3>

      <div className="deploy-detail-section">
        <label className="deploy-detail-label">Table Name</label>
        <div className="deploy-connection">
          <code className="deploy-connection-string">{details.table_name}</code>
          <button
            className="btn btn-sm"
            type="button"
            onClick={() => copyToClipboard(details.table_name, "table")}
            title="Copy table name"
          >
            <span className="icon icon-sm">
              {copied === "table" ? "check" : "content_copy"}
            </span>
          </button>
        </div>
      </div>

      <div className="deploy-detail-section mt-3">
        <label className="deploy-detail-label">Secret ARN</label>
        <div className="deploy-connection">
          <code className="deploy-connection-string">{details.secret_arn}</code>
          <button
            className="btn btn-sm"
            type="button"
            onClick={() => copyToClipboard(details.secret_arn, "arn")}
            title="Copy secret ARN"
          >
            <span className="icon icon-sm">
              {copied === "arn" ? "check" : "content_copy"}
            </span>
          </button>
        </div>
      </div>

      <div className="deploy-detail-section mt-3">
        <label className="deploy-detail-label">Get Database Credentials</label>
        <div className="deploy-connection">
          <code className="deploy-connection-string deploy-command">{awsCommand}</code>
          <button
            className="btn btn-sm"
            type="button"
            onClick={() => copyToClipboard(awsCommand, "aws")}
            title="Copy AWS command"
          >
            <span className="icon icon-sm">
              {copied === "aws" ? "check" : "content_copy"}
            </span>
          </button>
        </div>
      </div>

      <div className="deploy-detail-section mt-3">
        <label className="deploy-detail-label">Connect with psql</label>
        <div className="deploy-connection">
          <code className="deploy-connection-string deploy-command">{psqlCommand}</code>
          <button
            className="btn btn-sm"
            type="button"
            onClick={() => copyToClipboard(psqlCommand, "psql")}
            title="Copy psql command"
          >
            <span className="icon icon-sm">
              {copied === "psql" ? "check" : "content_copy"}
            </span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default RDSConnectionDetails;
