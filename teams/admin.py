from django.contrib import admin
from .models import Conference, Division, Team, Season


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'created_at']
    search_fields = ['name', 'abbreviation']
    ordering = ['name']


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'conference', 'created_at']
    list_filter = ['conference']
    search_fields = ['name', 'abbreviation', 'conference__name']
    ordering = ['conference__name', 'name']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'abbreviation', 'division', 'conference', 'is_active']
    list_filter = ['division__conference', 'division', 'is_active']
    search_fields = ['name', 'city', 'abbreviation']
    ordering = ['city', 'name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'city', 'abbreviation', 'division')
        }),
        ('Details', {
            'fields': ('founded_year', 'arena_name', 'arena_capacity')
        }),
        ('Branding', {
            'fields': ('primary_color', 'secondary_color', 'logo_url'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_current', 'created_at']
    list_filter = ['is_current']
    search_fields = ['name']
    ordering = ['-start_date']
    readonly_fields = ['created_at']
