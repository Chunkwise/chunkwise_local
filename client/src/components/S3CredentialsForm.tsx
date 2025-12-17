import { useState, type FormEvent, type ChangeEvent } from "react";
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

  const handleChange = (field: keyof S3Credentials) => (e: ChangeEvent<HTMLInputElement>) => {
    setCredentials((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSubmit(credentials);
  };

  return (
    <form className="deploy-form" onSubmit={handleSubmit}>
      <div className="field">
        <label className="label" htmlFor="access-key">
          <span className="icon icon-sm">key</span>
          Access Key
        </label>
        <input
          className="input"
          id="access-key"
          type="password"
          required
          value={credentials.access_key}
          onChange={handleChange("access_key")}
        />
      </div>

      <div className="field">
        <label className="label" htmlFor="secret-key">
          <span className="icon icon-sm">lock</span>
          Secret Key
        </label>
        <input
          className="input"
          id="secret-key"
          type="password"
          required
          value={credentials.secret_key}
          onChange={handleChange("secret_key")}
        />
      </div>

      <div className="field">
        <label className="label" htmlFor="bucket-name">
          <span className="icon icon-sm">folder</span>
          Bucket Name
        </label>
        <input
          className="input"
          id="bucket-name"
          type="text"
          required
          value={credentials.bucket_name}
          onChange={handleChange("bucket_name")}
        />
      </div>

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
