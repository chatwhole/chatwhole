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

# S3 bucket for regulatory data lake with folders for raw, processed, curated, reports
resource "aws_s3_bucket" "regulatory_data_lake" {
  bucket = var.s3_bucket_name
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "aws:kms"
      }
    }
  }
}

# Kinesis Data Stream for real-time ingestion
resource "aws_kinesis_stream" "regulatory_stream" {
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
    bucket_arn         = aws_s3_bucket.regulatory_data_lake.arn
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

# Glue Catalog Database
resource "aws_glue_catalog_database" "regulatory_db" {
  name = var.glue_database_name
}

# Glue Crawler
resource "aws_glue_crawler" "regulatory_crawler" {
  name          = "regulatory-data-crawler"
  database_name = aws_glue_catalog_database.regulatory_db.name
  role          = aws_iam_role.glue_role.arn

  s3_target {
    path = "s3://${aws_s3_bucket.regulatory_data_lake.bucket}/raw/"
  }

  schedule = "cron(0 12 * * ? *)"
}

# Glue Job
resource "aws_glue_job" "regulatory_etl_job" {
  name     = "regulatory-etl-job"
  role_arn = aws_iam_role.glue_role.arn

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.regulatory_data_lake.bucket}/scripts/regulatory_etl.py"
    python_version  = "3"
  }

  max_capacity = 2
  glue_version = "2.0"
}

# IAM Role for Glue
resource "aws_iam_role" "glue_role" {
  name = "glue_service_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "glue.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "glue_policy_attach" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Redshift Cluster
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

# SNS Topic for notifications
resource "aws_sns_topic" "regulatory_alerts" {
  name = var.sns_topic_name
}

# Lambda Role
resource "aws_iam_role" "lambda_role" {
  name = "regulatory_lambda_role"

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
          aws_s3_bucket.regulatory_data_lake.arn,
          "${aws_s3_bucket.regulatory_data_lake.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "glue:*",
          "redshift-data:*",
          "sns:Publish"
        ]
        Resource = "*"
      }
    ]
  })
}

# Lambda Function for Preprocessing
resource "aws_lambda_function" "preprocess_lambda" {
  filename         = "${path.module}/lambda/preprocess_lambda.zip"
  function_name    = "regulatory_preprocess_lambda"
  role             = aws_iam_role.lambda_role.arn
  handler          = "preprocess_lambda.handler"
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("${path.module}/lambda/preprocess_lambda.zip")
  timeout          = 30
  memory_size      = 256
}

# Lambda Function for Report Generation
resource "aws_lambda_function" "report_generation_lambda" {
  filename         = "${path.module}/lambda/report_generation_lambda.zip"
  function_name    = "regulatory_report_generation_lambda"
  role             = aws_iam_role.lambda_role.arn
  handler          = "report_generation_lambda.handler"
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("${path.module}/lambda/report_generation_lambda.zip")
  timeout          = 60
  memory_size      = 512
}

# Step Functions Role
resource "aws_iam_role" "step_functions_role" {
  name = "regulatory_step_functions_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "states.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "step_functions_policy_attach" {
  role       = aws_iam_role.step_functions_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSStepFunctionsFullAccess"
}

# Step Functions State Machine
resource "aws_sfn_state_machine" "regulatory_workflow" {
  name     = "regulatory-reporting-workflow"
  role_arn = aws_iam_role.step_functions_role.arn

  definition = <<EOF
{
  "Comment": "Orchestration for regulatory reporting pipeline",
  "StartAt": "RunGlueETL",
  "States": {
    "RunGlueETL": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "${aws_glue_job.regulatory_etl_job.name}"
      },
      "Next": "GenerateReport"
    },
    "GenerateReport": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${aws_lambda_function.report_generation_lambda.arn}",
        "Payload": {}
      },
      "End": true
    }
  }
}
EOF
}

# Outputs
output "s3_bucket" {
  value = aws_s3_bucket.regulatory_data_lake.bucket
}

output "kinesis_stream_name" {
  value = aws_kinesis_stream.regulatory_stream.name
}

output "glue_database_name" {
  value = aws_glue_catalog_database.regulatory_db.name
}

output "redshift_endpoint" {
  value = aws_redshift_cluster.redshift.endpoint
}

output "sns_topic_arn" {
  value = aws_sns_topic.regulatory_alerts.arn
}

output "lambda_preprocess_arn" {
  value = aws_lambda_function.preprocess_lambda.arn
}

output "lambda_report_generation_arn" {
  value = aws_lambda_function.report_generation_lambda.arn
}

output "step_functions_arn" {
  value = aws_sfn_state_machine.regulatory_workflow.arn
}
