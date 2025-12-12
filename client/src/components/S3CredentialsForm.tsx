import { useState, type FormEvent, type ChangeEvent } from "react";
import type { S3Credentials } from "../types";

interface S3CredentialsFormProps {
  onSubmit: (credentials: S3Credentials) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

const initialCredentials: S3Credentials = {
  access_key: "",
  secret_key: "",
  bucket_name: "",
};

const S3CredentialsForm = ({
  onSubmit,
  onCancel,
  isSubmitting,
}: S3CredentialsFormProps) => {
  const [formState, setFormState] = useState<S3Credentials>(initialCredentials);

  const handleChange = (key: keyof S3Credentials) => (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    setFormState((prev) => ({ ...prev, [key]: event.target.value }));
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit(formState);
  };

  const handleCancel = () => {
    setFormState(initialCredentials);
    onCancel();
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
          autoComplete="new-password"
          value={formState.access_key}
          onChange={handleChange("access_key")}
          disabled={isSubmitting}
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
          autoComplete="new-password"
          value={formState.secret_key}
          onChange={handleChange("secret_key")}
          disabled={isSubmitting}
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
          autoComplete="off"
          value={formState.bucket_name}
          onChange={handleChange("bucket_name")}
          disabled={isSubmitting}
        />
      </div>

      <div className="section-footer">
        <button
          className="btn"
          type="button"
          onClick={handleCancel}
          disabled={isSubmitting}
        >
          Cancel
        </button>
        <button
          className="btn btn-primary"
          type="submit"
          disabled={isSubmitting}
        >
          <span className={`icon icon-sm ${isSubmitting ? "spinner" : ""}`}>
            {isSubmitting ? "sync" : "link"}
          </span>
          {isSubmitting ? "Connecting..." : "Connect"}
        </button>
      </div>
    </form>
  );
};

export default S3CredentialsForm;
