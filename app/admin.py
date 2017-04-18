from django.contrib import admin

from .models import Application
from .models import alumni as Alumnus
from .models import invites as Invite
from .models import invite_links as InviteLink


class AlumnusAdmin(admin.ModelAdmin):
    search_fields = ('full_name', 'year', 'letter')
    ordering = ('full_name',)


class InviteAdmin(admin.ModelAdmin):
    list_display = ('alumni', 'code', 'status', 'disabled_at')
    ordering = ('alumni__full_name',)


admin.site.register(Alumnus, AlumnusAdmin)
admin.site.register(Invite, InviteAdmin)
admin.site.register(InviteLink)
admin.site.register(Application)
