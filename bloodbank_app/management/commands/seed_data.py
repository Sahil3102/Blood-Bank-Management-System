"""
Management command to seed initial data for the Blood Bank Management System.
Usage: python manage.py seed_data
"""
import random
from datetime import date, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from bloodbank_app.models import (
    Donor, Patient, BloodStock, BloodRequest, 
    EmergencyPost, AllocationLog, DonorResponse
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with initial data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))

        with transaction.atomic():
            self.create_admin_user()
            self.create_donors()
            self.create_patients()
            self.create_blood_stock()
            self.create_blood_requests()
            self.create_emergency_posts()

        self.stdout.write(self.style.SUCCESS('Data seeding completed successfully!'))

    def create_admin_user(self):
        """Create admin user."""
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@bloodbank.org',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                role='admin',
                phone_number='+1234567890',
                address='123 Admin Street',
                city='New York',
                state='NY',
                zip_code='10001'
            )
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin.username}'))
        else:
            self.stdout.write('Admin user already exists')

    def create_donors(self):
        """Create sample donors."""
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
        genders = ['M', 'F', 'O']
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 'William', 'Emma']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
        states = ['NY', 'CA', 'IL', 'TX', 'AZ']

        for i in range(20):
            username = f'donor{i+1}'
            if User.objects.filter(username=username).exists():
                continue

            user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='donor123',
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                role='donor',
                phone_number=f'+1{random.randint(1000000000, 9999999999)}',
                address=f'{random.randint(100, 9999)} Main Street',
                city=random.choice(cities),
                state=random.choice(states),
                zip_code=f'{random.randint(10000, 99999)}'
            )

            donor = Donor.objects.create(
                user=user,
                blood_group=random.choice(blood_groups),
                date_of_birth=date(random.randint(1960, 2000), random.randint(1, 12), random.randint(1, 28)),
                gender=random.choice(genders),
                weight_kg=random.uniform(50, 90),
                is_available=random.choice([True, True, True, False]),  # 75% available
                last_donation_date=date.today() - timedelta(days=random.randint(60, 365)) if random.choice([True, False]) else None,
                total_donations=random.randint(0, 10),
                medical_conditions='None' if random.choice([True, True, False]) else 'Mild hypertension',
                emergency_contact_name=random.choice(first_names) + ' ' + random.choice(last_names),
                emergency_contact_phone=f'+1{random.randint(1000000000, 9999999999)}'
            )

        self.stdout.write(self.style.SUCCESS('Created 20 sample donors'))

    def create_patients(self):
        """Create sample patients."""
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
        genders = ['M', 'F', 'O']
        first_names = ['Alice', 'Bob', 'Carol', 'Daniel', 'Eva', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack']
        last_names = ['Anderson', 'Baker', 'Clark', 'Davis', 'Evans', 'Foster', 'Gray', 'Hill', 'Irwin', 'Jones']
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
        states = ['NY', 'CA', 'IL', 'TX', 'AZ']
        hospitals = ['City General Hospital', 'Memorial Medical Center', 'St. Mary's Hospital', 'University Hospital', 'Community Health Center']

        for i in range(15):
            username = f'patient{i+1}'
            if User.objects.filter(username=username).exists():
                continue

            user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='patient123',
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                role='patient',
                phone_number=f'+1{random.randint(1000000000, 9999999999)}',
                address=f'{random.randint(100, 9999)} Oak Street',
                city=random.choice(cities),
                state=random.choice(states),
                zip_code=f'{random.randint(10000, 99999)}'
            )

            hospital = random.choice(hospitals)
            Patient.objects.create(
                user=user,
                blood_group=random.choice(blood_groups),
                date_of_birth=date(random.randint(1940, 1990), random.randint(1, 12), random.randint(1, 28)),
                gender=random.choice(genders),
                hospital_name=hospital,
                hospital_address=f'{random.randint(100, 9999)} Medical Drive, {user.city}, {user.state}',
                doctor_name=f'Dr. {random.choice(last_names)}',
                medical_condition=random.choice([
                    'Surgery scheduled - hip replacement',
                    'Anemia treatment',
                    'Cancer chemotherapy',
                    'Accident trauma recovery',
                    'Childbirth complications',
                    'Blood disorder treatment'
                ])
            )

        self.stdout.write(self.style.SUCCESS('Created 15 sample patients'))

    def create_blood_stock(self):
        """Create blood stock entries."""
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
        components = ['whole', 'plasma', 'platelets', 'rbc']
        donors = list(Donor.objects.all())

        for blood_group in blood_groups:
            # Create 3-5 stock entries per blood group
            for _ in range(random.randint(3, 5)):
                collection_date = date.today() - timedelta(days=random.randint(0, 30))
                donor = random.choice(donors) if donors and random.choice([True, False]) else None

                BloodStock.objects.create(
                    blood_group=blood_group,
                    component=random.choice(components),
                    units=random.randint(1, 5),
                    collection_date=collection_date,
                    donor=donor,
                    storage_location=f'Unit {random.randint(1, 5)} - Shelf {random.randint(1, 10)}',
                    notes='Sample data entry',
                    is_available=True
                )

        self.stdout.write(self.style.SUCCESS('Created blood stock entries'))

    def create_blood_requests(self):
        """Create sample blood requests."""
        patients = list(Patient.objects.all())
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
        priorities = ['low', 'normal', 'high', 'critical']
        statuses = ['pending', 'approved', 'rejected', 'fulfilled']

        for i in range(25):
            patient = random.choice(patients)
            status = random.choice(statuses)

            request = BloodRequest.objects.create(
                patient=patient,
                blood_group=random.choice(blood_groups),
                units_required=random.randint(1, 4),
                component=random.choice(['whole', 'plasma', 'platelets', 'rbc']),
                hospital_name=patient.hospital_name,
                hospital_address=patient.hospital_address,
                doctor_name=patient.doctor_name,
                required_date=date.today() + timedelta(days=random.randint(1, 14)),
                reason=random.choice([
                    'Scheduled surgery',
                    'Emergency transfusion needed',
                    'Ongoing treatment',
                    'Post-operative care'
                ]),
                priority=random.choice(priorities),
                status=status,
                units_allocated=random.randint(1, 2) if status in ['approved', 'fulfilled'] else 0
            )

        self.stdout.write(self.style.SUCCESS('Created 25 sample blood requests'))

    def create_emergency_posts(self):
        """Create sample emergency posts."""
        users = list(User.objects.filter(role='patient'))
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
        urgency_levels = ['urgent', 'critical', 'emergency']

        for i in range(8):
            user = random.choice(users) if users else User.objects.filter(role='admin').first()

            EmergencyPost.objects.create(
                posted_by=user,
                patient_name=f'Patient {i+1}',
                blood_group=random.choice(blood_groups),
                units_needed=random.randint(1, 5),
                urgency_level=random.choice(urgency_levels),
                hospital_name=random.choice(['City General', 'Memorial Hospital', 'St. Mary's']),
                hospital_address='123 Emergency Lane, New York, NY',
                contact_phone=f'+1{random.randint(1000000000, 9999999999)}',
                contact_email=f'emergency{i+1}@example.com',
                medical_notes='Urgent blood needed for surgery',
                deadline=timezone.now() + timedelta(hours=random.randint(6, 48)),
                is_active=random.choice([True, True, True, False]),
                fulfilled=False
            )

        self.stdout.write(self.style.SUCCESS('Created 8 sample emergency posts'))
