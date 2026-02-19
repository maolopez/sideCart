variable "db_name" {
  description = "Database name"
  type        = string
}

variable "db_username" {
  description = "Database username"
  type        = string
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

variable "vpc_security_group_ids" {
  description = "List of VPC security group IDs"
  type        = list(string)
}

variable "subnet_ids" {
  description = "List of subnet IDs for DB subnet group"
  type        = list(string)
}

variable "allocated_storage" {
  description = "The allocated storage in gibibytes"
  type        = number
  default     = 20
}

variable "publicly_accessible" {
  description = "Bool to control if instance is publicly accessible"
  type        = bool
  default     = false
}

variable "deletion_protection" {
  description = "Enable deletion protection"
  type        = bool
  default     = true
}

variable "backup_retention_period" {
  description = "The backup retention period"
  type        = number
  default     = 7
}

variable "readonly_username" {
  description = "Read-only database username for application access"
  type        = string
  default     = "readonly_user"
}

variable "readonly_password" {
  description = "Read-only database password"
  type        = string
  sensitive   = true
}