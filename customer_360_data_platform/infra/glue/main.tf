resource "aws_glue_catalog_database" "customer_360_db" {
  name = var.glue_database_name
}

resource "aws_glue_crawler" "customer_360_crawler" {
  name          = "customer_360_crawler"
  database_name = aws_glue_catalog_database.customer_360_db.name
  role          = var.glue_service_role_arn

  s3_target {
    path = "s3://${var.s3_bucket_name}/"
  }

  schedule = "cron(0 12 * * ? *)" # daily at noon
}

resource "aws_glue_job" "customer_360_etl_job" {
  name     = "customer_360_etl_job"
  role_arn = var.glue_service_role_arn

  command {
    name            = "glueetl"
    script_location = var.glue_script_s3_path
    python_version  = "3"
  }

  max_capacity = 2

  default_arguments = {
    "--job-language" = "python"
  }
}
