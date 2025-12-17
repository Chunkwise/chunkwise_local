const RDS_SECRET_ARN_KEY = "chunkwise_rds_secret_arn";

export const setRdsSecretArn = (arn: string): void => {
  localStorage.setItem(RDS_SECRET_ARN_KEY, arn);
};

export const getRdsSecretArn = (): string | null => {
  return localStorage.getItem(RDS_SECRET_ARN_KEY);
};
