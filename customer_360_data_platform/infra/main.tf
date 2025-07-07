module "s3" {
  source = "./s3"

  s3_bucket_name = var.s3_bucket_name
  environment    = var.environment
}

module "lambda" {
  source = "./lambda"

  s3_bucket_arn  = module.s3.s3_bucket_arn
  s3_bucket_name = var.s3_bucket_name
  lambda_zip_path = var.lambda_zip_path
}

module "glue" {
  source = "./glue"

  glue_database_name  = var.glue_database_name
  glue_service_role_arn = var.glue_service_role_arn
  s3_bucket_name      = var.s3_bucket_name
  glue_script_s3_path = var.glue_script_s3_path
}

module "athena" {
  source = "./athena"

  s3_bucket_name = var.s3_bucket_name
  environment    = var.environment
}

module "orchestration" {
  source = "./orchestration"

  # No variables needed currently, but can add if required
}
