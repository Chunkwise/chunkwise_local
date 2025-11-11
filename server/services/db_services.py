import json
import psycopg2
from psycopg2 import OperationalError
from configparser import ConfigParser
from server_types import Workflow, ChunkerConfig


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


def create_workflow() -> int:
    """
    Creates a row in the workflow table and returns the id of the
    created workflow.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "INSERT INTO workflow DEFAULT VALUES RETURNING id;"
        cursor.execute(query)
        print(query)

        result = cursor.fetchone()[0]
        return result
    except Exception as e:
        print(("Error creating workflow.", e))
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")


def update_workflow(workflow_id: int, updated_columns: Workflow) -> Workflow:
    """
    Takes an id and an object with Workflow properties and sets the
    corresponding columns in the database to match.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "YOUR QUERY HERE"
        cursor.execute(query)
        print(query)

        result = cursor.fetchone()
        return result
    except Exception as e:
        print(("Error updating workflow.", e))
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
        return result
    except Exception as e:
        print(("Error retrieving workflows.", e))
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")


def get_chunker_configuration(workflow_id) -> ChunkerConfig:
    """
    Takes an id and returns the chunking_strategy column for that row.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT chunking_strategy FROM workflow WHERE id = %s"
        cursor.execute(query, (workflow_id,))
        print(query)

        result = cursor.fetchone()
        chunker_config = json.loads(result[0])
        return chunker_config
    except Exception as e:
        print(("Error retrieving chunker configuration.", e))
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")
