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

resource "aws_glue_catalog_database" "financial_db" {
  name = var.glue_database_name
}

resource "aws_glue_crawler" "financial_crawler" {
  name          = "financial-data-crawler"
  database_name = aws_glue_catalog_database.financial_db.name
  role          = aws_iam_role.glue_role.arn

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/raw/"
  }

  schedule = "cron(0 12 * * ? *)"
}

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
