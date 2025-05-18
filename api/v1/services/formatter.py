from datetime import datetime


async def format_datetime(date: datetime, format_type: str) -> str:
    types = {
        "date": "%d-%m-%Y",
        "time": "%H:%M:%S",
        "datetime": "%H:%M:%S %d-%m-%Y",
    }
    return date.strftime(types[format_type])
