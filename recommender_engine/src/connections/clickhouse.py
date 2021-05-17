import clickhouse_driver


class ClickHouseConnCtxManager:
    """
    Simple Context Manager for ClickHouse connection. Accepts dsn as separate string keywords, returns cursor object.
    """

    def __init__(self, host: str, database: str, user: str, password: str):
        self.dsn = {"host": host,
                    "database": database,
                    "user": user,
                    "password": password}

    def __enter__(self):
        self.conn = clickhouse_driver.connect(**self.dsn)
        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.conn.close()
