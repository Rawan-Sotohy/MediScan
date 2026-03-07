from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # This hashes the password
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    GENDER_CHOICES = [
        ("Female", "Female"),
        ("Male", "Male")
    ]
    
    phone_validator = RegexValidator(
        regex=r'^\d{11,15}$',
        message="Phone number must be 11 to 15 digits."
    )
    username = None
    
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(unique=True, max_length=15, validators=[phone_validator])
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(120)],null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    avater=models.ImageField(null=True, default='img/profile.jpg')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  
    
    # Use custom manager
    objects = UserManager()
    
    def __str__(self):
        return self.name
    



# ======================
# PRESCRIPTIONS
# ======================
class Prescription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions')
    image_path = models.ImageField(upload_to='prescriptions/')  # or FileField for general files
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'prescriptions'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Prescription #{self.id} - {self.user.name} - {self.status}"


# ======================
# EXTRACTED MEDICATIONS
# ======================
class ExtractedMedication(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medications')
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50, blank=True, null=True)
    frequency = models.CharField(max_length=50, blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    confidence_score = models.FloatField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    class Meta:
        db_table = 'extracted_medications'
    
    def __str__(self):
        return f"{self.medicine_name} - {self.prescription.id}"


# ======================
# MEDICATION PLANS
# ======================
class MedicationPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medication_plans')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'medication_plans'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Plan #{self.id} - {self.user.name} - {'Active' if self.is_active else 'Inactive'}"


# ======================
# MEDICATION SCHEDULE
# ======================
class MedicationSchedule(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('taken', 'Taken'),
        ('missed', 'Missed'),
    ]
    
    plan = models.ForeignKey(MedicationPlan, on_delete=models.CASCADE, related_name='schedules')
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50, blank=True, null=True)
    dose_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    
    class Meta:
        db_table = 'medication_schedule'
        ordering = ['dose_time']
    
    def __str__(self):
        return f"{self.medicine_name} at {self.dose_time} - {self.status}"


# ======================
# NOTIFICATIONS
# ======================
class Notification(models.Model):
    TYPE_CHOICES = [
        ('reminder', 'Reminder'),
        ('warning', 'Warning'),
        ('info', 'Info'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100, blank=True, null=True)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.type.upper()}: {self.title} - {self.user.name}"


# ======================
# CHAT MESSAGES
# ======================
class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender}: {self.message[:50]}..."


# ======================
# USER SETTINGS
# ======================
class UserSettings(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ar', 'Arabic'),
        ('fr', 'French'),
        ('es', 'Spanish'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settings')
    notifications_enabled = models.BooleanField(default=True)
    dark_mode = models.BooleanField(default=True)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='en')
    
    class Meta:
        db_table = 'user_settings'
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'
    
    def __str__(self):
        return f"Settings for {self.user.name}"
    
class ContactMessage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contact_messages'
    )
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contact_messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.email}"
