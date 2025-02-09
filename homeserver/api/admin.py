from django.contrib import admin
from api.models import User, UserFile


class UserConfig(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
    )
    readonly_fields = ("username",)


class UserFileConfig(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
    )

    def username(self, obj):
        return obj.user.username


admin.site.register(User, UserConfig)
admin.site.register(UserFile, UserFileConfig)
