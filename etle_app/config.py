import psycopg2


import psycopg2

def get_connection():
    """
    Returns a new connection to the PostgreSQL database.
    """
    return psycopg2.connect(
    dbname="etle_app",
    user="postgres",
    password="abcd",  # Replace with your PostgreSQL password
    host="localhost",
    port="5432"
)