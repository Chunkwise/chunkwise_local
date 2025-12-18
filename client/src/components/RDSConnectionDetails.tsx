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

  const DetailRow = ({
    label,
    value,
    copyId,
  }: {
    label: string;
    value: string;
    copyId: string;
  }) => (
    <div className="deploy-detail-section">
      <label className="deploy-detail-label">{label}</label>
      <div className="deploy-connection">
        <code
          className={`deploy-connection-string${
            copyId === "aws" ? " deploy-command" : ""
          }`}
        >
          {value}
        </code>
        <button
          className="btn btn-sm"
          type="button"
          onClick={() => copyToClipboard(value, copyId)}
          title={`Copy ${label.toLowerCase()}`}
        >
          <span className="icon icon-sm">
            {copied === copyId ? "check" : "content_copy"}
          </span>
        </button>
      </div>
    </div>
  );

  return (
    <div className="deploy-details-card mt-4">
      <h3 className="section-header">
        <span className="icon">storage</span>
        <span className="title-sm">Database details</span>
      </h3>

      <DetailRow label="Table name" value={details.table_name} copyId="table" />
      <DetailRow label="Secret ARN" value={details.secret_arn} copyId="arn" />
      <DetailRow
        label="Get database credentials"
        value={awsCommand}
        copyId="aws"
      />
    </div>
  );
};

export default RDSConnectionDetails;
