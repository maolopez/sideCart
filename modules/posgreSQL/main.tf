resource "aws_db_subnet_group" "this" {
  name       = "${var.db_name}-subnet-group"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "${var.db_name}-subnet-group"
  }
}

resource "aws_db_instance" "this" {
  identifier              = var.db_name
  engine                  = "postgres"
  engine_version          = "15.4"
  instance_class          = var.db_instance_class
  allocated_storage       = var.allocated_storage
  storage_type            = "gp2"
  storage_encrypted       = true

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = var.vpc_security_group_ids

  skip_final_snapshot     = true
  publicly_accessible     = var.publicly_accessible
  deletion_protection     = var.deletion_protection
  backup_retention_period = var.backup_retention_period
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  performance_insights_enabled = false
  monitoring_interval         = 0

  tags = {
    Name        = var.db_name
    Environment = "poc"
  }
}