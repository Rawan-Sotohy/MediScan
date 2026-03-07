# ========================================
# views.py
# ========================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib import messages
from django.core.validators import validate_email
from .models import User , Notification , ContactMessage ,UserSettings ,Prescription , ExtractedMedication ,MedicationPlan, MedicationSchedule ,ChatMessage
from .forms import UserForm
from django.http import HttpResponse , FileResponse
from django.http import HttpResponseForbidden
from datetime import datetime, timedelta
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io
from django import forms
import json
import openai  
import os
import google.generativeai as genai
from google import genai  
from google.genai import types
import re


# ========================================
# REGISTER VIEW
# ========================================

def register_view(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()
        # confirm_password = request.POST.get('confirm_password', '').strip()
        phone = request.POST.get('phone', '').strip()
        gender = request.POST.get('Gender', '').capitalize().strip()
        age = request.POST.get('age', '').strip()
        
        errors = []
        
        # ===== VALIDATION =====
        
        # 1. Name Validation
        if not name:
            errors.append("Name is required.")
        elif len(name) < 2:
            errors.append("Name must be at least 2 characters long.")
        elif len(name) > 200:
            errors.append("Name cannot exceed 200 characters.")
        elif not re.match(r'^[a-zA-Z\s]+$', name):
            errors.append("Name can only contain letters and spaces.")
        
        # 2. Email Validation
        if not email:
            errors.append("Email is required.")
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors.append("Invalid email format.")
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                errors.append("Email already registered. Please login.")
        
        # 3. Password Validation
        if not password:
            errors.append("Password is required.")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        elif not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter.")
        elif not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter.")
        elif not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one digit.")
        elif not re.search(r'[@$!%*?&#]', password):
            errors.append("Password must contain at least one special character (@$!%*?&#).")
        
        # # 4. Confirm Password Validation
        # if password != confirm_password:
        #     errors.append("Passwords do not match.")
        
        # 5. Phone Validation
        if not phone:
            errors.append("Phone number is required.")
        elif not re.match(r'^\d{11,15}$', phone):
            errors.append("Phone number must be 11-15 digits.")
        elif User.objects.filter(phone=phone).exists():
            errors.append("Phone number already registered.")
        
        # 6. Gender Validation
        if not gender:
            errors.append("Gender is required.")
        elif gender not in ['Male', 'Female']:
            errors.append("Invalid gender selection.")
        
        # 7. Age Validation
        if not age:
            errors.append("Age is required.")
        else:
            try:
                age = int(age)
                if age < 1 or age > 120:
                    errors.append("Age must be between 1 and 120.")
            except ValueError:
                errors.append("Age must be a valid number.")
        
        # ===== IF ERRORS, RETURN WITH MESSAGES =====
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'mediScanApp/register.html', {
                'name': name,
                'email': email,
                'phone': phone,
                'gender': gender,
                'age': age if isinstance(age, int) else ''
            })
        
        # ===== CREATE USER =====
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                name=name,
                phone=phone,
                gender=gender,
                age=age
            )
            messages.success(request, "Registration successful! Please login.")
            return redirect('login')
        
        except IntegrityError as e:
            messages.error(request, "An error occurred during registration. Please try again.")
            return render(request, 'mediScanApp/register.html')
        
        except Exception as e:
            messages.error(request, f"Unexpected error: {str(e)}")
            return render(request, 'mediScanApp/register.html')
    
    return render(request, 'mediScanApp/register.html')


# ========================================
# LOGIN VIEW
# ========================================

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()
        
        errors = []
        
        # ===== VALIDATION =====
        
        # 1. Email Validation
        if not email:
            errors.append("Email is required.")
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors.append("Invalid email format.")
        
        # 2. Password Validation
        if not password:
            errors.append("Password is required.")
        
        # ===== IF ERRORS, RETURN WITH MESSAGES =====
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'mediScanApp/login.html', {'email': email})
        
        # ===== AUTHENTICATE USER =====
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.name}!")
            return redirect('home')  # Change 'home' to your dashboard/home page name
        else:
            # Check if user exists but wrong password
            if User.objects.filter(email=email).exists():
                messages.error(request, "Incorrect password. Please try again.")
            else:
                messages.error(request, "No account found with this email. Please register.")
            
            return render(request, 'mediScanApp/login.html', {'email': email})
    
    return render(request, 'mediScanApp/login.html')


# ========================================
# LOGOUT VIEW
# ========================================

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


def home_view(request):
    user=User.objects.all()
    return render(request, 'mediScanApp/index.html',{'user':user})

def home_page(request):
    user=User.objects.all()
    context= {'obj':user}
    print(user)
    return render(request, 'mediScanApp/home.html',context)
# def create_schedule_from_prescription(prescription):
#     """
#     Automatically create medication schedule from extracted prescription
#     Call this after prescription is processed
#     """
#     from datetime import time
    
#     user = prescription.user
#     medications = prescription.medications.all()
    
#     # Create a new medication plan
#     plan = MedicationPlan.objects.create(
#         user=user,
#         start_date=timezone.now().date(),
#         end_date=timezone.now().date() + timedelta(days=7),  # Default 7 days
#         is_active=True
#     )
    
#     for med in medications:
#         # Parse frequency to determine dose times
#         hours_between = parse_frequency(med.frequency)
        
#         if hours_between:
#             # Create schedules based on frequency
#             # Example: 3x daily (every 8 hours) → 8am, 4pm, 12am
#             dose_times = []
            
#             if hours_between == 8:  # 3x daily
#                 dose_times = [time(8, 0), time(16, 0), time(0, 0)]
#             elif hours_between == 12:  # 2x daily
#                 dose_times = [time(8, 0), time(20, 0)]
#             elif hours_between == 6:  # 4x daily
#                 dose_times = [time(8, 0), time(14, 0), time(20, 0), time(2, 0)]
#             else:  # Once daily
#                 dose_times = [time(8, 0)]
            
#             # Create schedule entries
#             for dose_time in dose_times:
#                 MedicationSchedule.objects.create(
#                     plan=plan,
#                     medicine_name=med.medicine_name,
#                     dosage=med.dosage,
#                     dose_time=dose_time,
#                     status='upcoming'
#                 )
    
#     return plan



@login_required(login_url='login')
def notifications_view(request):
    """Display all notifications for logged-in user"""
    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count
    }
    return render(request, 'mediScanApp/notifications.html', context)


@login_required(login_url='login')
@require_POST
def mark_as_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})


@login_required(login_url='login')
@require_POST
def mark_all_as_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})


@login_required(login_url='login')
def get_notifications_api(request):
    """API endpoint to fetch new notifications (for real-time updates)"""
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    
    data = [{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'type': n.type,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for n in notifications]
    
    return JsonResponse({'notifications': data, 'count': len(data)})

@login_required(login_url='login')
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message_text = request.POST.get('message', '').strip()

        if not name or not email or not message_text:
            messages.error(request, "All fields are required.")
        else:
            ContactMessage.objects.create(
                user=request.user,
                name=name,
                email=email,
                message=message_text
            )
            messages.success(request, "Your message has been sent successfully.")
            return redirect('contact')

    return render(request, 'mediScanApp/contact2.html')

# def profile(request):
#     user=User.objects.all()
#     context= {'obj':user}
#     return render(request, 'mediScanApp/profile.html',context)

# @login_required(login_url='login')
# def updateProfile(request ,pk):
#     user=User.objects.get(id=pk)
#     form=UserForm(instance=user)
    
#     if request.user.name != user.name :
#         return HttpResponse("You Are Not Allowed Here.!")
    
#     if request.method == 'POST':
#         form =UserForm(request.POST ,instance=user)
#         if form.is_valid():
#             form.save()
#             return redirect('home')
#     context ={'form':form}
#     return render(request , 'MediScanApp/register.html',context)


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avater','name', 'email', 'phone', 'gender', 'age',]
        widgets = {
            'avater': forms.FileInput(attrs={
                'class': 'form-control',
                'accept':'image/*'
                }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
                'readonly': 'readonly'  # Email shouldn't be changed
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Age',
                'min': 1,
                'max': 120
            }),
            
        }


# ========================================
# Profile View 
# ========================================

@login_required(login_url='login')
def profile(request):
    user = request.user 
    context = {
        'user': user ,
    }
    return render(request, 'mediScanApp/profile1.html', context)


# ========================================
# Update Profile View 
# ========================================

@login_required(login_url='login')
def updateProfile(request, pk):
    """Update user profile with validation"""
    
    # Get the user to be updated
    user = get_object_or_404(User, id=pk)
    
    # Security check: Only allow users to edit their own profile
    if request.user.id != user.id:
        messages.error(request, "You are not allowed to edit this profile!")
        return HttpResponseForbidden("You are not allowed here!")
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST,request.FILES, instance=user)
        
        if form.is_valid():
            # Additional validation
            name = form.cleaned_data.get('name')
            phone = form.cleaned_data.get('phone')

            # Check if phone number is unique (excluding current user)
            if User.objects.exclude(id=user.id).filter(phone=phone).exists():
                messages.error(request, "This phone number is already registered.")
                return render(request, 'mediScanApp/update_profile.html', {'form': form})
                
            
            # Save the form
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileUpdateForm(instance=user)
    
    context = {
        'form': form,
        'user': user
    }
    return render(request, 'mediScanApp/update_profile.html', context)

@login_required(login_url='login')
def settings_view(request):
    """Display and update user settings"""
    user = request.user
    
    # Get or create user settings
    settings, created = UserSettings.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # Update profile information
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        age = request.POST.get('age', '').strip()
        
        errors = []
        
        # Validation
        if not name or len(name) < 3:
            errors.append("Name must be at least 3 characters.")
        
        if not phone or len(phone) < 11:
            errors.append("Phone number must be at least 11 digits.")
        
        # Check if phone is unique (excluding current user)
        if User.objects.exclude(id=user.id).filter(phone=phone).exists():
            errors.append("This phone number is already in use.")
        
        try:
            age = int(age)
            if age < 1 or age > 120:
                errors.append("Age must be between 1 and 120.")
        except ValueError:
            errors.append("Age must be a valid number.")
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Update user
            user.name = name
            user.phone = phone
            user.age = age
            user.save()
            
            messages.success(request, "Profile updated successfully!")
            return redirect('settings')
    
    context = {
        'user': user,
        'settings': settings
    }
    return render(request, 'mediScanApp/settings.html', context)


@login_required(login_url='login')
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        user = request.user
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        errors = []
        
        # Validate current password
        if not user.check_password(current_password):
            errors.append("Current password is incorrect.")
        
        # Validate new password
        if len(new_password) < 8:
            errors.append("New password must be at least 8 characters.")
        
        if new_password != confirm_password:
            errors.append("New passwords do not match.")
        
        if not any(c.isupper() for c in new_password):
            errors.append("Password must contain at least one uppercase letter.")
        
        if not any(c.islower() for c in new_password):
            errors.append("Password must contain at least one lowercase letter.")
        
        if not any(c.isdigit() for c in new_password):
            errors.append("Password must contain at least one digit.")
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Change password
            user.set_password(new_password)
            user.save()
            
            # Keep user logged in after password change
            update_session_auth_hash(request, user)
            
            messages.success(request, "Password changed successfully!")
            return redirect('settings')
    
    return redirect('settings')


@login_required(login_url='login')
def update_email(request):
    """Update user email"""
    if request.method == 'POST':
        user = request.user
        new_email = request.POST.get('new_email', '').strip().lower()
        password = request.POST.get('password')
        
        errors = []
        
        # Verify password
        if not user.check_password(password):
            errors.append("Password is incorrect.")
        
        # Check if email is already taken
        if User.objects.exclude(id=user.id).filter(email=new_email).exists():
            errors.append("This email is already registered.")
        
        # Validate email format
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(new_email)
        except ValidationError:
            errors.append("Invalid email format.")
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Update email
            user.email = new_email
            user.save()
            
            messages.success(request, "Email updated successfully!")
            return redirect('settings')
    
    return redirect('settings')


@login_required(login_url='login')
@require_POST
def toggle_notifications(request):
    """Toggle notification settings"""
    try:
        data = json.loads(request.body)
        enabled = data.get('enabled', True)
        
        settings, created = UserSettings.objects.get_or_create(user=request.user)
        settings.notifications_enabled = enabled
        settings.save()
        
        return JsonResponse({'success': True, 'enabled': enabled})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@login_required(login_url='login')
def upload_prescription(request):
    if request.method == 'POST':
        image = request.FILES.get('image')

        if not image:
            return render(request, 'upload.html', {
                'error': 'Please upload an image first.'
            })

        prescription = Prescription.objects.create(
            user=request.user,
            image_path=image,
            status='pending'
        )
    

        return redirect('loading', prescription_id=prescription.id)
    return render(request , 'MediScanApp/upload.html')

@login_required(login_url='login')
def loading_view(request, prescription_id):
    prescription = Prescription.objects.get(id=prescription_id)
    return render(request, 'MediScanApp/load.html', {'prescription': prescription})

@login_required(login_url='login')
def result_view(request, prescription_id):
    prescription = get_object_or_404(
        Prescription,
        id=prescription_id,
        user=request.user
    )

    medications = prescription.medications.all()  # related_name='medications'

    return render(request, 'MediScanApp/extract.html', {
        'prescription': prescription,
        'medications': medications
    })
    
@login_required(login_url='login')
def save_prescription(request, pk):
    """Mark prescription as processed"""
    prescription = get_object_or_404(Prescription, id=pk, user=request.user)
    
    # Update status
    prescription.status = 'processed'
    prescription.save()
    
    messages.success(request, "Prescription saved successfully!")
    return redirect('records')
@login_required(login_url='login')
def records_view(request):
    """Display all prescription records for logged-in user"""
    prescriptions = Prescription.objects.filter(
        user=request.user
    ).prefetch_related('medications').order_by('-uploaded_at')
    
    context = {
        'prescriptions': prescriptions
    }
    return render(request, 'mediScanApp/records.html', context)


@login_required(login_url='login')
def delete_prescription(request, pk):
    """Delete a prescription record"""
    prescription = get_object_or_404(Prescription, id=pk, user=request.user)
    
    if request.method == 'POST':
        prescription.delete()
        messages.success(request, "Prescription deleted successfully!")
        return redirect('records')
    
    return redirect('records')


@login_required(login_url='login')
def download_prescription(request, pk):
    """Download prescription as PDF"""
    prescription = get_object_or_404(Prescription, id=pk, user=request.user)
    medications = prescription.medications.all()
    
    # Create PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    p.setFont("Helvetica-Bold", 24)
    p.drawString(1*inch, height - 1*inch, "MediScan Prescription Report")
    
    # User Info
    p.setFont("Helvetica", 12)
    p.drawString(1*inch, height - 1.5*inch, f"Patient: {request.user.name}")
    p.drawString(1*inch, height - 1.7*inch, f"Date: {prescription.uploaded_at.strftime('%B %d, %Y')}")
    p.drawString(1*inch, height - 1.9*inch, f"Prescription ID: #{prescription.id}")
    
    # Draw line
    p.setStrokeColorRGB(0.4, 0.5, 0.9)
    p.setLineWidth(2)
    p.line(1*inch, height - 2.1*inch, width - 1*inch, height - 2.1*inch)
    
    # Medications
    y_position = height - 2.5*inch
    
    for idx, med in enumerate(medications, 1):
        if y_position < 2*inch:  # New page if needed
            p.showPage()
            y_position = height - 1*inch
        
        # Medicine name
        p.setFont("Helvetica-Bold", 14)
        p.drawString(1*inch, y_position, f"{idx}. {med.medicine_name}")
        y_position -= 0.3*inch
        
        # Details
        p.setFont("Helvetica", 11)
        
        if med.dosage:
            p.drawString(1.2*inch, y_position, f"Dosage: {med.dosage}")
            y_position -= 0.25*inch
        
        if med.frequency:
            p.drawString(1.2*inch, y_position, f"Frequency: {med.frequency}")
            y_position -= 0.25*inch
        
        if med.duration:
            p.drawString(1.2*inch, y_position, f"Duration: {med.duration}")
            y_position -= 0.25*inch
        
        if med.notes:
            p.drawString(1.2*inch, y_position, f"Notes: {med.notes}")
            y_position -= 0.25*inch
        
        y_position -= 0.3*inch  # Space between medicines
    
    # Footer
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(1*inch, 0.5*inch, "Generated by MediScan - Your Smart Medication Assistant")
    
    p.showPage()
    p.save()
    
    # Get PDF
    buffer.seek(0)
    
    # Return as download
    response = FileResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="prescription_{prescription.id}.pdf"'
    
    return response


# ========================================
# Alternative: Simple text download
# ========================================

@login_required(login_url='login')
def download_prescription_txt(request, pk):
    """Download prescription as text file"""
    prescription = get_object_or_404(Prescription, id=pk, user=request.user)
    medications = prescription.medications.all()
    
    # Create text content
    content = f"""
MEDISCAN PRESCRIPTION REPORT
{'='*50}

Patient: {request.user.name}
Date: {prescription.uploaded_at.strftime('%B %d, %Y')}
Prescription ID: #{prescription.id}

{'='*50}
MEDICATIONS:
{'='*50}

"""
    
    for idx, med in enumerate(medications, 1):
        content += f"""
{idx}. {med.medicine_name}
   Dosage: {med.dosage or 'N/A'}
   Frequency: {med.frequency or 'N/A'}
   Duration: {med.duration or 'N/A'}
   Notes: {med.notes or 'None'}

"""
    
    content += "\n" + "="*50 + "\n"
    content += "Generated by MediScan\n"
    
    # Return as download
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="prescription_{prescription.id}.txt"'
    
    return response

    
@login_required(login_url='login')
def medication_plan_view(request):
    """Display user's medication schedule for today"""
    user = request.user
    
    # Get active medication plans
    active_plans = MedicationPlan.objects.filter(
        user=user,
        is_active=True
    ).prefetch_related('schedules')
    
    # Get today's schedules
    today_schedules = MedicationSchedule.objects.filter(
        plan__user=user,
        plan__is_active=True
    ).select_related('plan').order_by('dose_time')
    
    # Categorize schedules
    now = timezone.now().time()
    upcoming = []
    taken = []
    missed = []
    
    for schedule in today_schedules:
        if schedule.status == 'taken':
            taken.append(schedule)
        elif schedule.status == 'missed':
            missed.append(schedule)
        else:  # upcoming
            upcoming.append(schedule)
    
    # Calculate statistics
    total_today = today_schedules.count()
    taken_count = len(taken)
    missed_count = len(missed)
    completion_rate = (taken_count / total_today * 100) if total_today > 0 else 0
    
    context = {
        'active_plans': active_plans,
        'upcoming': upcoming,
        'taken': taken,
        'missed': missed,
        'total_today': total_today,
        'taken_count': taken_count,
        'missed_count': missed_count,
        'completion_rate': round(completion_rate, 1),
    }
    
    return render(request, 'mediScanApp/medication_plan.html', context)


@login_required(login_url='login')
@require_POST
def mark_medication_taken(request, schedule_id):
    """Mark a medication as taken"""
    schedule = get_object_or_404(
        MedicationSchedule,
        id=schedule_id,
        plan__user=request.user
    )
    
    schedule.status = 'taken'
    schedule.save()
    
    # Create notification
    Notification.objects.create(
        user=request.user,
        title="Medication Taken",
        message=f"You've marked {schedule.medicine_name} as taken.",
        type='info'
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Medication marked as taken'
    })


@login_required(login_url='login')
@require_POST
def skip_medication(request, schedule_id):
    """Skip/miss a medication"""
    schedule = get_object_or_404(
        MedicationSchedule,
        id=schedule_id,
        plan__user=request.user
    )
    
    schedule.status = 'missed'
    schedule.save()
    
    # Create warning notification
    Notification.objects.create(
        user=request.user,
        title="Medication Missed",
        message=f"You've skipped {schedule.medicine_name}. Remember to take your medications on time.",
        type='warning'
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Medication marked as missed'
    })


@login_required(login_url='login')
def create_medication_plan(request):
    """Create a new medication plan from prescription"""
    if request.method == 'POST':
        prescription_id = request.POST.get('prescription_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        prescription = get_object_or_404(
            Prescription,
            id=prescription_id,
            user=request.user
        )
        
        # Create medication plan
        plan = MedicationPlan.objects.create(
            user=request.user,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        
        # Get selected medications and times from form
        medications = prescription.medications.all()
        
        for index, med in enumerate(prescription.medications.all(), start=1):
            dose_times = request.POST.getlist(f'dose_time_{index}[]')
            for dose_time in dose_times:
                if dose_time:
                    MedicationSchedule.objects.create(
                        plan=plan,
                        medicine_name=med.medicine_name,
                        dosage=med.dosage,
                        dose_time=dose_time,
                        status='upcoming'
                    )


        
        messages.success(request, "Medication plan created successfully!")
        return redirect('medication_plan')
    
    # GET request - show prescriptions to choose from
    prescriptions = Prescription.objects.filter(
        user=request.user,
        status='processed'
    ).prefetch_related('medications')
    
    return render(request, 'mediScanApp/create_plan.html', {
        'prescriptions': prescriptions
    })


@login_required(login_url='login')
def deactivate_plan(request, plan_id):
    """Deactivate a medication plan"""
    plan = get_object_or_404(
        MedicationPlan,
        id=plan_id,
        user=request.user
    )
    
    plan.is_active = False
    plan.save()
    
    messages.success(request, "Medication plan deactivated.")
    return redirect('medication_plan')

@login_required(login_url='login')
def chatbot_view(request):
    """Display chatbot page"""
    return render(request, 'mediScanApp/chat.html')

openai.api_key = os.getenv("OPENAI_API_KEY")
# openai.api_base = os.getenv("OPENAI_API_BASE")

def chat_api(request):
    if request.method == "POST":
        prompt = request.POST.get("message", "")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # OpenRouter supports GPT-compatible models
                messages=[
                    {"role": "system", "content": "You are a helpful medical assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return JsonResponse({"response": response.choices[0].message['content']})
        except Exception as e:
            return JsonResponse({"error": str(e)})
@login_required
@require_POST
def chat_api(request):
    """Handle chat messages with OpenAI"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'success': False, 'error': 'Empty message'})
        
        # Save user message
        ChatMessage.objects.create(
            user=request.user,
            sender='user',
            message=user_message
        )
        
        # Get user's medication history for context
        from .models import ExtractedMedication, Prescription
        user_medications = ExtractedMedication.objects.filter(
            prescription__user=request.user
        ).values_list('medicine_name', flat=True).distinct()
        
        medications_context = ", ".join(user_medications) if user_medications else "No medications on record"
        
        # Call OpenAI API
        openai.api_key = os.getenv('OPENAI_API_KEY')  # Set in environment variables
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a helpful medical assistant for MediScan. 
                    The user's current medications are: {medications_context}.
                    Provide helpful, accurate information about medications, dosages, and general health advice.
                    Always remind users to consult their doctor for medical decisions.
                    Be friendly, concise, and professional."""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        bot_response = response.choices[0].message.content.strip()
        
        # Save bot response
        ChatMessage.objects.create(
            user=request.user,
            sender='ai',
            message=bot_response
        )
        
        return JsonResponse({
            'success': True,
            'response': bot_response
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
        
        
# @login_required
# @require_POST
# def chat_api(request):
#     """Handle chat messages with Google Gemini"""
#     try:
#         data = json.loads(request.body)
#         user_message = data.get('message', '').strip()
        
#         if not user_message:
#             return JsonResponse({'success': False, 'error': 'Empty message'})
        
#         # Save user message
#         ChatMessage.objects.create(
#             user=request.user,
#             sender='user',
#             message=user_message
#         )
        
#         # Get medication context
#         user_medications = ExtractedMedication.objects.filter(
#             prescription__user=request.user
#         ).values_list('medicine_name', flat=True).distinct()
        
#         medications_context = ", ".join(user_medications) if user_medications else "No medications on record"
        
#         # Get API key
#         api_key = os.getenv('GOOGLE_API_KEY')
        
#         if not api_key:
#             raise Exception("API key not found")
        
#         # Configure Gemini client
#         client = genai.Client(api_key=api_key)
        
#         # Create prompt
#         prompt = f"""You are a helpful medical assistant for MediScan app.

# User's current medications: {medications_context}
# User's question: {user_message}

# Provide a helpful, accurate, and concise response about medications, dosages, or general health advice.
# Always remind users to consult their doctor for medical decisions.
# Be friendly and professional. Keep responses under 150 words."""
        
#         # Generate response - USING gemini-1.5-flash
#         response = client.models.generate_content(
#             model='gemini-1.5-flash',  # Better free tier limits
#             contents=prompt
#         )
        
#         bot_response = response.text.strip()
        
#         # Save bot response
#         ChatMessage.objects.create(
#             user=request.user,
#             sender='ai',
#             message=bot_response
#         )
        
#         return JsonResponse({
#             'success': True,
#             'response': bot_response
#         })
        
#     except Exception as e:
#         print(f"❌ CHATBOT ERROR: {str(e)}")
#         import traceback
#         traceback.print_exc()
        
#         # Provide helpful error message
#         error_msg = str(e)
#         if 'RESOURCE_EXHAUSTED' in error_msg or '429' in error_msg:
#             return JsonResponse({
#                 'success': False,
#                 'response': "I'm experiencing high demand right now. Please try again in a minute! 😊"
#             })
        
#         return JsonResponse({
#             'success': False,
#             'error': str(e)
#         })


@login_required(login_url='login')
def chat_history(request):
    """Get chat history"""
    try:
        messages = ChatMessage.objects.filter(
            user=request.user
        ).order_by('created_at')[:50]
        
        data = [{
            'sender': msg.sender,
            'message': msg.message,
            'time': msg.created_at.strftime('%H:%M')
        } for msg in messages]
        
        return JsonResponse({'messages': data})
    
    except Exception as e:
        return JsonResponse({'messages': []})