from django.contrib import admin
from .models import alumni as Alumnus
from .models import invites as Invite
from .models import invite_links as InviteLink


class AlumnusAdmin(admin.ModelAdmin):
    search_fields = ('full_name', 'year', 'letter')
    ordering = ('full_name',)


admin.site.register(Alumnus, AlumnusAdmin)
admin.site.register(Invite)
admin.site.register(InviteLink)
