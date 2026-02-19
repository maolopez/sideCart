# PostgreSQL provider configuration
terraform {
  required_providers {
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "~> 1.21"
    }
  }
}

provider "postgresql" {
  host     = aws_db_instance.this.endpoint
  port     = aws_db_instance.this.port
  database = aws_db_instance.this.db_name
  username = aws_db_instance.this.username
  password = aws_db_instance.this.password
  sslmode  = "require"
}