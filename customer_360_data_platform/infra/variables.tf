variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for raw data"
  type        = string
  default     = "customer-360-raw"
}

variable "environment" {
  description = "Deployment environment (e.g., dev, prod)"
  type        = string
  default     = "dev"
}

variable "lambda_zip_path" {
  description = "Path to the zipped Lambda function code"
  type        = string
  default     = "lambda_function.zip"
}

variable "glue_database_name" {
  description = "Name of the Glue database"
  type        = string
  default     = "customer_360_db"
}

variable "glue_service_role_arn" {
  description = "IAM Role ARN for Glue service"
  type        = string
  default     = ""
}

variable "glue_script_s3_path" {
  description = "S3 path to the Glue ETL script"
  type        = string
  default     = ""
}
