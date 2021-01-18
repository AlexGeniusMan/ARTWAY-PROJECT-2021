from django.contrib import admin
from .models import *
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.admin import UserAdmin


class ArtifactAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    # fields = ('name', 'img', 'audio', 'description')


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'last_name', 'first_name', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (_('Авторизация'), {'fields': ('username', 'email', 'password')}),
        (_('Основная информация'),
         {'fields': ('last_name', 'first_name', 'middle_name', 'museum')}),
        # (_('Университет'), {'fields': ('university', 'faculty', 'specialty', 'course_type', 'course')}),
        # (_('Ссылки'),
        #  {'fields': ('link_vk', 'link_facebook', 'link_instagram', 'link_telegram', 'link_github', 'link_dribble')}),
        (_('Права доступа'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        # (_('Другое'), {'fields': ('last_login', 'date_joined', 'priority')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'last_name', 'first_name', 'middle_name', 'museum'),
        }),
    )


admin.site.register(Artifact, ArtifactAdmin)
admin.site.register(Museum)
admin.site.register(Location)
admin.site.register(Hall)
admin.site.register(User, CustomUserAdmin)
