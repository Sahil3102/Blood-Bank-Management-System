import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodbank.settings')
django.setup()

from bloodbank_app.forms import DonorRegistrationForm

data = {
    'username': 'test1',
    'first_name': 'test',
    'last_name': 'test',
    'email': 't@t.com',
    'phone_number': '+1234567890',
    'address': '1',
    'city': '1',
    'state': '1',
    'zip_code': '1',
    'password1': 'TestPassword123!',
    'password2': 'TestPassword123!',
    'blood_group': 'A+',
    'date_of_birth': '2000-01-01',
    'gender': 'M',
    'weight_kg': '60',
    'emergency_contact_name': 'test',
    'emergency_contact_phone': '+1234567890'
}

form = DonorRegistrationForm(data)
print("Is valid:", form.is_valid())
if not form.is_valid():
    print("Errors:", form.errors)
else:
    try:
        user = form.save()
        print("User saved successfully:", user.username)
    except Exception as e:
        print("Error saving:", str(e))
