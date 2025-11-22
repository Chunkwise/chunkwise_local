"""
This modules provides the server the functions that it needs to interact with the database.
"""

import json
from typing import Dict, Any
from contextlib import contextmanager
import psycopg2
from psycopg2 import OperationalError, sql
from server_types import ChunkerConfig
from pydantic import TypeAdapter
import boto3

COLUMN_NAMES: tuple[str, ...] = (
    "id",
    "title",
    "created_at",
    "document_title",
    "chunking_strategy",
    "chunks_stats",
    "visualization_html",
    "evaluation_metrics",
)

# Cache for database credentials (avoid repeated Secrets Manager calls)
_db_credentials_cache = {}


def get_db_credentials(secret_name: str) -> dict:
    """
    Get database credentials from AWS Secrets Manager.
    Results are cached to avoid repeated API calls.

    Returns dict with keys: username, password, host, port, dbname, engine
    """
    if secret_name in _db_credentials_cache:
        return _db_credentials_cache[secret_name]

    try:
        secretsmanager = boto3.client("secretsmanager")
        secret_response = secretsmanager.get_secret_value(SecretId=secret_name)
        secret = json.loads(secret_response["SecretString"])

        # Cache the credentials
        _db_credentials_cache[secret_name] = secret
        return secret
    except Exception as e:
        print(f"Error getting secret {secret_name}: {e}")
        raise


@contextmanager
def get_db_connection(
    host: str,
    port: str,
    database: str,
    user: str,
    password: str,
):
    """
    Context manager for database connections.
    Automatically closes connection when done.
    """
    connection = None
    try:
        db_connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
        )
        db_connection.autocommit = True
        print("Successfully connected to database at %s", host)
        yield db_connection

    except OperationalError as e:
        print(("Error connecting to the databaseat %s: %s", host, e))
        raise e
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")


def get_evaluation_db_connection():
    """
    Creates and returns a connection object for the evaluation database.
    Reads credentials from Secrets Manager.
    """

    # Get credentials from Secrets Manager
    db_creds = get_db_credentials("chunkwise/database-credentials")

    # Also try environment variables as fallback
    host = db_creds.get("host", os.getenv("DB_HOST"))
    port = int(db_creds.get("port", os.getenv("DB_PORT", "5432")))
    database = db_creds.get("dbname", os.getenv("DB_NAME"))
    user = db_creds.get("username")
    password = db_creds.get("password")

    return get_db_connection(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
    )


def setup_schema():
    """
    Creates a row in the workflow table and returns the id of the
    created workflow.
    """
    connection = None
    try:
        with get_evaluation_db_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'workflow'
                """
            )
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    """
                        CREATE TABLE workflow (
                        id SERIAL PRIMARY KEY,
                        title varchar(50) NOT NULL,
                        created_at timestamptz NOT NULL DEFAULT NOW(),
                        document_title TEXT,
                        chunking_strategy TEXT,
                        chunks_stats TEXT,
                        visualization_html TEXT,
                        evaluation_metrics TEXT
                        );
                    """
                )
                print("Created workflow table")
            else:
                print("Workflow table already exists")
    except Exception as e:
        print(("Error setting up database.", e))
        raise e


def format_workflow(workflow: tuple) -> Dict[str, Any]:
    """
    Takes a complete list of column values and put them with their corresponding property
    name. Also converts JSON strings into objects.
    """
    formatted_result = zip(COLUMN_NAMES, workflow)
    formatted_result_dict = dict(formatted_result)

    if isinstance(formatted_result_dict.get("chunking_strategy"), str):
        formatted_result_dict["chunking_strategy"] = json.loads(
            formatted_result_dict["chunking_strategy"]
        )

    if isinstance(formatted_result_dict.get("chunks_stats"), str):
        formatted_result_dict["chunks_stats"] = json.loads(
            formatted_result_dict["chunks_stats"]
        )

    if isinstance(formatted_result_dict.get("evaluation_metrics"), str):
        formatted_result_dict["evaluation_metrics"] = json.loads(
            formatted_result_dict["evaluation_metrics"]
        )

    return formatted_result_dict


def create_workflow(workflow_title: str) -> Dict[str, Any]:
    """
    Creates a row in the workflow table and returns the id of the
    created workflow.
    """
    connection = None
    try:
        with get_evaluation_db_connection() as connection:
            cursor = connection.cursor()

            query = "INSERT INTO workflow (title) VALUES (%s) RETURNING id;"
            cursor.execute(query, (workflow_title,))
            print(query)

            created_id = cursor.fetchone()[0]

            query = "SELECT * FROM workflow WHERE id = %s;"
            cursor.execute(query, (created_id,))
            print(query)

            result = cursor.fetchone()
            formatted_result = format_workflow(result)

            return formatted_result
    except Exception as e:
        print(("Error creating workflow.", e))
        raise e


def update_workflow(
    workflow_id: int, updated_columns: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Takes an id and an object with Workflow properties and sets the
    corresponding columns in the database to match.
    """
    connection = None
    try:
        with get_evaluation_db_connection() as connection:
            cursor = connection.cursor()

            for column, value in updated_columns.items():
                if value is None:
                    # Column update not sent
                    continue
                if value == "":
                    value = None
                elif (
                    column
                    in ("chunking_strategy", "chunks_stats", "evaluation_metrics")
                    and value is not None
                ):
                    if not isinstance(value, dict):
                        value = json.dumps(value.__dict__)
                    else:
                        value = json.dumps(value)

                query = sql.SQL(
                    "UPDATE workflow SET {column_name} = %s WHERE id = %s;"
                ).format(column_name=sql.Identifier(column))
                cursor.execute(query, (value, workflow_id))
                print(query)

            cursor.execute("SELECT * FROM workflow WHERE id = %s", (workflow_id,))

            result = cursor.fetchone()
            formatted_result = format_workflow(result)

            return formatted_result
    except Exception as e:
        print(("Error updating workflow.", e))
        raise e


def delete_workflow(workflow_id: int) -> bool:
    """
    Deletes a workflow and returns a boolean representing whether the
    operation was successful.
    """
    connection = None
    try:
        with get_evaluation_db_connection() as connection:
            cursor = connection.cursor()

            query = "DELETE FROM workflow WHERE id = %s"
            cursor.execute(query, (workflow_id,))
            print(query)

            return cursor.rowcount > 0
    except Exception as e:
        print(("Error deleting workflow.", e))
        raise e


def get_all_workflows() -> list[Dict[str, Any]]:
    """
    Returns a list containing all of the workflows stored in the database.
    """
    connection = None
    try:
        with get_evaluation_db_connection() as connection:
            cursor = connection.cursor()

            query = "SELECT * FROM workflow"
            cursor.execute(query)
            print(query)

            result = cursor.fetchall()

            formatted_result = [format_workflow(row) for row in result]

            return formatted_result
    except Exception as e:
        print(("Error retrieving workflows.", e))
        raise e


def get_workflow_info(workflow_id) -> tuple[str, ChunkerConfig]:
    """
    Retrieves both the document_title and chunking_strategy (as a ChunkerConfig)
    for a given workflow_id.
    """
    connection = None
    try:
        with get_evaluation_db_connection() as connection:
            cursor = connection.cursor()

            query = """
                SELECT document_title, chunking_strategy
                FROM workflow
                WHERE id = %s
            """
            cursor.execute(query, (workflow_id,))
            print(query)

            result = cursor.fetchone()
            if not result:
                raise ValueError(f"No workflow found with id {workflow_id}")

            document_title, chunking_strategy_json = result

            adapter = TypeAdapter(ChunkerConfig)
            chunker_config = adapter.validate_json(chunking_strategy_json)

            return document_title, chunker_config
    except Exception as e:
        print("Error retrieving workflow info:", e)
        raise e


def get_chunker_config(workflow_id) -> ChunkerConfig:
    """
    Retrieves both the document_title and chunking_strategy (as a ChunkerConfig)
    for a given workflow_id.
    """
    connection = None
    try:
        with get_evaluation_db_connection() as connection:
            cursor = connection.cursor()

            query = """
                SELECT chunking_strategy
                FROM workflow
                WHERE id = %s
            """
            cursor.execute(query, (workflow_id,))
            print(query)

            result = cursor.fetchone()
            if not result:
                raise ValueError(f"No workflow found with id {workflow_id}")

            chunking_strategy_json = result[0]

            adapter = TypeAdapter(ChunkerConfig)
            chunker_config = adapter.validate_json(chunking_strategy_json)

            return chunker_config
    except Exception as e:
        print("Error retrieving workflow info:", e)
        raise e


def ensure_pgvector_and_table(
    conn, workflow_id: str, table_prefix: str = "workflow_", embedding_dim: int = 1536
) -> str:
    """
    Creates a pgvector table for a workflow in the production database.
    Drops the table if it already exists to ensure a clean slate.
    """
    table_name = f"{table_prefix}{workflow_id}"

    with conn.cursor() as cursor:

        # Install pgvector extension if not exists
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Remove table if it exists
        remove_table_sql = sql.SQL("DROP TABLE IF EXISTS {table};").format(
            table=sql.Identifier(table_name)
        )
        cursor.execute(remove_table_sql)

        # Create table
        create_table_sql = sql.SQL(
            """
            CREATE TABLE {table} (
                id BIGSERIAL PRIMARY KEY,
                document_key TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                chunk_text TEXT,
                embedding vector(%s)
            );
            """
        ).format(table=sql.Identifier(table_name))
        cursor.execute(create_table_sql, (embedding_dim,))

        # Create index on embedding column
        idx_sql = sql.SQL(
            "CREATE INDEX IF NOT EXISTS {idx_name} ON {table} USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);"
        ).format(
            idx_name=sql.Identifier(f"{table_name}_emb_idx"),
            table=sql.Identifier(table_name),
        )
        cursor.execute(idx_sql)
        print(f"Created index on {table_name}")

    return table_name
