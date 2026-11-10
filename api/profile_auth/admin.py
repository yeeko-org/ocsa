from django.contrib import admin

from profile_auth.models import User
from profile_auth.signals import blocking_relations
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone', 'full_editor')}),
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': (
            'first_name', 'last_name', 'email', 'phone')}),
        ('Permissions', {
            'fields': ('is_superuser', 'is_staff', 'full_editor', 'is_active'),
        }),
        ('Groups', {'fields': ('groups',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # ) + UserAdmin.fieldsets
    list_display = (
        'email', 'first_name', 'last_name',
        'is_active', 'full_editor', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-is_active', 'email')
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'groups', 'full_editor')

    def get_deleted_objects(self, objs, request):
        deleted, model_count, perms_needed, protected = (
            super().get_deleted_objects(objs, request))
        # The guard raises ProtectedError only at the confirmation POST, a
        # 500; listed here, the admin refuses with its own protected page.
        protected = list(protected)
        for user in objs:
            protected += [f"Usuario «{user}»: {relation}"
                          for relation in blocking_relations(user)]
        return deleted, model_count, perms_needed, protected
