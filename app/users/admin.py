from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdmin(DjangoUserAdmin):
    """ Убираем из админки пользователя поле username. """
    fieldsets = (
        (
            (None, {'fields': ('email', 'password')}),
            (
                _('Personal info'),
                {'fields': ('first_name', 'last_name',)}
            ),
        ) +
        DjangoUserAdmin.fieldsets[2:]
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2'),
            },
        ),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    ordering = ('email',)


admin.site.register(User, UserAdmin)
