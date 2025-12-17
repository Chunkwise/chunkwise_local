import { useState, type FormEvent } from "react";
import type { S3Credentials } from "../types";

interface S3CredentialsFormProps {
  onSubmit: (credentials: S3Credentials) => void;
  onCancel: () => void;
}

const S3CredentialsForm = ({ onSubmit, onCancel }: S3CredentialsFormProps) => {
  const [credentials, setCredentials] = useState<S3Credentials>({
    access_key: "",
    secret_key: "",
    bucket_name: "",
  });

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSubmit(credentials);
  };

  const fields = [
    { key: "access_key", label: "Access key", icon: "key", type: "password" },
    { key: "secret_key", label: "Secret key", icon: "lock", type: "password" },
    { key: "bucket_name", label: "Bucket name", icon: "folder", type: "text" },
  ] as const;

  return (
    <form className="deploy-form" onSubmit={handleSubmit}>
      {fields.map(({ key, label, icon, type }) => (
        <div className="field" key={key}>
          <label className="label" htmlFor={key}>
            <span className="icon icon-sm">{icon}</span>
            {label}
          </label>
          <input
            className="input"
            id={key}
            type={type}
            required
            value={credentials[key]}
            onChange={(e) =>
              setCredentials((prev) => ({ ...prev, [key]: e.target.value }))
            }
          />
        </div>
      ))}

      <div className="section-footer">
        <button className="btn" type="button" onClick={onCancel}>
          Cancel
        </button>
        <button className="btn btn-primary" type="submit">
          <span className="icon icon-sm">link</span>
          Connect
        </button>
      </div>
    </form>
  );
};

export default S3CredentialsForm;
