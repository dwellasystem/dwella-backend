# hoa/admin.py
from django.contrib import admin
from .models import HoaInformation

@admin.register(HoaInformation)
class HoaInformationAdmin(admin.ModelAdmin):
    list_display = (
        'primary_payment_method', 
        'emergency_hotline',
        'hoa_office_phone',
        'updated_at'
    )
    list_filter = ('updated_at', 'primary_payment_method')
    search_fields = ('hoa_email', 'office_address')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    filter_horizontal = ('additional_payment_methods',)
    
    fieldsets = (
        ('Payment Methods', {
            'fields': ('primary_payment_method', 'additional_payment_methods', 'reference_format')
        }),
        ('Emergency Contacts', {
            'fields': (
                'emergency_hotline', 
                'security_guard_contact', 
                'fire_department',
                'police_station',
                'hospital'
            )
        }),
        ('HOA Office', {
            'fields': ('hoa_office_phone', 'hoa_email', 'office_hours', 'office_address')
        }),
        ('Maintenance Contacts', {
            'fields': ('maintenance_contact', 'electrician_contact', 'plumber_contact'),
            'classes': ('collapse',)
        }),
        ('Important Notices', {
            'fields': ('important_notices',),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)