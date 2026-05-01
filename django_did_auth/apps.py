from django.apps import AppConfig


class DjangoDidAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_did_auth'
    verbose_name = "Django Secure Auth"
    label = 'django_did_auth'  # Important if you have naming conflicts

    def ready(self):
        """
        Called when Django starts.
        You can put signal registrations or other initialization here.
        """
        # Optional: Import signals or hooks if needed in the future
        pass