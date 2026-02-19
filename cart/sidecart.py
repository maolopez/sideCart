#!/usr/bin/env python3
"""
SideCart - Secure PostgreSQL Database Access Container

This application provides secure, read-only access to a PostgreSQL database
using environment variables for configuration and connection pooling for
optimal performance.
"""

import os
import sys
import logging
import signal
import time
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from dataclasses import dataclass

import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor
import psycopg2.errors


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/sidecart.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration from environment variables."""
    host: str
    port: int
    database: str
    username: str
    password: str
    sslmode: str = 'require'
    connect_timeout: int = 10
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create configuration from environment variables."""
        required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USERNAME', 'DB_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        return cls(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME'),
            username=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            sslmode=os.getenv('DB_SSLMODE', 'require'),
            connect_timeout=int(os.getenv('DB_CONNECT_TIMEOUT', 10))
        )


class DatabaseManager:
    """Manages PostgreSQL database connections with connection pooling."""
    
    def __init__(self, config: DatabaseConfig, min_conn: int = 1, max_conn: int = 5):
        self.config = config
        self.connection_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self.min_conn = min_conn
        self.max_conn = max_conn
        self._shutdown = False
        
    def initialize_pool(self) -> None:
        """Initialize the connection pool."""
        try:
            connection_string = (
                f"host={self.config.host} "
                f"port={self.config.port} "
                f"dbname={self.config.database} "
                f"user={self.config.username} "
                f"password={self.config.password} "
                f"sslmode={self.config.sslmode} "
                f"connect_timeout={self.config.connect_timeout}"
            )
            
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                self.min_conn,
                self.max_conn,
                connection_string
            )
            
            logger.info(f"Database connection pool initialized (min: {self.min_conn}, max: {self.max_conn})")
            
        except psycopg2.Error as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool."""
        if not self.connection_pool:
            raise RuntimeError("Connection pool not initialized")
        
        connection = None
        try:
            connection = self.connection_pool.getconn()
            if connection:
                yield connection
            else:
                raise RuntimeError("Failed to get connection from pool")
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                self.connection_pool.putconn(connection)
    
    def test_connection(self) -> bool:
        """Test database connectivity."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    logger.info("Database connection test successful")
                    return result[0] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a read-only query safely."""
        # Ensure query is read-only (basic check)
        query_upper = query.strip().upper()
        if not query_upper.startswith(('SELECT', 'WITH', 'SHOW', 'EXPLAIN')):
            raise ValueError("Only read-only queries are allowed")
        
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
        except psycopg2.Error as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def get_table_info(self, schema: str = 'public') -> List[Dict[str, Any]]:
        """Get information about tables in the specified schema."""
        query = """
        SELECT 
            table_name,
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_schema = %s
        ORDER BY table_name, ordinal_position
        """
        return self.execute_query(query, (schema,))
    
    def close_pool(self) -> None:
        """Close all connections in the pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Database connection pool closed")


class SideCartApp:
    """Main application class for SideCart."""
    
    def __init__(self):
        self.db_manager: Optional[DatabaseManager] = None
        self._shutdown = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self._shutdown = True
    
    def initialize(self) -> None:
        """Initialize the application."""
        try:
            logger.info("Initializing SideCart application...")
            
            # Load configuration
            config = DatabaseConfig.from_env()
            logger.info(f"Loaded configuration for database: {config.host}:{config.port}/{config.database}")
            
            # Initialize database manager
            self.db_manager = DatabaseManager(config)
            self.db_manager.initialize_pool()
            
            # Test connection
            if not self.db_manager.test_connection():
                raise RuntimeError("Database connection test failed")
            
            logger.info("SideCart application initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            raise
    
    def run_sample_queries(self) -> None:
        """Run some sample queries to demonstrate functionality."""
        if not self.db_manager:
            raise RuntimeError("Database manager not initialized")
        
        try:
            # Get table information
            logger.info("Fetching table information...")
            tables = self.db_manager.get_table_info()
            
            if tables:
                logger.info(f"Found {len(tables)} columns across all tables")
                for table in tables:
                    logger.info(f"Table: {table['table_name']}, Column: {table['column_name']}, Type: {table['data_type']}")
            else:
                logger.info("No tables found in the database")
            
            # Sample query (adjust based on your actual tables)
            logger.info("Attempting to query existing tables...")
            
            # Get list of tables first
            table_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """
            
            table_list = self.db_manager.execute_query(table_query)
            
            if table_list:
                for table_info in table_list:
                    table_name = table_info['table_name']
                    logger.info(f"Querying table: {table_name}")
                    
                    # Count rows in table
                    count_query = f"SELECT COUNT(*) as row_count FROM {table_name}"
                    count_result = self.db_manager.execute_query(count_query)
                    logger.info(f"Table {table_name} has {count_result[0]['row_count']} rows")
            else:
                logger.info("No tables found to query")
            
        except Exception as e:
            logger.error(f"Error running sample queries: {e}")
    
    def run(self) -> None:
        """Main application loop."""
        logger.info("Starting SideCart main loop...")
        
        try:
            # Run sample queries
            self.run_sample_queries()
            
            # Main application loop
            while not self._shutdown:
                # In a real application, this would be where you:
                # - Listen for API requests
                # - Process scheduled tasks
                # - Handle database queries
                
                logger.info("SideCart is running... (Press Ctrl+C to stop)")
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Graceful shutdown of the application."""
        logger.info("Shutting down SideCart application...")
        
        if self.db_manager:
            self.db_manager.close_pool()
        
        logger.info("SideCart application shutdown complete")


def main():
    """Main entry point."""
    try:
        app = SideCartApp()
        app.initialize()
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()