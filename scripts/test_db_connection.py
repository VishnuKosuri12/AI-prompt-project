#!/usr/bin/env python3
import os
import sys
import json
import logging
from contextlib import closing

import boto3
import psycopg2
from psycopg2 import sql, OperationalError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_secret(secret_name: str, region: str):
    """Retrieve a secret from AWS Secrets Manager as a dict."""
    session = boto3.session.Session(region_name=region)
    client = session.client(service_name="secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def get_db_connection():
    """Obtain a PostgreSQL connection using credentials from Secrets Manager."""
    try:
        aws_region = os.environ.get("AWS_REGION", "us-east-1")
        # Secret that holds the DB endpoint/URL
        env_secret = get_secret("env-vars", aws_region)
        db_url = env_secret.get("db_url")
        if not db_url:
            raise KeyError("db_url not found in secret 'env-vars'")

        # Secret holding the DB credentials
        cred_secret = get_secret("chemtrack-db-app-user", aws_region)
        username = cred_secret.get("username")
        password = cred_secret.get("password")
        if not username or not password:
            raise KeyError("username or password missing in secret 'chemtrack-db-app-user'")

        # Parse host and optional port (default 5432)
        if ":" in db_url:
            host, port = db_url.split(":", maxsplit=1)
        else:
            host, port = db_url, 5432

        logger.info(f"Connecting to DB host={host}, user={username}")

        conn = psycopg2.connect(
            dbname="chemtrack",
            user=username,
            password=password,
            host=host,
            port=int(port),
        )
        return conn

    except Exception as exc:
        logger.error(f"Failed to get DB connection: {exc}")
        return None


def test_connection():
    """Test if the database connection can be established."""
    conn = get_db_connection()
    if conn:
        logger.info("Database connection successful.")
        conn.close()
        return True
    else:
        logger.error("Database connection failed.")
        return False


def check_users_table():
    """Verify that table `users` exists and has column `pswd_reset`, and sample its data."""
    conn = get_db_connection()
    if conn is None:
        return False

    with closing(conn), conn.cursor() as cursor:
        try:
            # Check existence of table
            cursor.execute(
                """
                SELECT EXISTS (
                  SELECT 1
                  FROM information_schema.tables
                  WHERE table_name = %s
                )
                """,
                ("users",),
            )
            table_exists = cursor.fetchone()[0]
            if not table_exists:
                logger.error("Table `users` does not exist.")
                return False

            # Check presence of pswd_reset column
            cursor.execute(
                """
                SELECT EXISTS (
                  SELECT 1
                  FROM information_schema.columns
                  WHERE table_name = %s AND column_name = %s
                )
                """,
                ("users", "pswd_reset"),
            )
            column_exists = cursor.fetchone()[0]
            if not column_exists:
                logger.error("Column `pswd_reset` not found in table `users`.")
                return False

            logger.info("Table `users` and column `pswd_reset` confirmed.")

            # Fetch sample rows
            cursor.execute("SELECT user_name, pswd_reset FROM users LIMIT 5")
            sample = cursor.fetchall()
            logger.info(f"Sample users: {sample}")

            return True

        except Exception as exc:
            logger.error(f"Error checking users table: {exc}")
            return False


def test_update_pswd_reset(username: str):
    """Test updating the `pswd_reset` flag for a given user."""
    conn = get_db_connection()
    if conn is None:
        return False

    with closing(conn), conn.cursor() as cursor:
        try:
            cursor.execute("SELECT user_name, pswd_reset FROM users WHERE user_name = %s", (username,))
            row = cursor.fetchone()
            if row is None:
                logger.error(f"User '{username}' does not exist.")
                return False

            old_value = row[1]
            logger.info(f"Old pswd_reset for {username}: {old_value}")

            new_value = "Y"
            cursor.execute(
                "UPDATE users SET pswd_reset = %s WHERE user_name = %s",
                (new_value, username),
            )
            conn.commit()

            # Verify the update
            cursor.execute("SELECT pswd_reset FROM users WHERE user_name = %s", (username,))
            updated = cursor.fetchone()[0]
            logger.info(f"Updated pswd_reset for {username}: {updated}")

            return updated == new_value

        except Exception as exc:
            logger.error(f"Error updating pswd_reset for {username}: {exc}")
            return False


def main():
    logger.info("=== Starting diagnostics ===")
    if not test_connection():
        return 1

    logger.info("=== Checking users table ===")
    check_users_table()

    if len(sys.argv) > 1:
        username = sys.argv[1]
        logger.info(f"=== Testing update of pswd_reset for '{username}' ===")
        if test_update_pswd_reset(username):
            logger.info(f"Successfully updated pswd_reset for user '{username}'.")
        else:
            logger.error(f"Failed to update pswd_reset for user '{username}'.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
