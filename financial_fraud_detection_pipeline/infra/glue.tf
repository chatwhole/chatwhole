resource "aws_glue_catalog_database" "fraud_db" {
  name = "fraud_detection_db"
}

resource "aws_glue_crawler" "fraud_crawler" {
  name         = "fraud-detection-crawler"
  database_name = aws_glue_catalog_database.fraud_db.name
  role         = aws_iam_role.glue_role.arn
  s3_target {
    path = "s3://${aws_s3_bucket.processed_data.bucket}/"
  }
  schedule = "cron(0 12 * * ? *)" # daily at noon
}

resource "aws_glue_job" "fraud_etl_job" {
  name     = "fraud-etl-job"
  role_arn = aws_iam_role.glue_role.arn
  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.processed_data.bucket}/scripts/fraud_etl.py"
    python_version  = "3"
  }
  max_capacity = 2
  glue_version = "2.0"
}

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
