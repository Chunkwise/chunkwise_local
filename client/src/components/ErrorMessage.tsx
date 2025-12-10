import { useEffect } from "react";

interface ErrorMessageProps {
  message: string;
  variant?: "banner" | "inline";
  onDismiss: () => void;
}

const AUTO_HIDE_MS = 5000;

const ErrorMessage = ({
  message,
  onDismiss,
  variant = "inline",
}: ErrorMessageProps) => {
  useEffect(() => {
    const timer = setTimeout(onDismiss, AUTO_HIDE_MS);
    return () => clearTimeout(timer);
  }, [onDismiss]);

  if (variant === "banner") {
    return (
      <div className="error-banner">
        <div className="error-content">
          <span className="icon">error</span>
          <span>{message}</span>
        </div>
        <button
          className="btn btn-icon btn-sm"
          onClick={onDismiss}
          aria-label="Dismiss error"
        >
          <span className="icon">close</span>
        </button>
      </div>
    );
  }

  return (
    <div className="error-text">
      <span className="icon icon-sm">error</span>
      <span>{message}</span>
      <button
        className="btn btn-icon btn-sm"
        onClick={onDismiss}
        aria-label="Dismiss error"
      >
        <span className="icon icon-sm">close</span>
      </button>
    </div>
  );
};

export default ErrorMessage;
