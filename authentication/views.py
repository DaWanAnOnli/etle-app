import uuid
import bcrypt
from django.http import JsonResponse
import psycopg2
from datetime import datetime, timedelta
from etle_app.config import get_connection
from django.shortcuts import render, redirect



def signup(request):
    session_id = request.COOKIES.get("session_id")

    # If the user is already logged in, redirect to the main page
    if session_id:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT user_id FROM sessions WHERE session_id = %s AND expires_at > %s",
                (session_id, datetime.now())
            )
            session = cursor.fetchone()
            if session:
                return redirect('/')
        finally:
            cursor.close()
            connection.close()

    if request.method == 'POST':
        data = request.POST
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return render(request, "signup.html", {"error": "Username and password are required."})

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hashed_password)
            )
            connection.commit()
            return redirect('/auth/login/')
        except psycopg2.IntegrityError:
            connection.rollback()
            return render(request, "signup.html", {"error": "Username already exists."})
        finally:
            cursor.close()
            connection.close()

    return render(request, "signup.html")



from django.shortcuts import redirect

def login(request):
    session_id = request.COOKIES.get("session_id")

    # If the user is already logged in, redirect to the main page
    if session_id:

        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT user_id FROM sessions WHERE session_id = %s AND expires_at > %s",
                (session_id, datetime.now())
            )
            session = cursor.fetchone()
            if session:
                return redirect('/')
        finally:
            cursor.close()
            connection.close()

    if request.method == 'POST':
        data = request.POST
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return render(request, "login.html", {"error": "Username and password are required."})

        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user is None or not bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
                return render(request, "login.html", {"error": "Invalid credentials."})

            # Create a session
            session_id = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(hours=1)

            cursor.execute(
                "INSERT INTO sessions (session_id, user_id, expires_at) VALUES (%s, %s, %s)",
                (session_id, user[0], expires_at)
            )
            connection.commit()

            # Redirect to main page
            response = redirect('/')
            response.set_cookie("session_id", session_id, httponly=True, expires=expires_at)
            return response
        finally:
            cursor.close()
            connection.close()

    return render(request, "login.html")


def logout(request):
    session_id = request.COOKIES.get("session_id")
    if session_id:
        DATABASE_CONFIG = get_connection()
        cursor = DATABASE_CONFIG.cursor()

        try:
            cursor.execute("DELETE FROM sessions WHERE session_id = %s", (session_id,))
            DATABASE_CONFIG.commit()
            response = redirect('/auth/login/')
            response.delete_cookie("session_id")
            return response
        finally:
            cursor.close()
            DATABASE_CONFIG.close()

    return redirect('/auth/login/')