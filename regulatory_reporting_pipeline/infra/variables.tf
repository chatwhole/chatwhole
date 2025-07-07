variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "S3 bucket name for regulatory data lake"
  type        = string
  default     = "regulatory-data-lake-bucket"
}

variable "kinesis_stream_name" {
  description = "Kinesis data stream name"
  type        = string
  default     = "regulatory-stream"
}

variable "kinesis_firehose_name" {
  description = "Kinesis Firehose delivery stream name"
  type        = string
  default     = "firehose-to-s3"
}

variable "glue_database_name" {
  description = "Glue catalog database name"
  type        = string
  default     = "regulatory_db"
}

variable "redshift_cluster_identifier" {
  description = "Redshift cluster identifier"
  type        = string
  default     = "regulatory-cluster"
}

variable "redshift_database" {
  description = "Redshift database name"
  type        = string
  default     = "regulatory_db"
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

variable "sns_topic_name" {
  description = "SNS topic name for regulatory alerts"
  type        = string
  default     = "regulatory-alerts"
}
