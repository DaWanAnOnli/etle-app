from django.shortcuts import render
import psycopg2

def display_table(request):
    connection = psycopg2.connect(
        dbname="etle_app",
        user="postgres",# Replace with your PostgreSQL username
        password="@ik4nkus",  # Replace with your PostgreSQL password
        host="localhost",
        port="5432" # Replace with your PostgreSQL IP
    )
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM violation;")
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    cursor.close()
    connection.close()

    return render(request, "table.html", {"columns": columns, "data": data})
