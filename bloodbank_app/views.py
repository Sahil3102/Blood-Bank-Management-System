"""
Views for Blood Bank Management System.
Implements role-based access control and blood allocation with transaction safety.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import date, timedelta

from .models import (
    CustomUser, Donor, Patient, BloodStock, 
    BloodRequest, AllocationLog, EmergencyPost, DonorResponse
)
from .forms import (
    DonorRegistrationForm, PatientRegistrationForm, LoginForm,
    DonorProfileForm, PatientProfileForm, BloodStockForm,
    BloodRequestForm, BloodRequestApprovalForm, EmergencyPostForm,
    DonorResponseForm, AdminUserCreationForm, DateRangeFilterForm
)
from .decorators import admin_required, donor_required, patient_required


# ==================== PUBLIC VIEWS ====================

def home(request):
    """Landing page with live statistics."""
    # Get live statistics
    total_donors = Donor.objects.filter(is_available=True).count()
    total_patients = Patient.objects.count()

    # Blood stock summary by group
    blood_stock = {}
    for group_code, group_name in BloodStock.BLOOD_GROUPS:
        total_units = BloodStock.get_total_units(blood_group=group_code)
        blood_stock[group_code] = {
            'units': total_units,
            'donors': Donor.objects.filter(blood_group=group_code, is_available=True).count()
        }

    # Recent emergency posts (active only)
    emergency_posts = EmergencyPost.objects.filter(
        is_active=True, 
        fulfilled=False,
        deadline__gt=timezone.now()
    ).order_by('-created_at')[:5]

    # Statistics
    stats = {
        'total_donors': total_donors,
        'total_patients': total_patients,
        'total_requests': BloodRequest.objects.count(),
        'fulfilled_requests': BloodRequest.objects.filter(status='fulfilled').count(),
        'total_units_collected': BloodStock.objects.aggregate(total=Sum('units'))['total'] or 0,
        'emergency_posts': EmergencyPost.objects.filter(is_active=True, fulfilled=False).count(),
    }

    context = {
        'blood_stock': blood_stock,
        'emergency_posts': emergency_posts,
        'stats': stats,
    }
    return render(request, 'bloodbank_app/home.html', context)


def about(request):
    """About page."""
    return render(request, 'bloodbank_app/about.html')


def contact(request):
    """Contact page."""
    return render(request, 'bloodbank_app/contact.html')


# ==================== AUTHENTICATION VIEWS ====================

def donor_register(request):
    """Donor registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DonorRegistrationForm()

    return render(request, 'bloodbank_app/donor_register.html', {'form': form})


def patient_register(request):
    """Patient registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PatientRegistrationForm()

    return render(request, 'bloodbank_app/patient_register.html', {'form': form})


def user_login(request):
    """Unified login view for all user types."""
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or username}!')
                return redirect('dashboard_redirect')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'bloodbank_app/login.html', {'form': form})


@login_required
def user_logout(request):
    """Logout view."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on user role."""
    if request.user.is_admin:
        return redirect('admin_dashboard')
    elif request.user.is_donor:
        return redirect('donor_dashboard')
    elif request.user.is_patient_user:
        return redirect('patient_dashboard')
    else:
        messages.error(request, 'Unknown user role.')
        return redirect('home')


# ==================== ADMIN VIEWS ====================

@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard with comprehensive statistics."""
    # Statistics
    stats = {
        'total_donors': Donor.objects.count(),
        'available_donors': Donor.objects.filter(is_available=True).count(),
        'total_patients': Patient.objects.count(),
        'pending_requests': BloodRequest.objects.filter(status='pending').count(),
        'approved_requests': BloodRequest.objects.filter(status='approved').count(),
        'fulfilled_requests': BloodRequest.objects.filter(status='fulfilled').count(),
        'total_emergency': EmergencyPost.objects.filter(is_active=True).count(),
        'expired_stock': BloodStock.objects.filter(expiry_date__lt=date.today()).count(),
    }

    # Blood stock by group
    blood_summary = []
    for group_code, group_name in BloodStock.BLOOD_GROUPS:
        total_units = BloodStock.get_total_units(blood_group=group_code)
        blood_summary.append({
            'group': group_code,
            'units': total_units,
            'donors': Donor.objects.filter(blood_group=group_code).count()
        })

    # Recent activity
    recent_requests = BloodRequest.objects.order_by('-created_at')[:10]
    recent_emergency = EmergencyPost.objects.order_by('-created_at')[:5]

    # Critical stock (expiring within 7 days)
    critical_stock = BloodStock.objects.filter(
        expiry_date__lte=date.today() + timedelta(days=7),
        expiry_date__gte=date.today(),
        is_available=True
    ).order_by('expiry_date')[:10]

    context = {
        'stats': stats,
        'blood_summary': blood_summary,
        'recent_requests': recent_requests,
        'recent_emergency': recent_emergency,
        'critical_stock': critical_stock,
    }
    return render(request, 'bloodbank_app/admin_dashboard.html', context)


@login_required
@admin_required
def admin_blood_stock(request):
    """Manage blood stock inventory."""
    if request.method == 'POST':
        form = BloodStockForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blood stock added successfully!')
            return redirect('admin_blood_stock')
    else:
        form = BloodStockForm()

    # Filter and pagination
    blood_group_filter = request.GET.get('blood_group', '')
    queryset = BloodStock.objects.all().order_by('-created_at')

    if blood_group_filter:
        queryset = queryset.filter(blood_group=blood_group_filter)

    paginator = Paginator(queryset, 20)
    page = request.GET.get('page')
    stock_list = paginator.get_page(page)

    context = {
        'form': form,
        'stock_list': stock_list,
        'blood_groups': BloodStock.BLOOD_GROUPS,
        'filter': blood_group_filter,
    }
    return render(request, 'bloodbank_app/admin_blood_stock.html', context)


@login_required
@admin_required
def admin_stock_edit(request, pk):
    """Edit blood stock entry."""
    stock = get_object_or_404(BloodStock, pk=pk)
    if request.method == 'POST':
        form = BloodStockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blood stock updated successfully!')
            return redirect('admin_blood_stock')
    else:
        form = BloodStockForm(instance=stock)

    return render(request, 'bloodbank_app/admin_stock_edit.html', {'form': form, 'stock': stock})


@login_required
@admin_required
def admin_stock_delete(request, pk):
    """Delete blood stock entry."""
    stock = get_object_or_404(BloodStock, pk=pk)
    if request.method == 'POST':
        stock.delete()
        messages.success(request, 'Blood stock deleted successfully!')
        return redirect('admin_blood_stock')
    return render(request, 'bloodbank_app/admin_stock_delete.html', {'stock': stock})


@login_required
@admin_required
def admin_donors(request):
    """Manage donors list."""
    donors = Donor.objects.select_related('user').all().order_by('-created_at')

    # Filters
    blood_group = request.GET.get('blood_group', '')
    availability = request.GET.get('availability', '')

    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    if availability:
        donors = donors.filter(is_available=availability == 'available')

    paginator = Paginator(donors, 20)
    page = request.GET.get('page')
    donor_list = paginator.get_page(page)

    context = {
        'donors': donor_list,
        'blood_groups': BloodStock.BLOOD_GROUPS,
        'filters': {'blood_group': blood_group, 'availability': availability}
    }
    return render(request, 'bloodbank_app/admin_donors.html', context)


@login_required
@admin_required
def admin_donor_detail(request, pk):
    """View donor details."""
    donor = get_object_or_404(Donor, pk=pk)
    donations = BloodStock.objects.filter(donor=donor).order_by('-collection_date')
    context = {
        'donor': donor,
        'donations': donations,
    }
    return render(request, 'bloodbank_app/admin_donor_detail.html', context)


@login_required
@admin_required
def admin_patients(request):
    """Manage patients list."""
    patients = Patient.objects.select_related('user').all().order_by('-created_at')

    # Filters
    blood_group = request.GET.get('blood_group', '')
    if blood_group:
        patients = patients.filter(blood_group=blood_group)

    paginator = Paginator(patients, 20)
    page = request.GET.get('page')
    patient_list = paginator.get_page(page)

    context = {
        'patients': patient_list,
        'blood_groups': BloodStock.BLOOD_GROUPS,
        'filter': blood_group,
    }
    return render(request, 'bloodbank_app/admin_patients.html', context)


@login_required
@admin_required
def admin_patient_detail(request, pk):
    """View patient details."""
    patient = get_object_or_404(Patient, pk=pk)
    requests = BloodRequest.objects.filter(patient=patient).order_by('-created_at')
    context = {
        'patient': patient,
        'requests': requests,
    }
    return render(request, 'bloodbank_app/admin_patient_detail.html', context)


@login_required
@admin_required
def admin_requests(request):
    """Manage blood requests with approval workflow."""
    status_filter = request.GET.get('status', 'pending')
    requests_qs = BloodRequest.objects.select_related('patient', 'patient__user').all()

    if status_filter:
        requests_qs = requests_qs.filter(status=status_filter)

    requests_qs = requests_qs.order_by('-created_at')
    paginator = Paginator(requests_qs, 20)
    page = request.GET.get('page')
    requests_list = paginator.get_page(page)

    context = {
        'requests': requests_list,
        'status_filter': status_filter,
        'status_choices': BloodRequest.STATUS_CHOICES,
    }
    return render(request, 'bloodbank_app/admin_requests.html', context)


@login_required
@admin_required
def admin_request_approve(request, pk):
    """Approve blood request with atomic allocation."""
    blood_request = get_object_or_404(BloodRequest, pk=pk)

    if blood_request.status != 'pending':
        messages.warning(request, 'This request has already been processed.')
        return redirect('admin_requests')

    if request.method == 'POST':
        form = BloodRequestApprovalForm(request.POST, instance=blood_request)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Lock the request row
                    blood_request = BloodRequest.objects.select_for_update().get(pk=pk)

                    status = form.cleaned_data['status']
                    units_to_allocate = form.cleaned_data.get('units_allocated', 0)

                    if status == 'approved':
                        # Check available stock
                        available_stock = BloodStock.get_available_stock(
                            blood_group=blood_request.blood_group,
                            component=blood_request.component
                        )
                        total_available = sum(s.units for s in available_stock)

                        if total_available < units_to_allocate:
                            raise ValueError(f"Insufficient stock. Available: {total_available}, Requested: {units_to_allocate}")

                        # Allocate from stock (FIFO - oldest first)
                        units_needed = units_to_allocate
                        for stock in available_stock.order_by('collection_date'):
                            if units_needed <= 0:
                                break

                            units_from_this = min(stock.units, units_needed)

                            # Update stock
                            stock.units -= units_from_this
                            if stock.units == 0:
                                stock.is_available = False
                            stock.save()

                            # Create allocation log
                            AllocationLog.objects.create(
                                blood_request=blood_request,
                                blood_stock=stock,
                                units_allocated=units_from_this,
                                allocated_by=request.user,
                                notes=f"Allocated from stock {stock.id}"
                            )

                            units_needed -= units_from_this

                        # Update request
                        blood_request.units_allocated = units_to_allocate
                        blood_request.allocated_by = request.user
                        blood_request.allocated_at = timezone.now()
                        blood_request.status = 'fulfilled' if units_to_allocate >= blood_request.units_required else 'approved'
                        blood_request.save()

                        messages.success(request, f'Request approved! {units_to_allocate} units allocated.')

                    elif status == 'rejected':
                        blood_request.status = 'rejected'
                        blood_request.rejection_reason = form.cleaned_data.get('rejection_reason', '')
                        blood_request.save()
                        messages.success(request, 'Request rejected.')

            except ValueError as e:
                messages.error(request, str(e))
                return redirect('admin_request_approve', pk=pk)
            except Exception as e:
                messages.error(request, f'Error processing request: {str(e)}')
                return redirect('admin_request_approve', pk=pk)

            return redirect('admin_requests')
    else:
        form = BloodRequestApprovalForm(instance=blood_request)
        # Calculate available stock
        available_stock = BloodStock.get_total_units(blood_group=blood_request.blood_group)

    context = {
        'form': form,
        'request_obj': blood_request,
        'available_stock': available_stock,
    }
    return render(request, 'bloodbank_app/admin_request_approve.html', context)


@login_required
@admin_required
def admin_emergency_posts(request):
    """Manage emergency posts."""
    posts = EmergencyPost.objects.select_related('posted_by').all().order_by('-created_at')

    status_filter = request.GET.get('status', 'active')
    if status_filter == 'active':
        posts = posts.filter(is_active=True, fulfilled=False)
    elif status_filter == 'fulfilled':
        posts = posts.filter(fulfilled=True)
    elif status_filter == 'expired':
        posts = posts.filter(deadline__lt=timezone.now(), is_active=True)

    paginator = Paginator(posts, 20)
    page = request.GET.get('page')
    posts_list = paginator.get_page(page)

    context = {
        'posts': posts_list,
        'status_filter': status_filter,
    }
    return render(request, 'bloodbank_app/admin_emergency_posts.html', context)


@login_required
@admin_required
def admin_allocation_logs(request):
    """View allocation logs."""
    logs = AllocationLog.objects.select_related(
        'blood_request', 'blood_request__patient', 
        'blood_stock', 'allocated_by'
    ).order_by('-allocated_at')

    # Date range filter
    form = DateRangeFilterForm(request.GET)
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        blood_group = form.cleaned_data.get('blood_group')

        if start_date:
            logs = logs.filter(allocated_at__date__gte=start_date)
        if end_date:
            logs = logs.filter(allocated_at__date__lte=end_date)
        if blood_group:
            logs = logs.filter(blood_stock__blood_group=blood_group)

    paginator = Paginator(logs, 30)
    page = request.GET.get('page')
    logs_list = paginator.get_page(page)

    context = {
        'logs': logs_list,
        'filter_form': form,
    }
    return render(request, 'bloodbank_app/admin_allocation_logs.html', context)


@login_required
@admin_required
def admin_create_user(request):
    """Admin create new user."""
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully!')
            return redirect('admin_dashboard')
    else:
        form = AdminUserCreationForm()

    return render(request, 'bloodbank_app/admin_create_user.html', {'form': form})


# ==================== DONOR VIEWS ====================

@login_required
@donor_required
def donor_dashboard(request):
    """Donor dashboard."""
    donor = request.user.donor_profile

    # Statistics
    stats = {
        'total_donations': donor.total_donations,
        'last_donation': donor.last_donation_date,
        'next_eligible': donor.next_eligible_date,
        'can_donate': donor.can_donate,
        'emergency_responses': DonorResponse.objects.filter(donor=donor).count(),
    }

    # Recent donations
    recent_donations = BloodStock.objects.filter(donor=donor).order_by('-collection_date')[:5]

    # Available emergency posts matching donor's blood group
    matching_emergency = EmergencyPost.objects.filter(
        blood_group=donor.blood_group,
        is_active=True,
        fulfilled=False,
        deadline__gt=timezone.now()
    ).exclude(
        responses__donor=donor
    ).order_by('-created_at')[:5]

    context = {
        'donor': donor,
        'stats': stats,
        'recent_donations': recent_donations,
        'matching_emergency': matching_emergency,
    }
    return render(request, 'bloodbank_app/donor_dashboard.html', context)


@login_required
@donor_required
def donor_profile(request):
    """Donor profile management."""
    donor = request.user.donor_profile

    if request.method == 'POST':
        form = DonorProfileForm(request.POST, instance=donor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('donor_profile')
    else:
        form = DonorProfileForm(instance=donor)

    context = {
        'form': form,
        'donor': donor,
    }
    return render(request, 'bloodbank_app/donor_profile.html', context)


@login_required
@donor_required
def donor_availability(request):
    """Toggle donor availability."""
    donor = request.user.donor_profile
    donor.is_available = not donor.is_available
    donor.save()

    status = "available" if donor.is_available else "unavailable"
    messages.success(request, f'You are now marked as {status} for donations.')
    return redirect('donor_dashboard')


@login_required
@donor_required
def donor_emergency_list(request):
    """List emergency posts for donors."""
    donor = request.user.donor_profile

    # All active emergency posts
    posts = EmergencyPost.objects.filter(
        is_active=True,
        fulfilled=False,
        deadline__gt=timezone.now()
    ).order_by('-created_at')

    # Check which ones this donor has responded to
    responded_ids = DonorResponse.objects.filter(
        donor=donor
    ).values_list('emergency_post_id', flat=True)

    context = {
        'posts': posts,
        'responded_ids': list(responded_ids),
        'donor_blood_group': donor.blood_group,
    }
    return render(request, 'bloodbank_app/donor_emergency_list.html', context)


@login_required
@donor_required
def donor_respond_emergency(request, post_id):
    """Respond to emergency post."""
    donor = request.user.donor_profile
    emergency_post = get_object_or_404(EmergencyPost, pk=post_id, is_active=True)

    # Check if already responded
    if DonorResponse.objects.filter(donor=donor, emergency_post=emergency_post).exists():
        messages.warning(request, 'You have already responded to this emergency post.')
        return redirect('donor_emergency_list')

    if request.method == 'POST':
        form = DonorResponseForm(request.POST)
        if form.is_valid():
            DonorResponse.objects.create(
                emergency_post=emergency_post,
                donor=donor,
                message=form.cleaned_data.get('message', ''),
                status='pending'
            )
            messages.success(request, 'Your response has been sent! The patient will be notified.')
            return redirect('donor_emergency_list')
    else:
        form = DonorResponseForm()

    context = {
        'form': form,
        'emergency_post': emergency_post,
    }
    return render(request, 'bloodbank_app/donor_respond_emergency.html', context)


@login_required
@donor_required
def donor_history(request):
    """View donation history."""
    donor = request.user.donor_profile
    donations = BloodStock.objects.filter(donor=donor).order_by('-collection_date')

    paginator = Paginator(donations, 20)
    page = request.GET.get('page')
    donations_list = paginator.get_page(page)

    context = {
        'donations': donations_list,
        'donor': donor,
    }
    return render(request, 'bloodbank_app/donor_history.html', context)


# ==================== PATIENT VIEWS ====================

@login_required
@patient_required
def patient_dashboard(request):
    """Patient dashboard."""
    patient = request.user.patient_profile

    # Statistics
    stats = {
        'total_requests': BloodRequest.objects.filter(patient=patient).count(),
        'pending_requests': BloodRequest.objects.filter(patient=patient, status='pending').count(),
        'approved_requests': BloodRequest.objects.filter(patient=patient, status__in=['approved', 'fulfilled']).count(),
        'emergency_posts': EmergencyPost.objects.filter(posted_by=request.user).count(),
    }

    # Recent requests
    recent_requests = BloodRequest.objects.filter(patient=patient).order_by('-created_at')[:5]

    # Active emergency posts by this patient
    my_emergency = EmergencyPost.objects.filter(
        posted_by=request.user,
        is_active=True
    ).order_by('-created_at')[:5]

    context = {
        'patient': patient,
        'stats': stats,
        'recent_requests': recent_requests,
        'my_emergency': my_emergency,
    }
    return render(request, 'bloodbank_app/patient_dashboard.html', context)


@login_required
@patient_required
def patient_profile(request):
    """Patient profile management."""
    patient = request.user.patient_profile

    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('patient_profile')
    else:
        form = PatientProfileForm(instance=patient)

    context = {
        'form': form,
        'patient': patient,
    }
    return render(request, 'bloodbank_app/patient_profile.html', context)


@login_required
@patient_required
def patient_search(request):
    """Search for blood availability and matching donors."""
    blood_group = request.GET.get('blood_group', '')
    results = None

    if blood_group:
        # Get stock availability
        stock_available = BloodStock.get_total_units(blood_group=blood_group)

        # Get matching donors
        matching_donors = Donor.objects.filter(
            blood_group=blood_group,
            is_available=True
        ).select_related('user')

        # Get recent emergency posts for this blood group
        emergency_posts = EmergencyPost.objects.filter(
            blood_group=blood_group,
            is_active=True,
            fulfilled=False
        ).order_by('-created_at')[:5]

        results = {
            'blood_group': blood_group,
            'stock_available': stock_available,
            'matching_donors': matching_donors,
            'emergency_posts': emergency_posts,
        }

    context = {
        'blood_groups': BloodStock.BLOOD_GROUPS,
        'selected_group': blood_group,
        'results': results,
    }
    return render(request, 'bloodbank_app/patient_search.html', context)


@login_required
@patient_required
def patient_request_blood(request):
    """Create blood request."""
    patient = request.user.patient_profile

    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.patient = patient
            blood_request.save()
            messages.success(request, f'Blood request submitted successfully! Request ID: {blood_request.request_id}')
            return redirect('patient_requests')
    else:
        # Pre-fill with patient data
        initial = {
            'blood_group': patient.blood_group,
            'hospital_name': patient.hospital_name,
            'hospital_address': patient.hospital_address,
            'doctor_name': patient.doctor_name,
        }
        form = BloodRequestForm(initial=initial)

    context = {
        'form': form,
        'patient': patient,
    }
    return render(request, 'bloodbank_app/patient_request_blood.html', context)


@login_required
@patient_required
def patient_requests(request):
    """View blood request history."""
    patient = request.user.patient_profile
    requests_list = BloodRequest.objects.filter(patient=patient).order_by('-created_at')

    paginator = Paginator(requests_list, 15)
    page = request.GET.get('page')
    requests_qs = paginator.get_page(page)

    context = {
        'requests': requests_qs,
    }
    return render(request, 'bloodbank_app/patient_requests.html', context)


@login_required
@patient_required
def patient_request_detail(request, pk):
    """View blood request details."""
    patient = request.user.patient_profile
    blood_request = get_object_or_404(BloodRequest, pk=pk, patient=patient)
    allocation_logs = AllocationLog.objects.filter(blood_request=blood_request)

    context = {
        'request_obj': blood_request,
        'allocation_logs': allocation_logs,
    }
    return render(request, 'bloodbank_app/patient_request_detail.html', context)


@login_required
@patient_required
def patient_emergency_create(request):
    """Create emergency blood request post."""
    if request.method == 'POST':
        form = EmergencyPostForm(request.POST)
        if form.is_valid():
            emergency_post = form.save(commit=False)
            emergency_post.posted_by = request.user
            emergency_post.save()
            messages.success(request, f'Emergency post created! Post ID: {emergency_post.post_id}')
            return redirect('patient_emergency_list')
    else:
        # Pre-fill patient data
        patient = request.user.patient_profile
        initial = {
            'patient_name': request.user.get_full_name(),
            'blood_group': patient.blood_group,
            'hospital_name': patient.hospital_name,
            'hospital_address': patient.hospital_address,
            'contact_phone': request.user.phone_number,
            'contact_email': request.user.email,
        }
        form = EmergencyPostForm(initial=initial)

    return render(request, 'bloodbank_app/patient_emergency_create.html', {'form': form})


@login_required
@patient_required
def patient_emergency_list(request):
    """List patient's emergency posts."""
    posts = EmergencyPost.objects.filter(posted_by=request.user).order_by('-created_at')

    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts_list = paginator.get_page(page)

    context = {
        'posts': posts_list,
    }
    return render(request, 'bloodbank_app/patient_emergency_list.html', context)


@login_required
@patient_required
def patient_emergency_detail(request, pk):
    """View emergency post details with donor responses."""
    post = get_object_or_404(EmergencyPost, pk=pk, posted_by=request.user)
    responses = DonorResponse.objects.filter(emergency_post=post).select_related('donor', 'donor__user')

    context = {
        'post': post,
        'responses': responses,
    }
    return render(request, 'bloodbank_app/patient_emergency_detail.html', context)


@login_required
@patient_required
def patient_emergency_close(request, pk):
    """Close emergency post."""
    post = get_object_or_404(EmergencyPost, pk=pk, posted_by=request.user)
    post.is_active = False
    post.fulfilled = True
    post.save()
    messages.success(request, 'Emergency post closed successfully.')
    return redirect('patient_emergency_list')


# ==================== API/AJAX VIEWS ====================

@login_required
def check_blood_availability(request):
    """AJAX endpoint to check blood availability."""
    blood_group = request.GET.get('blood_group')
    if blood_group:
        units = BloodStock.get_total_units(blood_group=blood_group)
        donors = Donor.objects.filter(blood_group=blood_group, is_available=True).count()
        return JsonResponse({
            'available': units > 0,
            'units': units,
            'donors': donors,
        })
    return JsonResponse({'error': 'Blood group required'}, status=400)


@login_required
def get_donor_details(request, donor_id):
    """AJAX endpoint to get donor details for emergency response."""
    try:
        donor = Donor.objects.select_related('user').get(pk=donor_id)
        return JsonResponse({
            'name': donor.user.get_full_name(),
            'blood_group': donor.blood_group,
            'phone': donor.user.phone_number,
            'email': donor.user.email,
            'available': donor.is_available,
        })
    except Donor.DoesNotExist:
        return JsonResponse({'error': 'Donor not found'}, status=404)
