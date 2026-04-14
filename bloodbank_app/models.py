"""
Models for Blood Bank Management System.
"""
import uuid
from datetime import date, timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone


class CustomUser(AbstractUser):
    """Custom User model with role-based access."""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('donor', 'Blood Donor'),
        ('patient', 'Patient'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    phone_regex = RegexValidator(
        regex=r'^(\+?1?\d{9,15})$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_donor(self):
        return self.role == 'donor'

    @property
    def is_patient_user(self):
        return self.role == 'patient'


class Donor(models.Model):
    """Donor profile with blood donation details."""
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='donor_profile')
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(45)])
    is_available = models.BooleanField(default=True)
    last_donation_date = models.DateField(null=True, blank=True)
    total_donations = models.PositiveIntegerField(default=0)
    medical_conditions = models.TextField(blank=True, null=True, help_text="Any medical conditions or medications")
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=17, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Donor: {self.user.get_full_name()} ({self.blood_group})"

    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    @property
    def can_donate(self):
        """Check if donor is eligible to donate based on last donation date."""
        if not self.last_donation_date:
            return True
        min_interval = timedelta(days=56)  # 8 weeks minimum for whole blood
        return (date.today() - self.last_donation_date) >= min_interval

    @property
    def next_eligible_date(self):
        """Calculate next eligible donation date."""
        if not self.last_donation_date:
            return date.today()
        return self.last_donation_date + timedelta(days=56)

    def update_donation_count(self):
        """Increment total donations counter."""
        self.total_donations += 1
        self.last_donation_date = date.today()
        self.save()


class Patient(models.Model):
    """Patient profile for blood recipients."""
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    hospital_name = models.CharField(max_length=200, blank=True, null=True)
    hospital_address = models.TextField(blank=True, null=True)
    doctor_name = models.CharField(max_length=100, blank=True, null=True)
    medical_condition = models.TextField(blank=True, null=True, help_text="Reason for blood requirement")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Patient: {self.user.get_full_name()} ({self.blood_group})"

    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class BloodStock(models.Model):
    """Blood inventory management with expiry tracking."""
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')
    ]

    COMPONENTS = [
        ('whole', 'Whole Blood'),
        ('plasma', 'Plasma'),
        ('platelets', 'Platelets'),
        ('rbc', 'Red Blood Cells'),
    ]

    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    component = models.CharField(max_length=10, choices=COMPONENTS, default='whole')
    units = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    collection_date = models.DateField(default=date.today)
    expiry_date = models.DateField()
    donor = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    storage_location = models.CharField(max_length=100, blank=True, null=True, help_text="Storage unit/location")
    notes = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Blood Stock'
        verbose_name_plural = 'Blood Stock'
        ordering = ['blood_group', 'component', 'expiry_date']
        unique_together = ['blood_group', 'component', 'collection_date', 'donor']

    def __str__(self):
        return f"{self.blood_group} {self.get_component_display()} - {self.units} units (Expires: {self.expiry_date})"

    @property
    def is_expired(self):
        """Check if blood unit has expired."""
        return date.today() > self.expiry_date

    @property
    def days_until_expiry(self):
        """Calculate days until expiry."""
        delta = self.expiry_date - date.today()
        return delta.days

    @property
    def status(self):
        """Get status based on expiry."""
        if self.is_expired:
            return 'expired'
        elif self.days_until_expiry <= 3:
            return 'critical'
        elif self.days_until_expiry <= 7:
            return 'warning'
        return 'good'

    def save(self, *args, **kwargs):
        """Auto-calculate expiry date based on component type."""
        if not self.expiry_date:
            if self.component == 'whole':
                self.expiry_date = self.collection_date + timedelta(days=42)
            elif self.component == 'plasma':
                self.expiry_date = self.collection_date + timedelta(days=365)
            elif self.component == 'platelets':
                self.expiry_date = self.collection_date + timedelta(days=5)
            elif self.component == 'rbc':
                self.expiry_date = self.collection_date + timedelta(days=42)
        super().save(*args, **kwargs)

    @classmethod
    def get_available_stock(cls, blood_group=None, component='whole'):
        """Get available non-expired stock."""
        queryset = cls.objects.filter(
            is_available=True,
            expiry_date__gte=date.today(),
            units__gt=0
        )
        if blood_group:
            queryset = queryset.filter(blood_group=blood_group)
        if component:
            queryset = queryset.filter(component=component)
        return queryset

    @classmethod
    def get_total_units(cls, blood_group=None):
        """Get total available units."""
        stock = cls.get_available_stock(blood_group)
        return sum(item.units for item in stock)


class BloodRequest(models.Model):
    """Blood request from patients with auto-generated ID."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')
    ]

    request_id = models.CharField(max_length=10, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='blood_requests')
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    units_required = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    component = models.CharField(max_length=10, choices=BloodStock.COMPONENTS, default='whole')
    hospital_name = models.CharField(max_length=200)
    hospital_address = models.TextField()
    doctor_name = models.CharField(max_length=100)
    required_date = models.DateField()
    reason = models.TextField(help_text="Medical reason for blood requirement")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # Allocation details
    units_allocated = models.PositiveIntegerField(default=0)
    allocated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='allocated_requests')
    allocated_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Request {self.request_id} - {self.patient.user.get_full_name()} ({self.blood_group})"

    def save(self, *args, **kwargs):
        if not self.request_id:
            self.request_id = self.generate_request_id()
        super().save(*args, **kwargs)

    def generate_request_id(self):
        """Generate unique request ID in format BB-XXXX."""
        while True:
            code = f"BB-{uuid.uuid4().hex[:4].upper()}"
            if not BloodRequest.objects.filter(request_id=code).exists():
                return code

    @property
    def is_urgent(self):
        return self.priority in ['high', 'critical'] or (self.required_date - date.today()).days <= 1

    @property
    def fulfillment_percentage(self):
        if self.units_required == 0:
            return 0
        return (self.units_allocated / self.units_required) * 100


class AllocationLog(models.Model):
    """Log of blood allocations with auto-generated ID."""
    log_id = models.CharField(max_length=10, unique=True, editable=False)
    blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='allocation_logs')
    blood_stock = models.ForeignKey(BloodStock, on_delete=models.CASCADE, related_name='allocations')
    units_allocated = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    allocated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='allocation_logs')
    allocated_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-allocated_at']

    def __str__(self):
        return f"Allocation {self.log_id} - {self.blood_request.request_id}"

    def save(self, *args, **kwargs):
        if not self.log_id:
            self.log_id = self.generate_log_id()
        super().save(*args, **kwargs)

    def generate_log_id(self):
        """Generate unique log ID in format AL-XXXX."""
        while True:
            code = f"AL-{uuid.uuid4().hex[:4].upper()}"
            if not AllocationLog.objects.filter(log_id=code).exists():
                return code


class EmergencyPost(models.Model):
    """Emergency blood request posts for urgent requirements."""
    URGENCY_CHOICES = [
        ('urgent', 'Urgent - Within 24 hours'),
        ('critical', 'Critical - Within 6 hours'),
        ('emergency', 'Emergency - Immediate'),
    ]

    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')
    ]

    post_id = models.CharField(max_length=10, unique=True, editable=False)
    posted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='emergency_posts')
    patient_name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    units_needed = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    urgency_level = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='urgent')
    hospital_name = models.CharField(max_length=200)
    hospital_address = models.TextField()
    contact_phone = models.CharField(max_length=17)
    contact_email = models.EmailField(blank=True, null=True)
    medical_notes = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    fulfilled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Emergency {self.post_id} - {self.patient_name} ({self.blood_group})"

    def save(self, *args, **kwargs):
        if not self.post_id:
            self.post_id = self.generate_post_id()
        super().save(*args, **kwargs)

    def generate_post_id(self):
        """Generate unique post ID in format EM-XXXX."""
        while True:
            code = f"EM-{uuid.uuid4().hex[:4].upper()}"
            if not EmergencyPost.objects.filter(post_id=code).exists():
                return code

    @property
    def is_expired(self):
        return timezone.now() > self.deadline

    @property
    def time_remaining(self):
        if self.is_expired:
            return "Expired"
        delta = self.deadline - timezone.now()
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f"{delta.days}d {hours}h {minutes}m"

    @property
    def response_count(self):
        return self.responses.filter(status='accepted').count()


class DonorResponse(models.Model):
    """Donor responses to emergency posts."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    emergency_post = models.ForeignKey(EmergencyPost, on_delete=models.CASCADE, related_name='responses')
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='emergency_responses')
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    responded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['emergency_post', 'donor']
        ordering = ['-responded_at']

    def __str__(self):
        return f"Response by {self.donor.user.get_full_name()} to {self.emergency_post.post_id}"
