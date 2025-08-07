# Django Event Management System

A comprehensive event management system built with Django and Tailwind CSS.

## Features

### User Authentication
- **User Registration**: Users can sign up with username, email, password, first name, and last name
- **User Login**: Secure login functionality with form validation
- **User Logout**: Secure logout with session cleanup
- **User Profile**: View user information and account details
- **Protected Views**: CRUD operations for events, participants, and categories require authentication

### Event Management
- Create, read, update, and delete events
- Manage event categories
- Track event participants
- Dashboard with statistics and analytics

## Authentication URLs

- **Sign Up**: `/accounts/signup/`
- **Login**: `/accounts/login/`
- **Logout**: `/accounts/logout/`
- **Profile**: `/accounts/profile/`

## Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django-event-management-system
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000/`
   - Sign up for a new account or login with existing credentials

## Authentication Features

### User Registration
- Users can create accounts with:
  - Username (unique)
  - Email address (unique)
  - Password (with validation)
  - First name
  - Last name

### User Login
- Secure authentication with username and password
- Form validation and error handling
- Automatic redirect after successful login

### User Profile
- View personal information
- See account creation date and last login
- Access to logout functionality

### Protected Features
The following features require user authentication:
- Organizer Dashboard
- Creating, editing, and deleting events
- Managing participants
- Managing event categories

## Security Features

- Password validation using Django's built-in validators
- CSRF protection on all forms
- Session-based authentication
- Secure logout with session cleanup
- Form validation and error handling

## Navigation

The navigation bar automatically shows different options based on authentication status:
- **Unauthenticated users**: Login and Sign Up links
- **Authenticated users**: Welcome message, Profile link, and Logout link

## Default Admin Account

A default admin account has been created:
- **Username**: admin
- **Email**: admin@example.com
- **Password**: (set during superuser creation)

## Technology Stack

- **Backend**: Django 4.x
- **Frontend**: Tailwind CSS
- **Database**: PostgreSQL
- **Authentication**: Django's built-in authentication system

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
