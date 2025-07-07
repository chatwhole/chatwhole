variable "glue_database_name" {
  description = "Name of the Glue database"
  type        = string
}

variable "glue_service_role_arn" {
  description = "IAM Role ARN for Glue service"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "glue_script_s3_path" {
  description = "S3 path to the Glue ETL script"
  type        = string
}
