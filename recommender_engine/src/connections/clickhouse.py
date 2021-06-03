from clickhouse_driver import connect

class ClickHouseConnCtxManager:
    """
    Simple Context Manager for PostgreSQL connection. Accepts dsn as separate string keywords, returns cursor object.
    """

    def __init__(self, host: str):
        self.host = host

    def __enter__(self):
        self.conn = connect(f'clickhouse://{self.host}')
        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.conn.close()
