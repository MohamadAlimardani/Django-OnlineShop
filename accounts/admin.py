from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.admin.sites import NotRegistered
from django.utils.translation import gettext_lazy as _

User = get_user_model()

try:
    admin.site.unregister(Group)
except NotRegistered:
    pass


@admin.register(Group)
class GroupAdmin(DjangoGroupAdmin):
    search_fields = ("name",)


try:
    admin.site.unregister(Permission)
except NotRegistered:
    pass


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    search_fields = ("name", "codename", "content_type__app_label", "content_type__model")
    list_filter = ("content_type__app_label", "content_type__model")
    ordering = ("content_type__app_label", "content_type__model", "codename")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "username",
        "phone_number",
        "is_staff",
        "is_active",
        "date_joined",
        "last_login",
    )
    
    list_filter = ("is_staff", "is_active", "is_superuser", "groups")
    
    list_display_links = ("id", "username")
    
    search_fields = ("username", "phone_number", "email", "first_name", "last_name")
    
    ordering = ("-date_joined", "is_staff", "-last_login")
    
    list_per_page = 50
    
    readonly_fields = ("last_login", "date_joined")
    
    autocomplete_fields = ("groups", "user_permissions")
    
    fieldsets = (
        (_("Account"), {
            "classes": ("wide",),
            "fields": ("username", "password")
            }),
        
        (_("Personal Info"), {
            "classes": ("wide",),
            "fields": ("first_name", "last_name", "phone_number", "email")
            }),
        
        (_("Permissions"), {
            "classes": ("wide", "collapse"),
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
            }),
        
        (_("Important Dates"), {
            "classes": ("wide", "collapse"),
            "fields": ("last_login", "date_joined")
            }),
    )
    
    add_fieldsets = (
        ("Create Account", {
            "classes": ("wide",),
            "fields": ("username", "phone_number", "email", "password1", "password2", "is_staff", "is_active"),
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        
        if not request.user.is_superuser:
            readonly += [
                "is_superuser",
                "groups",
                "user_permissions",
            ]
        
        return readonly
