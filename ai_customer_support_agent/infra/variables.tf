variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "lambda_image_uri" {
  description = "ECR image URI for the Lambda function"
  type        = string
}
