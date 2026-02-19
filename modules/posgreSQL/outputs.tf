output "endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.this.endpoint
}

output "port" {
  description = "RDS instance port"
  value       = aws_db_instance.this.port
}

output "db_name" {
  description = "Database name"
  value       = aws_db_instance.this.db_name
}

output "db_username" {
  description = "Database username"
  value       = aws_db_instance.this.username
  sensitive   = true
}

output "db_password" {
  description = "Database password"
  value       = aws_db_instance.this.password
  sensitive   = true
}

output "readonly_username" {
  description = "Read-only database username"
  value       = postgresql_role.readonly_user.name
  sensitive   = true
}

output "readonly_password" {
  description = "Read-only database password"
  value       = var.readonly_password
  sensitive   = true
}