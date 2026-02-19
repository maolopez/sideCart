module "postgresql" {
  source                 = "../../modules/posgreSQL"
  db_name                = var.db_name
  db_username            = var.db_username
  db_password            = var.db_password
  db_instance_class      = var.db_instance_class
  vpc_security_group_ids = [aws_security_group.rds.id]
  subnet_ids             = data.aws_subnets.default.ids

  # Configuration from variables
  publicly_accessible     = var.publicly_accessible
  deletion_protection     = var.deletion_protection
  backup_retention_period = var.backup_retention_period
  readonly_password       = var.readonly_password
}

resource "null_resource" "init_db" {
  provisioner "local-exec" {
    command = <<EOT
# Wait for RDS to be ready
sleep 60
# Create table
PGPASSWORD=${module.postgresql.db_password} psql -h ${module.postgresql.endpoint} -U ${module.postgresql.db_username} -d ${module.postgresql.db_name} -p ${module.postgresql.port} -c "CREATE TABLE IF NOT EXISTS demo_table (id SERIAL PRIMARY KEY, name TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"
EOT
    environment = {
      PGPASSWORD = module.postgresql.db_password
    }
  }
  depends_on = [module.postgresql]
}

resource "aws_security_group" "rds" {
  name        = var.security_group_name
  description = "Allow PostgreSQL inbound for PoC"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "PostgreSQL"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # For PoC only; restrict in production!
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = var.security_group_name
    Environment = var.environment
  }
}

# Data sources
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}