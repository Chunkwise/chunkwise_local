import psycopg2
from psycopg2 import sql


def connect_db(
    host: str,
    port: int,
    user: str,
    password: str,
    dbname: str,
):
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname,
    )
    conn.autocommit = True
    return conn


def ensure_pgvector_and_table(
    conn, workflow_id: str, table_prefix: str = "workflow_", embedding_dim: int = 1536
):
    table_name = f"{table_prefix}{workflow_id}_chunks"
    cur = conn.cursor()

    # Install pgvector extension if not exists
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Create table if not exists
    create_table_sql = sql.SQL(
        """
    CREATE TABLE IF NOT EXISTS {table} (
        id BIGSERIAL PRIMARY KEY,
        workflow_id TEXT NOT NULL,
        chunk_index INTEGER NOT NULL,
        chunk_text TEXT,
        embedding vector(%s)
    );
    """
    ).format(table=sql.Identifier(table_name))
    cur.execute(create_table_sql, (embedding_dim,))

    # Create index on embedding column
    idx_sql = sql.SQL(
        "CREATE INDEX IF NOT EXISTS {idx_name} ON {table} USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);"
    ).format(
        idx_name=sql.Identifier(f"{table_name}_emb_idx"),
        table=sql.Identifier(table_name),
    )
    cur.execute(idx_sql)

    # Truncate table if exists
    cur.execute(
        sql.SQL("TRUNCATE TABLE {table};").format(table=sql.Identifier(table_name))
    )

    cur.close()
    return table_name
