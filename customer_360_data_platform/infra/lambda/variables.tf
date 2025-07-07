variable "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "lambda_zip_path" {
  description = "Path to the zipped Lambda function code"
  type        = string
}
