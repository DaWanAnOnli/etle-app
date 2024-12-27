from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

class MyAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my_auth'
