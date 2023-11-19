from django.contrib import admin
from backend.models import Settings
from django.contrib import admin
from django.contrib.auth.models import User, Group


class AccessUser(object):
    has_module_perms = has_perm = __getattr__ = lambda s, *a, **kw: True


admin.site.has_permission = lambda r: setattr(r, "user", AccessUser()) or True
admin.site.unregister(User)
admin.site.unregister(Group)


class SettingsAdmin(admin.ModelAdmin):
    has_module_perms = has_perm = __getattr__ = lambda s, *a, **kw: True


admin.site.register(Settings, SettingsAdmin)
