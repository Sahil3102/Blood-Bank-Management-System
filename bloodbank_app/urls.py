"""
URL configuration for bloodbank_app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Public views
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # Authentication
    path('register/donor/', views.donor_register, name='donor_register'),
    path('register/patient/', views.patient_register, name='patient_register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),

    # Admin views
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/blood-stock/', views.admin_blood_stock, name='admin_blood_stock'),
    path('admin/stock/edit/<int:pk>/', views.admin_stock_edit, name='admin_stock_edit'),
    path('admin/stock/delete/<int:pk>/', views.admin_stock_delete, name='admin_stock_delete'),
    path('admin/donors/', views.admin_donors, name='admin_donors'),
    path('admin/donor/<int:pk>/', views.admin_donor_detail, name='admin_donor_detail'),
    path('admin/patients/', views.admin_patients, name='admin_patients'),
    path('admin/patient/<int:pk>/', views.admin_patient_detail, name='admin_patient_detail'),
    path('admin/requests/', views.admin_requests, name='admin_requests'),
    path('admin/request/approve/<int:pk>/', views.admin_request_approve, name='admin_request_approve'),
    path('admin/emergency/', views.admin_emergency_posts, name='admin_emergency_posts'),
    path('admin/logs/', views.admin_allocation_logs, name='admin_allocation_logs'),
    path('admin/create-user/', views.admin_create_user, name='admin_create_user'),

    # Donor views
    path('donor/dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('donor/profile/', views.donor_profile, name='donor_profile'),
    path('donor/availability/', views.donor_availability, name='donor_availability'),
    path('donor/emergency/', views.donor_emergency_list, name='donor_emergency_list'),
    path('donor/emergency/respond/<int:post_id>/', views.donor_respond_emergency, name='donor_respond_emergency'),
    path('donor/history/', views.donor_history, name='donor_history'),

    # Patient views
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/profile/', views.patient_profile, name='patient_profile'),
    path('patient/search/', views.patient_search, name='patient_search'),
    path('patient/request/', views.patient_request_blood, name='patient_request_blood'),
    path('patient/requests/', views.patient_requests, name='patient_requests'),
    path('patient/request/<int:pk>/', views.patient_request_detail, name='patient_request_detail'),
    path('patient/emergency/create/', views.patient_emergency_create, name='patient_emergency_create'),
    path('patient/emergency/', views.patient_emergency_list, name='patient_emergency_list'),
    path('patient/emergency/<int:pk>/', views.patient_emergency_detail, name='patient_emergency_detail'),
    path('patient/emergency/close/<int:pk>/', views.patient_emergency_close, name='patient_emergency_close'),

    # API endpoints
    path('api/check-availability/', views.check_blood_availability, name='check_blood_availability'),
    path('api/donor/<int:donor_id>/', views.get_donor_details, name='get_donor_details'),
]
