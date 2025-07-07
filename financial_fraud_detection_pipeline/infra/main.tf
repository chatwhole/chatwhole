terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 Buckets
resource "aws_s3_bucket" "raw_data" {
  bucket = var.s3_bucket_raw
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "aws:kms"
      }
    }
  }
}

resource "aws_s3_bucket" "processed_data" {
  bucket = var.s3_bucket_processed
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "aws:kms"
      }
    }
  }
}

resource "aws_s3_bucket" "model_artifacts" {
  bucket = var.s3_bucket_models
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "aws:kms"
      }
    }
  }
}

# Kinesis Data Stream
resource "aws_kinesis_stream" "transaction_stream" {
  name             = var.kinesis_stream_name
  shard_count      = 1
  retention_period = 24
}

# Kinesis Firehose Delivery Stream to S3
resource "aws_kinesis_firehose_delivery_stream" "firehose_to_s3" {
  name        = var.kinesis_firehose_name
  destination = "s3"

  extended_s3_configuration {
    role_arn           = aws_iam_role.firehose_role.arn
    bucket_arn         = aws_s3_bucket.raw_data.arn
    buffering_interval = 300
    compression_format = "GZIP"
  }
}

# IAM Role for Firehose
resource "aws_iam_role" "firehose_role" {
  name = "firehose_delivery_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {
        Service = "firehose.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "firehose_policy_attach" {
  role       = aws_iam_role.firehose_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

# Lambda Role
resource "aws_iam_role" "lambda_role" {
  name = "fraud_detection_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_custom_policy" {
  name = "lambda_custom_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kinesis:GetRecords",
          "kinesis:GetShardIterator",
          "kinesis:DescribeStream",
          "kinesis:ListStreams"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = [
          aws_s3_bucket.raw_data.arn,
          "${aws_s3_bucket.raw_data.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sagemaker:InvokeEndpoint"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "redshift-data:ExecuteStatement",
          "redshift-data:GetStatementResult"
        ]
        Resource = "*"
      }
    ]
  })
}

# Lambda Function for Preprocessing
resource "aws_lambda_function" "preprocess_lambda" {
  filename         = "${path.module}/lambda/preprocess_lambda.zip"
  function_name    = "fraud_preprocess_lambda"
  role             = aws_iam_role.lambda_role.arn
  handler          = "preprocess_lambda.handler"
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("${path.module}/lambda/preprocess_lambda.zip")
  timeout          = 30
  memory_size      = 256
}

# Lambda Function for Fraud Detection
resource "aws_lambda_function" "fraud_detection_lambda" {
  filename         = "${path.module}/lambda/fraud_detection_lambda.zip"
  function_name    = "fraud_detection_lambda"
  role             = aws_iam_role.lambda_role.arn
  handler          = "fraud_detection_lambda.handler"
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("${path.module}/lambda/fraud_detection_lambda.zip")
  timeout          = 30
  memory_size      = 256
}

# SNS Topic for Fraud Alerts
resource "aws_sns_topic" "fraud_alerts" {
  name = var.sns_topic_name
}

# Redshift Cluster (simplified for demo)
resource "aws_redshift_cluster" "redshift" {
  cluster_identifier = var.redshift_cluster_identifier
  database_name      = var.redshift_database
  master_username    = var.redshift_master_username
  master_password    = var.redshift_master_password
  node_type          = "dc2.large"
  cluster_type       = "single-node"
  publicly_accessible = true
  skip_final_snapshot = true
}

# Outputs
output "s3_raw_bucket" {
  value = aws_s3_bucket.raw_data.bucket
}

output "kinesis_stream_name" {
  value = aws_kinesis_stream.transaction_stream.name
}

output "sns_topic_arn" {
  value = aws_sns_topic.fraud_alerts.arn
}

output "redshift_endpoint" {
  value = aws_redshift_cluster.redshift.endpoint
}
