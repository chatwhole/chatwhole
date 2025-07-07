resource "aws_athena_workgroup" "customer_360_workgroup" {
  name = "customer_360_workgroup"

  configuration {
    enforce_workgroup_configuration = true

    result_configuration {
      output_location = "s3://${var.s3_bucket_name}/athena-results/"
    }
  }

  tags = {
    Environment = var.environment
  }
}
