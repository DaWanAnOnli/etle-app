from django.shortcuts import redirect, render
from datetime import datetime
from etle_app.config import get_connection
import json

from django.db.models import Q
from datetime import datetime, timedelta

def display_table(request):
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

        # Filter parameters
        time_filter = request.GET.get("time_filter", "all")
        status_filter = request.GET.getlist("status_filter", ["0", "1", "2", "3"])
        type_filter = request.GET.getlist("type_filter", ["0", "1", "2"])
        sort_order = request.GET.get("sort_order", "desc")
        page_number = int(request.GET.get("page", 1))

        # Timestamp filtering
        current_time = datetime.now()
        time_conditions = {
            "today": current_time - timedelta(days=1),
            "past_week": current_time - timedelta(weeks=1),
            "past_month": current_time - timedelta(days=30),
            "past_year": current_time - timedelta(days=365),
        }

        query_conditions = []
        if time_filter != "all":
            query_conditions.append(f"timestamp >= '{time_conditions[time_filter]}'")

        # Status filtering
        status_conditions = ",".join(status_filter)
        query_conditions.append(f"status IN ({status_conditions})")

        # Type filtering
        type_conditions = ",".join(type_filter)
        query_conditions.append(f"type IN ({type_conditions})")

        # Combine all conditions
        where_clause = " AND ".join(query_conditions)
        where_clause = f"WHERE {where_clause}" if where_clause else ""

        # Sorting
        order_clause = "ORDER BY timestamp DESC" if sort_order == "desc" else "ORDER BY timestamp ASC"

        # Pagination setup
        items_per_page = 10
        offset = (page_number - 1) * items_per_page
        limit_clause = f"LIMIT {items_per_page} OFFSET {offset}"

        # Execute the query with pagination
        query = f"SELECT id, plate_number, status, type, timestamp, location, image_url, drone, is_verified FROM violation {where_clause} {order_clause} {limit_clause};"
        cursor.execute(query)
        data = cursor.fetchall()


        # Total count for pagination
        cursor.execute(f"SELECT COUNT(*) FROM violation {where_clause};")
        total_records = cursor.fetchone()[0]
        total_pages = (total_records // items_per_page) + (1 if total_records % items_per_page > 0 else 0)


        # Pass filters, sorting, and pagination details to the template
        return render(request, "table.html", {
            "data": data,
            "filters": {
                "time_filter": time_filter,
                "status_filter": status_filter,
                "type_filter": type_filter,
                "sort_order": sort_order,
            },
            "page": page_number,
            "total_pages": total_pages,
        })

    finally:
        cursor.close()
        connection.close()
        
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
                cursor.execute("UPDATE violation SET is_verified = True WHERE id = %s", (row_id,))
            elif action == 'deny':
                cursor.execute("UPDATE violation SET status = 2 WHERE id = %s", (row_id,))
                cursor.execute("UPDATE violation SET is_verified = True WHERE id = %s", (row_id,))
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