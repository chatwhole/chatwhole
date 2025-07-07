variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_raw" {
  description = "S3 bucket name for raw data"
  type        = string
  default     = "fraud-detection-raw-bucket"
}

variable "s3_bucket_processed" {
  description = "S3 bucket name for processed data"
  type        = string
  default     = "fraud-detection-processed-bucket"
}

variable "s3_bucket_models" {
  description = "S3 bucket name for model artifacts"
  type        = string
  default     = "fraud-detection-models-bucket"
}

variable "kinesis_stream_name" {
  description = "Kinesis data stream name"
  type        = string
  default     = "transaction-stream"
}

variable "kinesis_firehose_name" {
  description = "Kinesis Firehose delivery stream name"
  type        = string
  default     = "firehose-to-s3"
}

variable "sns_topic_name" {
  description = "SNS topic name for fraud alerts"
  type        = string
  default     = "fraud-alerts"
}

variable "redshift_cluster_identifier" {
  description = "Redshift cluster identifier"
  type        = string
  default     = "fraud-detection-cluster"
}

variable "redshift_database" {
  description = "Redshift database name"
  type        = string
  default     = "fraud_db"
}

variable "redshift_master_username" {
  description = "Redshift master username"
  type        = string
  default     = "admin"
}

variable "redshift_master_password" {
  description = "Redshift master password"
  type        = string
  sensitive   = true
}
