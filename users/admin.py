from django.contrib import admin
from users.models import CustomUser
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    list_display = ('id','name', 'email','dob', 'is_active', # 'modified_at','created_at',
                    'is_staff', 'is_superuser', 'last_login',)
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('name', 'email', 'password','modified_at')}),
        ('Permissions', {'fields': ('is_staff', 'is_active',
            'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('-created_at',)


admin.site.register(CustomUser, CustomUserAdmin)