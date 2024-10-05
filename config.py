Hostname = "127.0.0.1"
Port=5432
username="postgres"
password=""
database = "snapshop_db"
DB_URI= f"postgresql://{username}:{password}@{Hostname}:{Port}/{database}"
SQLALCHEMY_DATABASE_URI = DB_URI
