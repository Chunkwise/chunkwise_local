"""
This modules provides the server the functions that it needs to interact with the database.
"""

import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError, sql
from server_types import ChunkerConfig
from pydantic import TypeAdapter

load_dotenv()

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
DBNAME = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
ENDPOINT = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
REGION = "us-east-1"


def setup_schema():
    """
    Creates a row in the workflow table and returns the id of the
    created workflow.
    """
    connection = None
    try:
        connection = get_db_connection()
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
    except Exception as e:
        print(("Error setting up database.", e))
        raise e
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")


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


def get_db_connection():
    """
    Creates and returns a connection object for the database.
    """
    try:
        db_connection = psycopg2.connect(
            host=ENDPOINT,
            port=PORT,
            database=DBNAME,
            user=USER,
            password=PASSWORD,
        )
        db_connection.autocommit = True
        print("Successfully connected to database.")
        return db_connection

    except OperationalError as e:
        print(("Error connecting to the database.", e))
        raise e


def create_workflow(workflow_title: str) -> Dict[str, Any]:
    """
    Creates a row in the workflow table and returns the id of the
    created workflow.
    """
    connection = None
    try:
        connection = get_db_connection()
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
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")


def update_workflow(
    workflow_id: int, updated_columns: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Takes an id and an object with Workflow properties and sets the
    corresponding columns in the database to match.
    """
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        for column, value in updated_columns.items():
            if value is None:
                # Column update not sent
                continue
            if value == "":
                value = None
            elif (
                column in ("chunking_strategy", "chunks_stats", "evaluation_metrics")
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
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")


def delete_workflow(workflow_id: int) -> bool:
    """
    Deletes a workflow and returns a boolean representing whether the
    operation was successful.
    """
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "DELETE FROM workflow WHERE id = %s"
        cursor.execute(query, (workflow_id,))
        print(query)

        return cursor.rowcount > 0
    except Exception as e:
        print(("Error deleting workflow.", e))
        raise e
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")


def get_all_workflows() -> list[Dict[str, Any]]:
    """
    Returns a list containing all of the workflows stored in the database.
    """
    connection = None
    try:
        connection = get_db_connection()
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
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")


def get_workflow_info(workflow_id) -> tuple[str, ChunkerConfig]:
    """
    Retrieves both the document_title and chunking_strategy (as a ChunkerConfig)
    for a given workflow_id.
    """
    connection = None
    try:
        connection = get_db_connection()
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
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")


def get_chunker_config(workflow_id) -> ChunkerConfig:
    """
    Retrieves both the document_title and chunking_strategy (as a ChunkerConfig)
    for a given workflow_id.
    """
    connection = None
    try:
        connection = get_db_connection()
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
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")
