# SideCart - PostgreSQL Database Access Tool

SideCart is a secure Python application designed to provide read-only access to PostgreSQL databases. It features connection pooling, comprehensive logging, and can be run either directly as a Python script or within a Docker container.

## Overview

SideCart connects to a PostgreSQL database using environment variables for configuration and provides:
- Secure, read-only database access
- Connection pooling for optimal performance
- Comprehensive logging and error handling
- Graceful shutdown handling
- Sample queries to demonstrate functionality

## Prerequisites

- Python 3.11 or higher (for direct usage)
- Docker (for containerized usage)
- Access to a PostgreSQL database
- Database credentials (preferably read-only user)

## Usage Methods

### Method 1: Direct Python Execution

#### 1. Install Dependencies

```bash
# Install required Python packages
pip install psycopg2-binary python-dotenv
```

#### 2. Configure Environment Variables

Create a `.env` file in the same directory as `sidecart.py`:

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your database credentials
```

Required environment variables:
```env
DB_HOST=your-database-host
DB_PORT=5432
DB_NAME=your-database-name
DB_USERNAME=your-username
DB_PASSWORD=your-password
DB_SSLMODE=require
DB_CONNECT_TIMEOUT=10
```

#### 3. Run the Application

```bash
# Make the script executable (optional)
chmod +x sidecart.py

# Run directly
python sidecart.py

# Or if made executable
./sidecart.py
```

#### 4. Expected Output

The application will:
- Initialize database connection pool
- Test database connectivity
- Display table information
- Run sample queries
- Enter a monitoring loop (press Ctrl+C to stop)

### Method 2: Docker Container Execution

#### 1. Build the Docker Image

```bash
# Build the container image
docker build -t sidecart:latest .

# Verify the image was created
docker images | grep sidecart
```

#### 2. Prepare Environment File

```bash
# Copy and configure environment variables
cp .env.example .env

# Edit .env with your actual database credentials
vim .env  # or use your preferred editor
```

#### 3. Run the Container

**Option A: Using environment file**
```bash
# Run with environment file
docker run --env-file .env sidecart:latest
```

**Option B: Using individual environment variables**
```bash
docker run \
  -e DB_HOST="your-database-host" \
  -e DB_PORT="5432" \
  -e DB_NAME="your-database-name" \
  -e DB_USERNAME="your-username" \
  -e DB_PASSWORD="your-password" \
  -e DB_SSLMODE="require" \
  sidecart:latest
```

**Option C: Interactive mode with volume mounting**
```bash
# Run interactively with log persistence
docker run -it \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  sidecart:latest
```

#### 4. Container Management

```bash
# Run in detached mode
docker run -d --name sidecart-app --env-file .env sidecart:latest

# View logs
docker logs sidecart-app

# Follow logs in real-time
docker logs -f sidecart-app

# Stop the container
docker stop sidecart-app

# Remove the container
docker rm sidecart-app

# Check container health
docker ps
```

## Configuration Options

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | Database hostname or IP | `mydb.amazonaws.com` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `myapp_db` |
| `DB_USERNAME` | Database username | `readonly_user` |
| `DB_PASSWORD` | Database password | `secure_password` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `DB_SSLMODE` | SSL connection mode | `require` |
| `DB_CONNECT_TIMEOUT` | Connection timeout (seconds) | `10` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `APP_ENV` | Application environment | `production` |

## Security Considerations

1. **Read-Only Access**: Use a database user with only SELECT permissions
2. **SSL Connections**: Always use `DB_SSLMODE=require` for production
3. **Environment Variables**: Never commit `.env` files with real credentials
4. **Container Security**: The Docker image runs as a non-root user
5. **Network Security**: Ensure database access is properly firewalled

## Troubleshooting

### Common Issues

**Connection Refused**
```bash
# Check if database is accessible
telnet $DB_HOST $DB_PORT

# Verify credentials
psql -h $DB_HOST -p $DB_PORT -U $DB_USERNAME -d $DB_NAME
```

**Permission Denied**
- Ensure the database user has SELECT permissions
- Check if the user can connect from your IP/container

**SSL Errors**
- Try `DB_SSLMODE=prefer` for testing
- Ensure your database supports SSL connections

### Viewing Logs

**Direct execution:**
```bash
# Logs are output to stdout and to logs/sidecart.log
tail -f logs/sidecart.log
```

**Docker execution:**
```bash
# View container logs
docker logs sidecart-app

# Mount logs directory to host
docker run -v $(pwd)/logs:/app/logs --env-file .env sidecart:latest
```

## Example Usage Scenarios

### Scenario 1: Database Health Check
```bash
# Quick connectivity test
python sidecart.py
# Look for "Database connection test successful" in output
```

### Scenario 2: Scheduled Database Monitoring
```bash
# Run in Docker with restart policy
docker run -d \
  --name sidecart-monitor \
  --restart unless-stopped \
  --env-file .env \
  sidecart:latest
```

### Scenario 3: Development Testing
```bash
# Run with debug logging
LOG_LEVEL=DEBUG python sidecart.py
```

## Integration with Terraform

If you're using the accompanying Terraform configuration:

1. Deploy the PostgreSQL RDS instance using Terraform
2. Use the Terraform outputs for your environment variables:
   - `DB_HOST`: Use the RDS endpoint output
   - `DB_NAME`: Use the database name from Terraform
   - `DB_USERNAME`: Use the read-only user created by Terraform
   - `DB_PASSWORD`: Use the password from Terraform outputs

```bash
# Get Terraform outputs
terraform output -json > outputs.json

# Extract values for .env file
echo "DB_HOST=$(terraform output -raw rds_endpoint)" >> .env
echo "DB_NAME=$(terraform output -raw database_name)" >> .env
```

---

**Note**: This tool is designed for read-only database access. For write operations, use appropriate database administration tools with proper authentication and authorization.