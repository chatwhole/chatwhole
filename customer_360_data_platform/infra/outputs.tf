output "s3_bucket_name" {
  description = "The name of the S3 bucket"
  value       = aws_s3_bucket.customer_360_raw.bucket
}

output "lambda_function_name" {
  description = "The name of the Lambda function"
  value       = aws_lambda_function.data_ingestion.function_name
}
