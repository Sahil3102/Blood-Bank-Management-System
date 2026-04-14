# Cloud-Based Blood Bank Management System

A comprehensive, cloud-ready Django web application for managing blood donation, inventory, and distribution. Built for academic Cloud Computing Lab projects with support for Google App Engine and Railway deployment.

![Blood Bank System](https://img.shields.io/badge/Django-4.2-green.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple.svg)

## 🚀 Features

### Core Functionality
- **Blood Stock Management**: Track inventory by blood group (A+, A-, B+, B-, O+, O-, AB+, AB-) with automatic expiry tracking
- **Donor Management**: Complete donor profiles with availability tracking, donation history, and eligibility checks
- **Patient Management**: Patient registration with medical history and blood request tracking
- **Blood Request System**: Request workflow with approval/rejection and automatic allocation
- **Emergency Response**: Urgent blood request posting with real-time donor notifications
- **Admin Dashboard**: Comprehensive statistics and management interface

### User Roles
- **Administrator**: Full system control, user management, stock management, request approval
- **Blood Donor**: Profile management, availability toggle, emergency response, donation history
- **Patient**: Blood search, request submission, emergency posting, request tracking

### Technical Features
- Role-based authentication with custom user model
- Transaction-safe blood allocation using `transaction.atomic()`
- Automatic blood expiry checking and status updates
- Real-time statistics on landing page
- Responsive Bootstrap 5 UI with red medical theme
- Toast notifications using Django messages framework
- Post/Redirect/Get pattern implementation
- Cloud-ready configuration (Google App Engine, Railway)

## 📋 Prerequisites

- Python 3.11 or higher
- pip package manager
- Virtual environment (recommended)
- PostgreSQL (optional, for production)

## 🛠️ Installation

### 1. Clone or Download the Project

```bash
cd bloodbank_project
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
cp .env.example .env
# Edit .env file with your configuration
```

### 5. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Seed Initial Data

```bash
python manage.py seed_data
```

This creates:
- Admin user (username: `admin`, password: `admin123`)
- 20 sample donors
- 15 sample patients
- Blood stock entries
- Sample requests and emergency posts

### 7. Run Development Server

```bash
python manage.py runserver
```

Access the application at: http://127.0.0.1:8000/

## 🔑 Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Donor | donor1 | donor123 |
| Patient | patient1 | patient123 |

## 📁 Project Structure

```
bloodbank_project/
├── bloodbank/                  # Project configuration
│   ├── __init__.py
│   ├── settings.py            # Django settings (SQLite/PostgreSQL ready)
│   ├── urls.py                # Main URL configuration
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
├── bloodbank_app/             # Main application
│   ├── models.py              # Database models
│   ├── views.py               # All views (public, admin, donor, patient)
│   ├── forms.py               # All forms
│   ├── urls.py                # App URL configuration
│   ├── admin.py               # Admin configurations
│   ├── decorators.py          # Role-based access decorators
│   ├── templates/             # All HTML templates
│   │   └── bloodbank_app/
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── login.html
│   │       ├── donor_*.html
│   │       ├── patient_*.html
│   │       └── admin_*.html
│   └── management/
│       └── commands/
│           └── seed_data.py   # Data seeding command
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── Procfile                   # Railway/Heroku deployment
├── app.yaml                   # Google App Engine configuration
└── .env.example               # Environment variables template
```

## 🗄️ Database Models

### CustomUser
- Extended Django user with role-based fields
- Roles: admin, donor, patient
- Contact information and address

### Donor
- Blood group, date of birth, gender
- Weight, availability status
- Donation history tracking
- Medical conditions
- Emergency contact

### Patient
- Blood group, medical condition
- Hospital and doctor information
- Linked to user account

### BloodStock
- Blood group and component type
- Units, collection and expiry dates
- Donor reference
- Expiry status checking

### BloodRequest
- Auto-generated ID (BB-XXXX format)
- Patient, blood group, units required
- Priority levels (low, normal, high, critical)
- Status tracking (pending, approved, rejected, fulfilled)
- Allocation tracking

### AllocationLog
- Auto-generated ID (AL-XXXX format)
- Links request to stock
- Tracks allocation details

### EmergencyPost
- Auto-generated ID (EM-XXXX format)
- Urgency levels (urgent, critical, emergency)
- Real-time countdown
- Donor response tracking

### DonorResponse
- Links donors to emergency posts
- Message and status tracking

## 🎨 UI Features

- **Bootstrap 5** responsive design
- **Red medical theme** throughout
- **Sidebar navigation** for dashboard views
- **Status badges** for quick identification
- **Toast notifications** for user feedback
- **Data tables** with pagination
- **Card-based layouts** for statistics
- **Mobile-responsive** design

## ☁️ Cloud Deployment

### Google App Engine

1. Install Google Cloud SDK
2. Update `app.yaml` with your configuration
3. Deploy:
```bash
gcloud app deploy
```

### Railway

1. Connect your GitHub repository to Railway
2. Add PostgreSQL database
3. Set environment variables
4. Deploy automatically

### Environment Variables

```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://...  # Optional
```

## 🔒 Security Features

- CSRF protection enabled
- Secure password hashing
- Role-based access control
- Transaction-safe operations
- SQL injection prevention (Django ORM)
- XSS protection

## 🧪 Testing

Run tests with:
```bash
python manage.py test
```

## 📝 API Endpoints

- `GET /api/check-availability/?blood_group=A+` - Check blood availability
- `GET /api/donor/<id>/` - Get donor details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is for academic purposes. Feel free to use and modify for your Cloud Computing Lab project.

## 🙏 Acknowledgments

- Django Framework
- Bootstrap 5
- Bootstrap Icons
- Google Fonts (Poppins)

## 📧 Support

For issues or questions, please contact your lab instructor or create an issue in the repository.

---

**Made with ❤️ for Cloud Computing Lab** | Django 4.2 | Python 3.11 | Bootstrap 5
