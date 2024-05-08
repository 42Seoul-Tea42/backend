import psycopg2
import os

# Database setup logic here...
# Database connection parameters
db_params = {
    "dbname": os.getenv("POSTGRES_DB_NAME"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
}

# Create a connection to the database
conn = psycopg2.connect(**db_params)

# Export the connection to make it accessible in other modules
__all__ = ["conn"]
