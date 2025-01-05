import psycopg2


import psycopg2

def get_connection():
    """
    Returns a new connection to the PostgreSQL database.
    """
    return psycopg2.connect(
    dbname="etle_app",
    user="joel",
    password="ik4nkus",  # Replace with your PostgreSQL password
    host="35.208.155.0",
    port="5432"
)