import psycopg2
from datetime import datetime
from django.http import JsonResponse
from etle_app.config import get_connection

def session_middleware(get_response):
    def middleware(request):
        session_id = request.COOKIES.get("session_id")
        if session_id:
            DATABASE_CONFIG = get_connection()
            cursor = DATABASE_CONFIG.cursor()

            try:
                cursor.execute(
                    "SELECT user_id FROM sessions WHERE session_id = %s AND expires_at > %s",
                    (session_id, datetime.now())
                )
                session = cursor.fetchone()

                if session:
                    request.user_id = session[0]  # Attach user ID to the request
                else:
                    request.user_id = None
            finally:
                cursor.close()
                DATABASE_CONFIG.close()
        else:
            request.user_id = None

        return get_response(request)

    return middleware
