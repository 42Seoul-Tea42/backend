import psycopg2
import os

# Database setup logic here...
# Database connection parameters
db_params = {
    'dbname': os.environ.get('POSTGRES_DB'),
    'user': os.environ.get('POSTGRES_USER'),
    'password': os.environ.get('POSTGRES_PASSWORD'),
    'host': os.environ.get('POSTGRES_HOST'),
    'port': os.environ.get('POSTGRES_PORT')
}

# Create a connection to the database
conn = psycopg2.connect(**db_params)

# Export the connection to make it accessible in other modules
__all__ = ['conn']