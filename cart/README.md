# SideCart - Secure PostgreSQL Database Access Container

SideCart is a secure, containerized Python application designed to provide safe, read-only access to PostgreSQL databases using dedicated read-only credentials.

## Features

- 🔒 **Secure Access**: Uses read-only database credentials with minimal privileges
- 🐳 **Containerized**: Runs in a secure Docker container with non-root user
- 🔄 **Connection Pooling**: Efficient database connection management
- 📊 **Comprehensive Logging**: Structured logging for monitoring and debugging
- 🛡️ **Security Best Practices**: SSL connections, input validation, and secure configuration
- 🏗️ **Infrastructure as Code**: Terraform modules for database and role provisioning

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SideCart      │    │   PostgreSQL    │    │   Terraform     │
│   Container     │───▶│   RDS Instance  │◀───│   Modules       │
│                 │    │                 │    │                 │
│ • Python App    │    │ • Read-only     │    │ • RDS Setup     │
│ • psycopg2      │    │   User          │    │ • Role Creation │
│ • Connection    │    │ • SSL Required  │    │ • Security      │
│   Pooling       │    │                 │    │   Groups        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

- Docker and Docker Compose
- Terraform (for infrastructure provisioning)
- PostgreSQL RDS instance with read-only user configured

## Quick Start

### 1. Infrastructure Setup

First, provision your PostgreSQL RDS instance and read-only user using Terraform:

```bash
cd ../terraform
terraform init
terraform plan
terraform apply
```

### 2. Configuration

Copy the environment variables template and configure your database connection:

```bash
cp .env.example .env
# Edit .env with your actual database credentials
```

### 3. Build and Run

Using Docker Compose:

```bash
# Build and start the container
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f sidecart

# Stop the container
docker-compose down
```

Using Docker directly:

```bash
# Build the image
docker build -t sidecart .

# Run the container
docker run --env-file .env -v $(pwd)/logs:/app/logs sidecart
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|----------|
| `DB_HOST` | PostgreSQL server hostname | Yes | - |
| `DB_PORT` | PostgreSQL server port | No | 5432 |
| `DB_NAME` | Database name | Yes | - |
| `DB_READONLY_USERNAME` | Read-only user username | Yes | - |
| `DB_READONLY_PASSWORD` | Read-only user password | Yes | - |
| `DB_SSLMODE` | SSL connection mode | No | require |
| `DB_CONNECT_TIMEOUT` | Connection timeout in seconds | No | 10 |

## Terraform Integration

The SideCart container is designed to work with the PostgreSQL Terraform module located in `../modules/posgreSQL/`. This module creates:

- PostgreSQL RDS instance
- Read-only database user with minimal privileges
- Security groups and networking configuration
- Outputs for connection details

### Terraform Outputs

After applying the Terraform configuration, you can get the connection details:

```bash
# Get database endpoint
terraform output endpoint

# Get read-only credentials (sensitive)
terraform output -json | jq '.readonly_username.value'
terraform output -json | jq '.readonly_password.value'
```

## Security Features

### Container Security
- Non-root user execution
- Minimal base image (Python slim)
- No unnecessary packages
- Security options enabled
- Resource limits configured

### Database Security
- Read-only database access
- SSL/TLS encryption required
- Connection timeout limits
- Input validation for queries
- No dynamic SQL execution

### Application Security
- Environment variable configuration (no hardcoded secrets)
- Comprehensive error handling
- Structured logging (no sensitive data in logs)
- Graceful shutdown handling
- Query validation (read-only operations only)

## Monitoring and Logging

### Log Files
- Application logs: `/app/logs/sidecart.log`
- Container logs: `docker-compose logs sidecart`

### Health Checks
The container includes health checks that verify:
- Python application is running
- Database connectivity
- psycopg2 module availability

### Monitoring Commands

```bash
# Check container health
docker-compose ps

# View real-time logs
docker-compose logs -f sidecart

# Check resource usage
docker stats sidecart-app

# Execute commands in running container
docker-compose exec sidecart python -c "print('Container is running')"
```

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
# ... other variables

# Run the application
python sidecart.py
```

### Testing Database Connection

```bash
# Test connection using psql
psql -h $DB_HOST -p $DB_PORT -U $DB_READONLY_USERNAME -d $DB_NAME

# Test connection using Python
python -c "
import os
import psycopg2
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_READONLY_USERNAME'),
    password=os.getenv('DB_READONLY_PASSWORD')
)
print('Connection successful!')
conn.close()
"
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if RDS instance is running
   - Verify security group allows connections
   - Confirm VPC and subnet configuration

2. **Authentication Failed**
   - Verify read-only user credentials
   - Check if user was created successfully
   - Ensure password is correct

3. **SSL Connection Issues**
   - Verify SSL is enabled on RDS
   - Check SSL mode configuration
   - Ensure certificates are valid

4. **Permission Denied**
   - Confirm read-only user has SELECT privileges
   - Check if tables exist in the database
   - Verify schema permissions

### Debug Commands

```bash
# Check container logs
docker-compose logs sidecart

# Access container shell
docker-compose exec sidecart /bin/bash

# Test database connectivity
docker-compose exec sidecart python -c "from sidecart import DatabaseConfig, DatabaseManager; config = DatabaseConfig.from_env(); db = DatabaseManager(config); db.initialize_pool(); print('Success!' if db.test_connection() else 'Failed!')"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review container and application logs
3. Verify Terraform infrastructure is properly deployed
4. Create an issue with detailed error information