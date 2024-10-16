# SnapShop Backend Service

This is a backend service for SnapShop, which is based on the Flask framework and PostgreSQL database. The service
provides APIs for SnapShop frontend to interact with the database.

---

## Installation

Use Python 3.8 or later to run the service. Install the required packages by running the following command:

```
pip install -r requirements.txt
```

## Configuration

The service requires a PostgreSQL database to run. You can configure the database connection by setting the following
environment variables in the `app/config.py` file:

- `DB_HOST`: The hostname of the database server.
- `DB_PORT`: The port of the database server.
- `DB_USER`: The password of the database user.
- `DB_PASSWORD`: The password of the database user.

## Running the Service

To run the service, execute the following command:

```
python3 app.py
```

The service will start running on `http://localhost:5000`.

## Migration

To create the database schema, run the following command:

```
python3 migrate.py
```

This will create the necessary tables in the database.

## Cloud Deployment

We have deployed the service on Alibaba Cloud. You can access the service at the following URL:

```
http://47.98.118.134/api
```