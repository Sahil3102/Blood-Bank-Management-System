"""
Admin configuration for Blood Bank Management System.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Donor, Patient, BloodStock, BloodRequest, AllocationLog, EmergencyPost, DonorResponse


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom User Admin with role-based display."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone_number', 'address', 'city', 'state', 'zip_code')
        }),
    )


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    """Donor Admin configuration."""
    list_display = ('user', 'blood_group', 'age', 'gender', 'is_available', 'total_donations', 'can_donate')
    list_filter = ('blood_group', 'gender', 'is_available', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'blood_group', 'date_of_birth', 'gender', 'weight_kg')
        }),
        ('Donation Status', {
            'fields': ('is_available', 'last_donation_date', 'total_donations')
        }),
        ('Medical Information', {
            'fields': ('medical_conditions',),
            'classes': ('collapse',)
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Patient Admin configuration."""
    list_display = ('user', 'blood_group', 'age', 'gender', 'hospital_name', 'doctor_name')
    list_filter = ('blood_group', 'gender', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'hospital_name')
    date_hierarchy = 'created_at'


@admin.register(BloodStock)
class BloodStockAdmin(admin.ModelAdmin):
    """Blood Stock Admin with expiry status."""
    list_display = ('blood_group', 'component', 'units', 'collection_date', 'expiry_date', 'status', 'is_available')
    list_filter = ('blood_group', 'component', 'is_available', 'collection_date')
    search_fields = ('blood_group', 'storage_location', 'donor__user__username')
    date_hierarchy = 'collection_date'

    actions = ['mark_expired', 'mark_available']

    def mark_expired(self, request, queryset):
        queryset.update(is_available=False)
    mark_expired.short_description = "Mark selected stock as expired/unavailable"

    def mark_available(self, request, queryset):
        queryset.update(is_available=True)
    mark_available.short_description = "Mark selected stock as available"


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    """Blood Request Admin with status tracking."""
    list_display = ('request_id', 'patient', 'blood_group', 'units_required', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'blood_group', 'created_at')
    search_fields = ('request_id', 'patient__user__username', 'patient__user__first_name')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Request Information', {
            'fields': ('request_id', 'patient', 'blood_group', 'units_required', 'component', 'priority')
        }),
        ('Hospital Details', {
            'fields': ('hospital_name', 'hospital_address', 'doctor_name', 'required_date')
        }),
        ('Status', {
            'fields': ('status', 'units_allocated', 'allocated_by', 'allocated_at', 'rejection_reason')
        }),
        ('Additional Info', {
            'fields': ('reason',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('request_id', 'allocated_at')


@admin.register(AllocationLog)
class AllocationLogAdmin(admin.ModelAdmin):
    """Allocation Log Admin."""
    list_display = ('log_id', 'blood_request', 'blood_stock', 'units_allocated', 'allocated_by', 'allocated_at')
    list_filter = ('allocated_at',)
    search_fields = ('log_id', 'blood_request__request_id')
    date_hierarchy = 'allocated_at'
    readonly_fields = ('log_id', 'allocated_at')


@admin.register(EmergencyPost)
class EmergencyPostAdmin(admin.ModelAdmin):
    """Emergency Post Admin."""
    list_display = ('post_id', 'patient_name', 'blood_group', 'units_needed', 'urgency_level', 'is_active', 'fulfilled', 'created_at')
    list_filter = ('urgency_level', 'is_active', 'fulfilled', 'blood_group', 'created_at')
    search_fields = ('post_id', 'patient_name', 'hospital_name')
    date_hierarchy = 'created_at'

    actions = ['deactivate_posts', 'mark_fulfilled']

    def deactivate_posts(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_posts.short_description = "Deactivate selected posts"

    def mark_fulfilled(self, request, queryset):
        queryset.update(fulfilled=True, is_active=False)
    mark_fulfilled.short_description = "Mark selected posts as fulfilled"


@admin.register(DonorResponse)
class DonorResponseAdmin(admin.ModelAdmin):
    """Donor Response Admin."""
    list_display = ('emergency_post', 'donor', 'status', 'responded_at')
    list_filter = ('status', 'responded_at')
    search_fields = ('emergency_post__post_id', 'donor__user__username')
