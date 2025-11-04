def normalize_document(input_path, output_path):
    """Normalize smart quotes and dashes in the document to standard ASCII characters."""

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize smart quotes and dashes for consistency
    content = content.replace('\u2018', "'")  #  → '
    content = content.replace('\u2019', "'")  # ’ → '
    content = content.replace('\u201c', '"')  # ” → "
    content = content.replace('\u201d', '"')  # " → "
    content = content.replace('\u2013', '-')  # – → -
    content = content.replace('\u2014', '-')  # — → -

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return output_path