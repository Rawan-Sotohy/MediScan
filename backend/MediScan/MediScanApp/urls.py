from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home', views.home_page, name='homePage'),
    path('contact/', views.contact_view, name='contact'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('notifications/mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('api/notifications/', views.get_notifications_api, name='get_notifications_api'),
    path('profile/', views.profile, name='profile'),
    path('update-profile/<int:pk>/' ,views.updateProfile ,name="updateProfile"),
    path('settings/', views.settings_view, name='settings'),
    path('settings/change-password/', views.change_password, name='change_password'),
    path('settings/update-email/', views.update_email, name='update_email'),
    path('settings/toggle-notifications/', views.toggle_notifications, name='toggle_notifications'),
    path('upload/', views.upload_prescription, name='upload'),
    path('loading/<int:prescription_id>/', views.loading_view, name='loading'),
    path('result/<int:prescription_id>/', views.result_view, name='result'),
    path('records/', views.records_view, name='records'),
    path('prescriptions/save/<int:pk>/', views.save_prescription, name='save_prescription'),
    path('prescriptions/delete/<int:pk>/', views.delete_prescription, name='delete_prescription'),
    path('prescriptions/download/<int:pk>/', views.download_prescription, name='download_prescription'),
    # Alternative text download:
    path('prescriptions/download-txt/<int:pk>/', views.download_prescription_txt, name='download_prescription_txt'),
    path('medication-plan/', views.medication_plan_view, name='medication_plan'),
    path('medication/mark-taken/<int:schedule_id>/', views.mark_medication_taken, name='mark_medication_taken'),
    path('medication/skip/<int:schedule_id>/', views.skip_medication, name='skip_medication'),
    path('medication/create-plan/', views.create_medication_plan, name='create_plan'),
    path('medication/deactivate/<int:plan_id>/', views.deactivate_plan, name='deactivate_plan'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('api/chat/', views.chat_api, name='chat_api'),  # or chat_api_simple
    path('api/chat/history/', views.chat_history, name='chat_history'),
]