def normalize_document(content):
    """Normalize smart quotes and dashes in the document to standard ASCII characters."""

    # Normalize smart quotes and dashes for consistency
    content = content.replace("\u2018", "'")  #  → '
    content = content.replace("\u2019", "'")  # ’ → '
    content = content.replace("\u201c", '"')  # ” → "
    content = content.replace("\u201d", '"')  # " → "
    content = content.replace("\u2013", "-")  # – → -
    content = content.replace("\u2014", "-")  # — → -

    return content
