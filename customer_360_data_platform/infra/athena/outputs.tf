output "athena_workgroup_name" {
  description = "The name of the Athena workgroup"
  value       = aws_athena_workgroup.customer_360_workgroup.name
}
