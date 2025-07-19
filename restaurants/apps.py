from django.apps import AppConfig
from django.db.models.signals import post_migrate


class RestaurantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'restaurants'

    def ready(self):
        # Delay import until app registry is ready
        from django.contrib.auth import get_user_model

        User = get_user_model()

        def create_default_superuser(sender, **kwargs):
            if not User.objects.filter(username="admin").exists():
                print("Creating default superuser 'admin' / '123456'")
                User.objects.create_superuser(
                    username="admin",
                    email="admin@example.com",  # adjust as you like
                    password="123456",
                )

        post_migrate.connect(create_default_superuser, sender=self)