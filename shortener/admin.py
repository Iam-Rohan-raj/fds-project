from django.contrib import admin
from .models import URL, Click


class ClickInline(admin.TabularInline):
    model = Click
    extra = 0
    readonly_fields = ['clicked_at', 'ip_address', 'user_agent', 'referer', 'device_type']
    can_delete = False


@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ['get_short_identifier', 'original_url', 'click_count', 'is_active', 'created_at', 'expires_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['original_url', 'short_code', 'custom_alias', 'title']
    readonly_fields = ['short_code', 'click_count', 'created_at']
    inlines = [ClickInline]
    list_per_page = 25

    def get_short_identifier(self, obj):
        return obj.get_short_identifier()
    get_short_identifier.short_description = 'Short Code'


@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ['url', 'clicked_at', 'ip_address', 'device_type', 'referer']
    list_filter = ['device_type', 'clicked_at']
    search_fields = ['url__short_code', 'ip_address']
    readonly_fields = ['clicked_at']
