from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    Prescription,
    ExtractedMedication,
    MedicationPlan,
    MedicationSchedule,
    Notification,
    ChatMessage,
    UserSettings,
    ContactMessage
)

# ======================
# USER
# ======================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['id', 'name', 'email', 'gender', 'age', 'avater','phone', 'is_staff']
    ordering = ['id']
    search_fields = ['email', 'name', 'phone']
    list_filter = ['gender', 'is_staff', 'is_active']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone', 'gender', 'age' , 'avater')}),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'name',
                'phone',
                'gender',
                'age',
                'password1',
                'password2',
                'is_staff',
                'is_active'
            )
        }),
    )

    readonly_fields = ['date_joined', 'last_login']


# ======================
# PRESCRIPTIONS
# ======================
class ExtractedMedicationInline(admin.TabularInline):
    model = ExtractedMedication
    extra = 1


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'uploaded_at']
    list_filter = ['status', 'uploaded_at']
    search_fields = ['user__name', 'user__email']
    ordering = ['-uploaded_at']
    readonly_fields = ['uploaded_at']
    inlines = [ExtractedMedicationInline]


# ======================
# EXTRACTED MEDICATION
# ======================
@admin.register(ExtractedMedication)
class ExtractedMedicationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'medicine_name',
        'dosage',
        'frequency',
        'duration',
        'confidence_score'
    ]
    search_fields = ['medicine_name']
    ordering = ['-id']


# ======================
# MEDICATION PLAN
# ======================
class MedicationScheduleInline(admin.TabularInline):
    model = MedicationSchedule
    extra = 1


@admin.register(MedicationPlan)
class MedicationPlanAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'start_date',
        'end_date',
        'is_active',
        'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__name', 'user__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    inlines = [MedicationScheduleInline]


# ======================
# MEDICATION SCHEDULE
# ======================
@admin.register(MedicationSchedule)
class MedicationScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'medicine_name',
        'dosage',
        'dose_time',
        'status',
        'plan'
    ]
    list_filter = ['status', 'dose_time']
    search_fields = ['medicine_name']
    ordering = ['dose_time']


# ======================
# NOTIFICATIONS
# ======================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'type', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['title', 'message']
    ordering = ['-created_at']


# ======================
# CHAT MESSAGES
# ======================
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'sender', 'message', 'created_at']
    list_filter = ['sender', 'created_at']
    search_fields = ['message']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


# ======================
# USER SETTINGS
# ======================
@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'notifications_enabled',
        'dark_mode',
        'language'
    ]
    list_filter = ['notifications_enabled', 'dark_mode', 'language']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'user', 'created_at')
    search_fields = ('name', 'email', 'message')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)