from django.urls import path
from main.views import display_table

app_name = 'main'

urlpatterns = [
    path('', display_table, name='display_table'),
]