# Role-Based Access Control Implementation

This document outlines the implementation of role-based access control (RBAC) in the Django Event Management System.

## Overview

The system now uses Django Groups to implement three distinct user roles:

1. **Admin**: Full access to all features
2. **Organizer**: Can create, update, and delete events and categories
3. **Participant**: Can only view events and register/unregister for events

## Implementation Details

### 1. User Roles and Permissions

#### Admin Role
- Full access to all features
- Can change user roles
- Can delete users
- Can manage all events, categories, and registrations
- Access to user management interface

#### Organizer Role
- Can create, update, and delete events
- Can create, update, and delete categories
- Can view event registrations
- Cannot manage users or change roles

#### Participant Role
- Can view events and categories
- Can register/unregister for events
- Cannot create, edit, or delete events/categories
- Cannot access user management

### 2. Models

#### Updated Models
- **Event**: Added `created_by`, `created_at`, `updated_at` fields
- **UserProfile**: New model for user profile information
- **EventRegistration**: New model to track event registrations
- **Removed**: Participant model (replaced with User model)

#### Key Model Relationships
```python
# Event registration
User -> EventRegistration -> Event

# User profile
User -> UserProfile (OneToOne)

# Event creation
User -> Event (created_by)
```

### 3. Decorators

Custom decorators in `accounts/decorators.py`:

- `@admin_required`: Only Admin users
- `@organizer_required`: Only Organizer users  
- `@admin_or_organizer_required`: Admin or Organizer users
- `@participant_required`: Only Participant users
- `@any_authenticated_user`: Any logged-in user

### 4. Views and Access Control

#### Public Views (No authentication required)
- Home page (`home`)
- Event list (`event_list`)
- Event detail (`event_detail`)
- Category list (`category_list`)

#### Admin Only Views
- User management (`user_list`, `user_delete`, `user_role_update`)

#### Admin/Organizer Views
- Organizer dashboard (`organizer_dashboard`)
- Event management (`event_create`, `event_update`, `event_delete`)
- Category management (`category_create`, `category_update`, `category_delete`)

#### Authenticated User Views
- Event registration (`register_for_event`, `unregister_from_event`)

### 5. URL Structure

```
/                           # Home page (public)
/events/                    # Event list (public)
/events/<id>/              # Event detail (public)
/events/<id>/register/     # Register for event (authenticated)
/events/<id>/unregister/   # Unregister from event (authenticated)

/dashboard/                 # Organizer dashboard (admin/organizer)
/events/create/            # Create event (admin/organizer)
/events/<id>/edit/         # Edit event (admin/organizer)
/events/<id>/delete/       # Delete event (admin/organizer)

/categories/               # Category list (public)
/categories/create/        # Create category (admin/organizer)
/categories/<id>/edit/     # Edit category (admin/organizer)
/categories/<id>/delete/   # Delete category (admin/organizer)

/users/                    # User management (admin only)
/users/<id>/delete/        # Delete user (admin only)
/users/<id>/role/          # Update user role (admin only)
```

### 6. Setup Commands

#### Setup Groups
```bash
python manage.py setup_groups
```
Creates Admin, Organizer, and Participant groups with appropriate permissions.

#### Assign Admin Role
```bash
python manage.py assign_admin_role
```
Assigns superuser to Admin group.

### 7. User Registration

New users are automatically:
1. Assigned to the "Participant" group
2. Given a UserProfile instance
3. Logged in after successful registration

### 8. Templates

#### New Templates
- `user_list.html`: User management interface
- `user_role_form.html`: Role update form
- `user_confirm_delete.html`: User deletion confirmation

#### Updated Templates
- `event_detail.html`: Shows registrations instead of participants
- `organizer_dashboard.html`: Added user management link for admins

### 9. Security Features

- Role-based access control using Django Groups
- Custom decorators for view protection
- Automatic role assignment on user registration
- User profile creation for all users
- Event registration tracking

### 10. Testing the Implementation

1. **Create a superuser**: `python manage.py createsuperuser`
2. **Set up groups**: `python manage.py setup_groups`
3. **Assign admin role**: `python manage.py assign_admin_role`
4. **Register new users**: They'll automatically be assigned to Participant group
5. **Test role-based access**: Try accessing different views with different user roles

### 11. Admin Interface

All models are registered in the Django admin:
- Event management with filtering and search
- Category management
- User profile management with role display
- Event registration tracking

This implementation provides a robust, secure, and scalable role-based access control system for the event management application.
