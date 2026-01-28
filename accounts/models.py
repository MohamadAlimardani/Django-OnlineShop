from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone_number = models.CharField(
        max_length=11,
        unique=False,
        null=True,
        verbose_name="Phone Number"
        )
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True
    )

    def __str__(self):
        return self.username


class OtpCode(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )
    
    code = models.CharField(max_length=6)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.phone_number} - {self.code}"
    