from django.shortcuts import redirect, render
from datetime import datetime
from etle_app.config import get_connection

def display_table(request):
    session_id = request.COOKIES.get("session_id")

    if not session_id:  # No session cookie present
        return redirect('/auth/login/')

    DATABASE_CONFIG = get_connection()
    cursor = DATABASE_CONFIG.cursor()

    try:
        # Check if session is valid
        cursor.execute(
            "SELECT user_id FROM sessions WHERE session_id = %s AND expires_at > %s",
            (session_id, datetime.now())
        )
        session = cursor.fetchone()

        if not session:  # Session is invalid or expired
            return redirect('/auth/login/')

        # Session is valid; fetch the table data
        cursor.execute("SELECT * FROM violation;")
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        return render(request, "table.html", {"columns": columns, "data": data})
    finally:
        cursor.close()
        DATABASE_CONFIG.close()
