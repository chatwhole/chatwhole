resource "aws_s3_bucket" "customer_360_raw" {
  bucket = var.s3_bucket_name

  versioning {
    enabled = true
  }

  lifecycle_rule {
    id      = "ExpireOldObjects"
    enabled = true

    expiration {
      days = 90
    }
  }

  tags = {
    Name        = "Customer 360 Raw Data Bucket"
    Environment = var.environment
  }
}
