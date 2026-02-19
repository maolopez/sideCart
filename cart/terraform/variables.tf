variable "db_name" {
  description = "Database name"
  type        = string
  default     = "pocdb"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "pocuser"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "security_group_name" {
  description = "Name for the RDS security group"
  type        = string
  default     = "rds-poc-sg"
}

variable "publicly_accessible" {
  description = "Whether the RDS instance should be publicly accessible"
  type        = bool
  default     = true
}

variable "deletion_protection" {
  description = "Enable deletion protection for RDS instance"
  type        = bool
  default     = false
}

variable "backup_retention_period" {
  description = "Number of days to retain backups"
  type        = number
  default     = 0
}

variable "environment" {
  description = "Environment tag"
  type        = string
  default     = "poc"
}

variable "readonly_password" {
  description = "Read-only database password"
  type        = string
  sensitive   = true
}