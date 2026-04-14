"""
Forms for Blood Bank Management System.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import date, timedelta
from .models import CustomUser, Donor, Patient, BloodStock, BloodRequest, EmergencyPost


class CustomUserCreationForm(UserCreationForm):
    """Base user registration form."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(
        max_length=17,
        required=True,
        validators=[RegexValidator(regex=r'^(\+?1?\d{9,15})$', message="Enter valid phone number")]
    )
    address = forms.CharField(widget=forms.Textarea, required=True)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    zip_code = forms.CharField(max_length=10, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 
                  'address', 'city', 'state', 'zip_code', 'password1', 'password2')


class DonorRegistrationForm(CustomUserCreationForm):
    """Extended form for donor registration."""
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    blood_group = forms.ChoiceField(choices=BLOOD_GROUPS, required=True)
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True, widget=forms.RadioSelect)
    weight_kg = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=45,
        required=True,
        help_text="Minimum 45 kg required for donation"
    )
    medical_conditions = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="List any medical conditions or medications (optional)"
    )
    emergency_contact_name = forms.CharField(max_length=100, required=True)
    emergency_contact_phone = forms.CharField(
        max_length=17,
        required=True,
        validators=[RegexValidator(regex=r'^(\+?1?\d{9,15})$', message="Enter valid phone number")]
    )

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            age = (date.today() - dob).days // 365
            if age < 18:
                raise forms.ValidationError("Donor must be at least 18 years old.")
            if age > 65:
                raise forms.ValidationError("Donor age must be under 65 years.")
        return dob

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'donor'
        if commit:
            user.save()
            Donor.objects.create(
                user=user,
                blood_group=self.cleaned_data['blood_group'],
                date_of_birth=self.cleaned_data['date_of_birth'],
                gender=self.cleaned_data['gender'],
                weight_kg=self.cleaned_data['weight_kg'],
                medical_conditions=self.cleaned_data.get('medical_conditions', ''),
                emergency_contact_name=self.cleaned_data['emergency_contact_name'],
                emergency_contact_phone=self.cleaned_data['emergency_contact_phone']
            )
        return user


class PatientRegistrationForm(CustomUserCreationForm):
    """Extended form for patient registration."""
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    blood_group = forms.ChoiceField(choices=BLOOD_GROUPS, required=True)
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True, widget=forms.RadioSelect)
    hospital_name = forms.CharField(max_length=200, required=True)
    hospital_address = forms.CharField(widget=forms.Textarea, required=True)
    doctor_name = forms.CharField(max_length=100, required=True)
    medical_condition = forms.CharField(
        widget=forms.Textarea,
        required=True,
        help_text="Describe your medical condition requiring blood"
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        if commit:
            user.save()
            Patient.objects.create(
                user=user,
                blood_group=self.cleaned_data['blood_group'],
                date_of_birth=self.cleaned_data['date_of_birth'],
                gender=self.cleaned_data['gender'],
                hospital_name=self.cleaned_data['hospital_name'],
                hospital_address=self.cleaned_data['hospital_address'],
                doctor_name=self.cleaned_data['doctor_name'],
                medical_condition=self.cleaned_data['medical_condition']
            )
        return user


class LoginForm(AuthenticationForm):
    """Custom login form."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class DonorProfileForm(forms.ModelForm):
    """Form for updating donor profile."""
    class Meta:
        model = Donor
        fields = ['blood_group', 'date_of_birth', 'gender', 'weight_kg', 
                  'is_available', 'medical_conditions', 
                  'emergency_contact_name', 'emergency_contact_phone']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'medical_conditions': forms.Textarea(attrs={'rows': 3}),
        }


class PatientProfileForm(forms.ModelForm):
    """Form for updating patient profile."""
    class Meta:
        model = Patient
        fields = ['blood_group', 'date_of_birth', 'gender', 'hospital_name',
                  'hospital_address', 'doctor_name', 'medical_condition']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'hospital_address': forms.Textarea(attrs={'rows': 3}),
            'medical_condition': forms.Textarea(attrs={'rows': 3}),
        }


class BloodStockForm(forms.ModelForm):
    """Form for adding/updating blood stock."""
    class Meta:
        model = BloodStock
        fields = ['blood_group', 'component', 'units', 'collection_date', 
                  'expiry_date', 'donor', 'storage_location', 'notes']
        widgets = {
            'collection_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available donors in dropdown
        self.fields['donor'].queryset = Donor.objects.filter(is_available=True)
        self.fields['donor'].required = False


class BloodRequestForm(forms.ModelForm):
    """Form for creating blood requests."""
    class Meta:
        model = BloodRequest
        fields = ['blood_group', 'units_required', 'component', 'hospital_name',
                  'hospital_address', 'doctor_name', 'required_date', 'reason', 'priority']
        widgets = {
            'required_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_required_date(self):
        required_date = self.cleaned_data.get('required_date')
        if required_date and required_date < date.today():
            raise forms.ValidationError("Required date cannot be in the past.")
        return required_date


class BloodRequestApprovalForm(forms.ModelForm):
    """Form for admin to approve/reject blood requests."""
    class Meta:
        model = BloodRequest
        fields = ['status', 'units_allocated', 'rejection_reason']
        widgets = {
            'rejection_reason': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        units_allocated = cleaned_data.get('units_allocated')
        rejection_reason = cleaned_data.get('rejection_reason')

        if status == 'rejected' and not rejection_reason:
            raise forms.ValidationError("Please provide a reason for rejection.")

        if status == 'approved' and (not units_allocated or units_allocated <= 0):
            raise forms.ValidationError("Please specify units to allocate when approving.")

        return cleaned_data


class EmergencyPostForm(forms.ModelForm):
    """Form for creating emergency blood requests."""
    class Meta:
        model = EmergencyPost
        fields = ['patient_name', 'blood_group', 'units_needed', 'urgency_level',
                  'hospital_name', 'hospital_address', 'contact_phone', 
                  'contact_email', 'medical_notes', 'deadline']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'hospital_address': forms.Textarea(attrs={'rows': 3}),
            'medical_notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default deadline to 24 hours from now
        self.fields['deadline'].initial = timezone.now() + timedelta(hours=24)

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < timezone.now():
            raise forms.ValidationError("Deadline cannot be in the past.")
        return deadline

    def clean_contact_phone(self):
        phone = self.cleaned_data.get('contact_phone')
        if phone:
            validator = RegexValidator(regex=r'^(\+?1?\d{9,15})$', message="Enter valid phone number")
            validator(phone)
        return phone


class DonorResponseForm(forms.Form):
    """Form for donors to respond to emergency posts."""
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional message to the patient/family'}),
        required=False,
        help_text="You can include your availability or any relevant information"
    )


class AdminUserCreationForm(UserCreationForm):
    """Form for admin to create users."""
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2')


class DateRangeFilterForm(forms.Form):
    """Form for filtering by date range."""
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    blood_group = forms.ChoiceField(
        choices=[('', 'All')] + BloodStock.BLOOD_GROUPS,
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date cannot be after end date.")

        return cleaned_data
