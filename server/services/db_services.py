import psycopg2
from psycopg2 import OperationalError
from configparser import ConfigParser


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
    try:
        db_info = get_db_info("db_info.ini", "chunkwise-db")
        db_connection = psycopg2.connect(**db_info)
        print("Successfully connected to database.")

    except OperationalError:
        print("Error connecting to the database.")

    return db_connection


def create_workflow() -> int:
    try:
        pass
    except:
        pass
    finally:
        pass


def update_workflow(workflow_id: int, updated_columns):
    try:
        pass
    except:
        pass
    finally:
        pass


def delete_workflow(workflow_id: int) -> bool:
    try:
        pass
    except:
        pass
    finally:
        pass


def get_workflows() -> list:
    try:
        pass
    except:
        pass
    finally:
        pass


def get_workflow() -> list:
    try:
        pass
    except:
        pass
    finally:
        pass
