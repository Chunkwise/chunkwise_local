import { useState, type FormEvent, type ChangeEvent } from "react";
import { type S3Credentials } from "../services/deploy";

interface S3CredentialsFormProps {
  onSubmit: (credentials: S3Credentials) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

const initialCredentials: S3Credentials = {
  access_key: "",
  secret_key: "",
  bucket_name: "",
  region: "",
};

const S3CredentialsForm = ({
  onSubmit,
  onCancel,
  isSubmitting,
}: S3CredentialsFormProps) => {
  const [formState, setFormState] = useState<S3Credentials>(initialCredentials);

  const handleChange = (
    key: keyof S3Credentials,
    event: ChangeEvent<HTMLInputElement>
  ) => {
    const { value } = event.target;
    setFormState((previous) => ({
      ...previous,
      [key]: value,
    }));
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit(formState);
    setFormState(initialCredentials);
  };

  const handleCancel = () => {
    setFormState(initialCredentials);
    onCancel();
  };

  return (
    <form className="deploy-form" onSubmit={handleSubmit}>
      <div className="field">
        <label className="label" htmlFor="access-key">
          Access Key
        </label>
        <input
          className="input"
          id="access-key"
          type="password"
          required
          autoComplete="new-password"
          value={formState.access_key}
          onChange={(event) => handleChange("access_key", event)}
          disabled={isSubmitting}
        />
      </div>

      <div className="field">
        <label className="label" htmlFor="secret-key">
          Secret Key
        </label>
        <input
          className="input"
          id="secret-key"
          type="password"
          required
          autoComplete="new-password"
          value={formState.secret_key}
          onChange={(event) => handleChange("secret_key", event)}
          disabled={isSubmitting}
        />
      </div>

      <div className="field">
        <label className="label" htmlFor="bucket-name">
          Bucket Name
        </label>
        <input
          className="input"
          id="bucket-name"
          type="text"
          required
          autoComplete="off"
          value={formState.bucket_name}
          onChange={(event) => handleChange("bucket_name", event)}
          disabled={isSubmitting}
        />
      </div>

      <div className="field">
        <label className="label" htmlFor="region">
          Region (optional)
        </label>
        <input
          className="input"
          id="region"
          type="text"
          autoComplete="off"
          placeholder="us-east-1"
          value={formState.region}
          onChange={(event) => handleChange("region", event)}
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
          {isSubmitting ? "Connecting..." : "Connect"}
        </button>
      </div>
    </form>
  );
};

export default S3CredentialsForm;
