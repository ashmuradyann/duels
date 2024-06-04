from django.apps import AppConfig
from django.db.models.signals import post_migrate


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        post_migrate.connect(self.create_admin_user, sender=self)

    @staticmethod
    def create_admin_user(sender, **kwargs):
        from .models import CustomUser
        username = 'admin'
        user = CustomUser.objects.filter(username=username)
        if not user.exists():
            CustomUser.objects.create_superuser(**{
                'username': 'admin',
                'email': 'dev.vrv@gmail.com',
                'password': 'admin',
                'is_staff': True,
                'is_active': True,
                'is_superuser': True,
            })