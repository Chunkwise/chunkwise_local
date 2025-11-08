"""
Contains the delete_file function.
"""

import os


def delete_file(file_path):
    """
    Deletes a file based on the specified path/document_id
    """
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print("The file does not exist")
