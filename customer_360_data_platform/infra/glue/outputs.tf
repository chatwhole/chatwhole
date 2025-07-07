output "glue_database_name" {
  description = "The name of the Glue database"
  value       = aws_glue_catalog_database.customer_360_db.name
}

output "glue_crawler_name" {
  description = "The name of the Glue crawler"
  value       = aws_glue_crawler.customer_360_crawler.name
}

output "glue_job_name" {
  description = "The name of the Glue ETL job"
  value       = aws_glue_job.customer_360_etl_job.name
}
