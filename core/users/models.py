# models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
import uuid


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if self.model.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password=password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    photo = models.URLField(null=True, blank=True)

    balance = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    leaves = models.PositiveIntegerField(default=0)

    auth_types = (
        ('telegram', 'Telegram'),
        ('vk', 'VK'),
        ('google', 'Google'),
        ('default', 'Default')
    )
    auth_type = models.CharField(max_length=10, choices=auth_types, default='default')
    api_id = models.CharField(max_length=150, null=True, blank=True)

    uuid = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    is_authenticated = models.BooleanField(default=False)
    telegram_id = models.CharField(max_length=150, unique=True, null=True, blank=True)

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class UserQuestions(models.Model):
    user = models.ForeignKey(CustomUser, related_name='questions', on_delete=models.CASCADE)
    question_type_choices = (
        ('general', 'General'),
        ('technical', 'Technical'),
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
        ('other', 'Other')
    )
    question_type = models.CharField(max_length=10, choices=question_type_choices, default='other')
    question = models.TextField(blank=True)
    answer = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = 'User Question'
        verbose_name_plural = 'User Questions'


class Report(models.Model):
    report_choices = (
        ('cheating', 'Cheating'),
        ('insult', 'Insult'),
        ('foul', 'Foul'),
        ('other', 'Other')
    )
    result_choices = (
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
    )

    user = models.ForeignKey(CustomUser, related_name='reports', on_delete=models.PROTECT)
    reported_user = models.ForeignKey(CustomUser, related_name='reported', on_delete=models.PROTECT)

    report_type = models.CharField(max_length=10, choices=report_choices, default='other')
    result_type = models.CharField(max_length=10, choices=result_choices, default='pending')

    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} reported {self.reported_user.username} for {self.report_type}'

    class Meta:
        unique_together = ('user', 'reported_user')
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
