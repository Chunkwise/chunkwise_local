import json
import psycopg2
from psycopg2 import OperationalError, sql
from configparser import ConfigParser
from server_types import Workflow, ChunkerConfig
from pydantic import TypeAdapter

COLUMN_NAMES = (
    "id",
    "title",
    "created_at",
    "document_title",
    "chunking_strategy",
    "chunks_stats",
    "visualization_html",
    "evaluation_metrics",
)


def format_workflow(workflow):
    formatted_result = zip(COLUMN_NAMES, workflow)
    formatted_result = dict(formatted_result)

    if type(formatted_result["chunking_strategy"]) == str:
        formatted_result["chunking_strategy"] = json.loads(
            formatted_result["chunking_strategy"]
        )

    if type(formatted_result["chunks_stats"]) == str:
        formatted_result["chunks_stats"] = json.loads(formatted_result["chunks_stats"])

    if type(formatted_result["evaluation_metrics"]) == str:
        formatted_result["evaluation_metrics"] = json.loads(
            formatted_result["evaluation_metrics"]
        )

    return formatted_result


def get_db_info(filename, section):
    """
    Returns the necessary database configs from the db_info file.
    """
    # instantiating the parser object
    parser = ConfigParser()
    parser.read(filename)

    db_info = {}
    if parser.has_section(section):
        # items() method returns (key,value) tuples
        key_val_tuple = parser.items(section)
        for item in key_val_tuple:
            db_info[item[0]] = item[1]  # index 0: key & index 1: value

    return db_info


def get_db_connection():
    """
    Creates and returns a connection object for the database.
    """
    try:
        db_info = get_db_info("db_info.ini", "chunkwise-db")
        db_connection = psycopg2.connect(**db_info)
        db_connection.autocommit = True
        print("Successfully connected to database.")
        return db_connection

    except OperationalError as e:
        print(("Error connecting to the database.", e))
        raise e


def create_workflow(workflow_title: str) -> int:
    """
    Creates a row in the workflow table and returns the id of the
    created workflow.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "INSERT INTO workflow (title) VALUES (%s) RETURNING id;"
        cursor.execute(query, (workflow_title,))
        print(query)

        id = cursor.fetchone()[0]

        query = "SELECT * FROM workflow WHERE id = %s;"
        cursor.execute(query, (id,))
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


def update_workflow(workflow_id: int, updated_columns: Workflow) -> Workflow:
    """
    Takes an id and an object with Workflow properties and sets the
    corresponding columns in the database to match.
    """
    if not isinstance(updated_columns, dict):
        updated_columns = Workflow.model_dump(updated_columns)
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        for column, value in updated_columns.items():
            if value == None:
                # Column update not sent
                continue
            if value == "":
                value = None
            elif (
                column == "chunking_strategy"
                or column == "chunks_stats"
                or column == "evaluation_metrics"
            ) and not value is None:
                if type(value) != dict:
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


def get_all_workflows() -> list[list]:
    """
    Returns a list containing all of the workflows stored in the database.
    """
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
