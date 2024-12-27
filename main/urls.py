from django.urls import path
from main.views import display_table, details

app_name = 'main'

urlpatterns = [
    path('', display_table, name='display_table'),
    path('details/<int:row_id>/', details),  # Pass row_id to details view
]