# PostgreSQL Read-Only Role Configuration

# Create a read-only user for application access
resource "postgresql_role" "readonly_user" {
  name     = var.readonly_username
  login    = true
  password = var.readonly_password

  depends_on = [aws_db_instance.this]
}

# Grant connect privilege to the database
resource "postgresql_grant" "readonly_connect" {
  database    = var.db_name
  role        = postgresql_role.readonly_user.name
  object_type = "database"
  privileges  = ["CONNECT"]

  depends_on = [postgresql_role.readonly_user]
}

# Grant usage on public schema
resource "postgresql_grant" "readonly_schema_usage" {
  database    = var.db_name
  role        = postgresql_role.readonly_user.name
  schema      = "public"
  object_type = "schema"
  privileges  = ["USAGE"]

  depends_on = [postgresql_role.readonly_user]
}

# Grant select on all existing tables in public schema
resource "postgresql_grant" "readonly_tables" {
  database    = var.db_name
  role        = postgresql_role.readonly_user.name
  schema      = "public"
  object_type = "table"
  privileges  = ["SELECT"]

  depends_on = [postgresql_role.readonly_user]
}

# Grant select on all future tables in public schema
resource "postgresql_default_privileges" "readonly_default_tables" {
  role        = postgresql_role.readonly_user.name
  database    = var.db_name
  schema      = "public"
  owner       = var.db_username
  object_type = "table"
  privileges  = ["SELECT"]

  depends_on = [postgresql_role.readonly_user]
}

# Grant usage on all existing sequences (for serial columns)
resource "postgresql_grant" "readonly_sequences" {
  database    = var.db_name
  role        = postgresql_role.readonly_user.name
  schema      = "public"
  object_type = "sequence"
  privileges  = ["SELECT"]

  depends_on = [postgresql_role.readonly_user]
}

# Grant usage on all future sequences
resource "postgresql_default_privileges" "readonly_default_sequences" {
  role        = postgresql_role.readonly_user.name
  database    = var.db_name
  schema      = "public"
  owner       = var.db_username
  object_type = "sequence"
  privileges  = ["SELECT"]

  depends_on = [postgresql_role.readonly_user]
}