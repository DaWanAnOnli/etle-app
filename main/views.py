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


def details(request, row_id):
    session_id = request.COOKIES.get("session_id")

    # Check if the user is logged in
    if not session_id:
        return redirect('/auth/login/')

    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Check session validity
        cursor.execute(
            "SELECT user_id FROM sessions WHERE session_id = %s AND expires_at > %s",
            (session_id, datetime.now())
        )
        session = cursor.fetchone()
        if not session:
            return redirect('/auth/login/')

        if request.method == 'POST':
            # Handle Confirm or Deny actions
            action = request.POST.get('action')
            if action == 'confirm':
                cursor.execute("UPDATE violation SET status = 1 WHERE id = %s", (row_id,))
            elif action == 'deny':
                cursor.execute("UPDATE violation SET status = 2 WHERE id = %s", (row_id,))
            connection.commit()
            return redirect('/')

        # Fetch row details
        cursor.execute("SELECT * FROM violation WHERE id = %s", (row_id,))
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]

        # Prepare zipped data
        details_data = zip(columns, row)

        return render(request, "details.html", {"details_data": details_data})
    finally:
        cursor.close()
        connection.close()