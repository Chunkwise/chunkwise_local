interface ErrorMessageProps {
  message: string;
  onDismiss?: () => void;
  variant?: "banner" | "inline";
}

const ErrorMessage = ({
  message,
  onDismiss,
  variant = "inline",
}: ErrorMessageProps) => {
  if (variant === "banner") {
    return (
      <div className="error-banner">
        <div className="error-content">
          <span className="icon">error</span>
          <span>{message}</span>
        </div>
        {onDismiss && (
          <button
            className="btn btn-icon btn-sm"
            onClick={onDismiss}
            aria-label="Dismiss error"
          >
            <span className="icon">close</span>
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="error-text">
      <span className="icon icon-sm">error</span>
      <span>{message}</span>
    </div>
  );
};

export default ErrorMessage;
