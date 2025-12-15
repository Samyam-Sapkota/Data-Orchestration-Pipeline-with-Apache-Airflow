# etl/load.py

from airflow.providers.postgres.hooks.postgres import PostgresHook

def pandas_dtype_to_postgres(dtype):
    if "int" in str(dtype):
        return "INTEGER"
    if "float" in str(dtype):
        return "FLOAT"
    return "TEXT"


def load_to_postgres(df, table_name, postgres_conn_id):
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    conn = hook.get_conn()
    cursor = conn.cursor()

    # ---- CREATE TABLE QUERY ----
    columns = []
    for col, dtype in df.dtypes.items():
        pg_type = pandas_dtype_to_postgres(dtype)
        columns.append(f"{col} {pg_type}")

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join(columns)}
    );
    """

    cursor.execute(create_table_sql)

    # ---- INSERT DATA ----
    insert_sql = f"""
    INSERT INTO {table_name} ({', '.join(df.columns)})
    VALUES ({', '.join(['%s'] * len(df.columns))})
    """

    for row in df.itertuples(index=False):
        cursor.execute(insert_sql, tuple(row))

    conn.commit()
    cursor.close()
    conn.close()
