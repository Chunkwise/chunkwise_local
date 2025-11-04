def save_to_file(html_content: str) -> None:
    """
    For testing purposes only
    Receives HTML as a string
    Saves an html file
    """
    try:
        import os

        filepath = os.path.abspath("example_visualizations/visualization.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML visualization saved to: file://{filepath}")
    except IOError as e:
        raise IOError(f"Error: Could not write file '{filename}': {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred during file saving: {e}")
