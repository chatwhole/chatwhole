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

# S3 bucket for data lake with folders for raw, processed, curated
resource "aws_s3_bucket" "data_lake" {
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
resource "aws_kinesis_stream" "financial_stream" {
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
    bucket_arn         = aws_s3_bucket.data_lake.arn
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
resource "aws_glue_catalog_database" "financial_db" {
  name = var.glue_database_name
}

# Glue Crawler
resource "aws_glue_crawler" "financial_crawler" {
  name          = "financial-data-crawler"
  database_name = aws_glue_catalog_database.financial_db.name
  role          = aws_iam_role.glue_role.arn

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/raw/"
  }

  schedule = "cron(0 12 * * ? *)"
}

# Glue Job
resource "aws_glue_job" "financial_etl_job" {
  name     = "financial-etl-job"
  role_arn = aws_iam_role.glue_role.arn

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.data_lake.bucket}/scripts/financial_etl.py"
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

# API Gateway REST API
resource "aws_api_gateway_rest_api" "financial_api" {
  name        = "financial-data-api"
  description = "API for accessing curated financial data"
}

# Outputs
output "s3_data_lake_bucket" {
  value = aws_s3_bucket.data_lake.bucket
}

output "kinesis_stream_name" {
  value = aws_kinesis_stream.financial_stream.name
}

output "glue_database_name" {
  value = aws_glue_catalog_database.financial_db.name
}

output "redshift_endpoint" {
  value = aws_redshift_cluster.redshift.endpoint
}

output "api_gateway_id" {
  value = aws_api_gateway_rest_api.financial_api.id
}
