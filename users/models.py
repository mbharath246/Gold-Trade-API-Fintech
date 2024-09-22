from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Email id is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **kwargs):
        kwargs.setdefault('is_staff',True)
        kwargs.setdefault('is_superuser',True)
        kwargs.setdefault('is_active',True)

        if not kwargs.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True')

        if not kwargs.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True')
        return self.create_user(email=email, password=password, **kwargs)
    


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField(unique=True, null=False)
    dob = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    REQUIRED_FIELDS = ('name','dob')
    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.email