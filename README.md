# Django Event Management System

A comprehensive web application for managing events, user registration, and RSVPs built with Django 5.2. This system provides role-based access control and email notifications for a complete event management experience.

## 🌐 Live Demo

**Live Application**: [https://django-event-management-system-60t0.onrender.com](https://django-event-management-system-60t0.onrender.com)

## ✨ Features

### User Management
- **Custom User Authentication** with email verification
- **Role-based Access Control** (Admin, Organizer, Participant)
- **User Profile Management** with profile pictures, bio, phone numbers
- **Email-based Account Activation**
- **Password Reset Functionality**

### Event Management
- **Create, Read, Update, Delete Events** with rich details
- **Event Categories** for better organization
- **Event Images** with default fallbacks
- **Event Filtering** by category and date range
- **Event Search** functionality

### RSVP System
- **Event Registration/RSVP** with optional notes
- **Automatic Email Notifications** for RSVP confirmations
- **RSVP Management** (register/unregister from events)
- **Email Templates** for various RSVP actions

### Dashboards
- **Organizer Dashboard** with event management tools and statistics
- **Participant Dashboard** showing upcoming and past RSVPs
- **Admin Dashboard** for user and system management

### Additional Features
- **Responsive Design** with Tailwind CSS
- **Media File Management** for event images and user profiles
- **Timezone Support**
- **Email Integration** for notifications
- **Admin Interface** for system management

## 🏗️ Technology Stack

- **Backend**: Django 5.2, Python
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Database**: PostgreSQL (production),
- **Email**: SMTP integration
- **Media Storage**: Local file system
- **Deployment**: Render.com

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL (for production)
- Node.js (for Tailwind CSS)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/django-event-management-system.git
cd django-event-management-system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
npm install  # For Tailwind CSS
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://[username[:password]@]host[:port]/database_name
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create User Groups and Permissions
```bash
python manage.py setup_groups
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
python manage.py assign_admin_role  # Assign admin role to superuser
```

### 8. Compile Tailwind CSS
```bash
npm run build  # or python manage.py tailwind build
```

### 9. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## 👥 User Roles & Permissions

### Admin
- Full access to all features
- User management (create, edit, delete users)
- Role assignment
- System-wide settings

### Organizer
- Create and manage events
- Create and manage categories
- View RSVP lists for their events
- Access organizer dashboard

### Participant
- View and search events
- RSVP to events
- Manage their RSVPs
- Access participant dashboard

## 📁 Project Structure

```
django-event-management-system/
├── accounts/                    # User authentication & profiles
│   ├── management/commands/     # Custom Django commands
│   ├── templates/accounts/      # Account-related templates
│   └── ...
├── events/                      # Event management app
│   ├── templates/events/        # Event-related templates
│   ├── templates/events/emails/ # Email templates
│   └── ...
├── EMS/                         # Project settings
├── media/                       # User uploads
├── static/                      # Static files
├── staticfiles/                 # Collected static files
└── manage.py
```

## 🔧 Configuration

### Email Settings
Configure SMTP settings in your `.env` file for email notifications:
- RSVP confirmations
- Account activation emails
- Password reset emails

### Media Files
- Event images: `media/events/`
- Profile pictures: `media/users/profile_pictures/`
- Default images provided in `media/*/defaults/`

## 🚀 Deployment

### Render.com Deployment
1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Configure build command: `pip install -r requirements.txt`
4. Configure start command: `python manage.py collectstatic --noinput && python manage.py migrate && gunicorn EMS.wsgi:application`

### Environment Variables for Production
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=your-postgresql-url
ALLOWED_HOSTS=your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com
# Email settings...
```

## 📚 API Endpoints

### Authentication
- `/accounts/login/` - User login
- `/accounts/signup/` - User registration
- `/accounts/logout/` - User logout
- `/accounts/profile/` - User profile management

### Events
- `/` - Homepage with recent events
- `/events/` - Event list with filtering
- `/events/create/` - Create new event (Organizer+)
- `/events/<id>/` - Event details
- `/events/<id>/edit/` - Edit event (Organizer+)

### Categories
- `/categories/` - Category management (Organizer+)

### RSVP
- `/events/<id>/rsvp/` - RSVP to event
- `/events/<id>/rsvp/delete/` - Cancel RSVP

### Dashboards
- `/dashboard/` - Organizer dashboard
- `/participant-dashboard/` - Participant dashboard

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/toaha-unc/django-event-management-system/issues) page
2. Create a new issue with detailed information
3. Contact the maintainers

## 🙏 Acknowledgments

- Django framework and community
- Tailwind CSS for styling
- Render.com for hosting
- All contributors and users

---

**Built with ❤️ using Django and modern web technologies**