from clickhouse_driver import connect

ch: connect = None


# Функция понадобится при внедрении зависимостей


async def get_clickhouse() -> connect:
    return ch
