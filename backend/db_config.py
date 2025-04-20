from typing import Dict, Any


def get_db_config() -> Dict[str, Any]:
    """
    Centralized database configuration
    Returns a dictionary with database connection parameters
    """
    return {
        "host": "localhost",
        "user": "fastapi_user",
        "password": "fastApi_Pass456!",
        "database": "fastapi_db",
        "port": 3306,
    }
