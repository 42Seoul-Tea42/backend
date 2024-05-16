import psycopg2
import os


class PostgreSQLFactory:
    _conn = None

    @classmethod
    def get_connection(cls):
        if cls._conn is None:
            cls.create_connection()
        return cls._conn

    @classmethod
    def create_connection(cls):
        db_params = {
            "dbname": os.getenv("POSTGRES_DB_NAME"),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "host": os.getenv("POSTGRES_HOST"),
            "port": os.getenv("POSTGRES_PORT"),
        }
        cls._conn = psycopg2.connect(**db_params)

    @classmethod
    def close_connection(cls):
        if cls._conn:
            cls._conn.close()
            cls._conn = None
