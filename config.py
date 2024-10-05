import os

Hostname = os.getenv("DB_HOST", "127.0.0.1")
Port = os.getenv("DB_PORT", 5432)
username = os.getenv("DB_USER", "postgres")
password = os.getenv("DB_PASSWORD", "")
database = os.getenv("DB_NAME", "snapshop_db")

DB_URI = f"postgresql://{username}:{password}@{Hostname}:{Port}/{database}"
SQLALCHEMY_DATABASE_URI = DB_URI
