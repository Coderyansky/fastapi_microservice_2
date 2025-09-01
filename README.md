# FastAPI User Management Microservice with Desktop GUI

## Overview
Complete FastAPI microservice for user management with CRUD operations, HTTP Basic Authentication, and a desktop GUI application built with Python Tkinter.

## ✅ Implementation Status
All tasks completed successfully:

### Backend API ✅
1. **Project Structure** ✅
   - Organized folder structure: app/, models/, schemas/, auth/, routes/
   - All __init__.py files in place

2. **Dependencies** ✅
   - requirements.txt with all necessary packages
   - FastAPI, SQLAlchemy, passlib[bcrypt], uvicorn, requests

3. **Database Configuration** ✅
   - SQLite database with SQLAlchemy ORM
   - Database session management
   - Automatic table creation

4. **User Model** ✅
   - Complete User model with required fields:
     - id (primary key), name, email (unique), password_hash, created_at, phone

5. **API Endpoints** ✅
   All 7 required endpoints implemented:
   - GET /users - Get all users (with auth)
   - POST /users - Create new user
   - GET /users/{user_id} - Get user by ID (with auth)
   - DELETE /users/{user_id} - Delete own profile (with auth)
   - PUT /api/user/profile - Update own profile (with auth)
   - PUT /api/user/password - Change own password (with auth)
   - POST /users/{user_id}/change-password - Admin password change (with auth)

### Desktop GUI Application ✅
6. **GUI Framework** ✅
   - Python Tkinter desktop application
   - Multi-window architecture with proper state management
   - Threaded API calls for non-blocking UI
   - Role-based interface (different views for admin vs regular users)

7. **GUI Features** ✅
   - **Login Window**: Email/password authentication with validation
   - **User Dashboard**: Profile view for regular users in card format
   - **Admin Dashboard**: User list with management capabilities
   - **Profile Editor**: Edit name, email, phone with real-time validation
   - **Password Changer**: Secure password change with confirmation
   - **Admin Functions**: Integrated user management (delete, edit, change passwords)

8. **GUI Security & UX** ✅
   - HTTP Basic Authentication integration
   - Session management with 8-hour timeout
   - Input validation and error handling
   - Secure password field handling with automatic clearing
   - User role detection and appropriate interface display
   - Error handling for network issues and server responses

## ✅ Testing Results
All endpoints tested successfully:

### ✅ User Creation
- Created user with valid data: **SUCCESS**
- Proper response format with user data
- Automatic password hashing

### ✅ Authentication
- Login with correct credentials: **SUCCESS**
- Login with wrong credentials: **PROPER ERROR** (401 Unauthorized)
- All authenticated endpoints working

### ✅ User Management
- Get all users: **SUCCESS**
- Get specific user: **SUCCESS**
- Update profile: **SUCCESS**
- Change password: **SUCCESS**
- Delete user: **SUCCESS**

### ✅ Error Handling
- Duplicate email registration: **PROPER ERROR** (409 Conflict)
- Invalid credentials: **PROPER ERROR** (401 Unauthorized)
- All error messages in required format

### ✅ Security Features
- Only users can modify their own data
- Passwords securely hashed with bcrypt
- HTTP Basic Auth working correctly

## 📁 Final Project Structure
```
fastapi_microservice_2/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app with all endpoints
│   ├── database.py          # SQLite + SQLAlchemy configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # User SQLAlchemy model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py          # Pydantic validation schemas
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── password.py      # Password hashing service
│   │   └── basic_auth.py    # HTTP Basic Auth implementation
│   ├── routes/
│   │   ├── __init__.py
│   │   └── users.py         # All 7 API endpoints
│   └── gui/                 # Desktop GUI Application
│       ├── __init__.py
│       ├── main_app.py      # Main application controller
│       ├── components/      # Core GUI components
│       │   ├── __init__.py
│       │   ├── api_client.py    # HTTP API communication
│       │   ├── auth_manager.py  # Authentication management
│       │   └── session_manager.py # User session management
│       ├── windows/         # GUI windows
│       │   ├── __init__.py
│       │   ├── login_window.py  # Login interface
│       │   ├── main_dashboard.py # Main dashboard
│       │   ├── user_profile_view.py # User profile card
│       │   ├── profile_editor.py # Profile editing
│       │   ├── password_changer.py # Password change
│       │   ├── admin_profile_editor.py # Admin profile editing
│       │   ├── admin_password_changer.py # Admin password change
│       │   └── admin_panel.py   # Admin management panel
│       └── utils/           # Utility functions
│           ├── __init__.py
│           ├── validators.py    # Input validation
│           └── helpers.py       # Helper functions
├── launcher.py              # 🚀 Complete service launcher (NEW!)
├── start_service.bat        # 🚀 Windows batch launcher (NEW!)
├── start_service.ps1        # 🚀 PowerShell launcher (NEW!)
├── main_gui.py              # GUI application entry point
├── requirements.txt         # Dependencies
├── users.db                 # SQLite database (auto-created)
├── LAUNCHER_GUIDE.md        # 📖 Detailed launcher documentation (NEW!)
└── README.md                # Documentation
```

## 🚀 How to Run

### 🎯 Quick Start (Recommended)

**Option 1: Complete Service Launcher (All-in-One)**
```bash
# Start both backend and GUI together
python launcher.py

# Or use Windows batch file (double-click)
start_service.bat

# Or use PowerShell
.\start_service.ps1
```

**Option 2: Manual Setup (Traditional)**
For more control, follow the manual steps below.

### Complete Service Launcher Features

The project includes multiple launcher options:

1. **`launcher.py`** - Main Python launcher (cross-platform)
   - Automatically starts FastAPI backend
   - Waits for backend to be ready
   - Launches GUI application
   - Handles graceful shutdown
   - Supports custom host/port configuration

2. **`start_service.bat`** - Windows batch file launcher
   - Simple double-click execution
   - Automatic virtual environment activation
   - Error handling with user prompts

3. **`start_service.ps1`** - PowerShell launcher (Windows)
   - Native PowerShell interface with colored output
   - Parameter validation and built-in help
   - Advanced error handling

**Launcher Usage Examples:**
```bash
# Basic usage
python launcher.py

# Custom port
python launcher.py --port 8080

# Backend only (no GUI)
python launcher.py --no-gui

# Custom host and GUI delay
python launcher.py --host 0.0.0.0 --gui-delay 5

# Show help
python launcher.py --help
```

**What the launcher does:**
1. ✅ Validates all dependencies
2. ✅ Starts FastAPI backend with uvicorn
3. ✅ Waits for backend health check
4. ✅ Launches GUI application
5. ✅ Handles graceful shutdown (Ctrl+C)
6. ✅ Provides detailed error messages

📖 **For detailed launcher information, see [LAUNCHER_GUIDE.md](LAUNCHER_GUIDE.md)**

### Prerequisites
- Python 3.11 or higher
- Git

### Setup and Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd fastapi_microservice_2
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   .\venv\Scripts\Activate.ps1
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the FastAPI server** (keep this running in one terminal):
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Launch the GUI application** (open a new terminal with activated environment):
   ```bash
   python main_gui.py
   ```

6. **Access the API** (optional for direct API testing):
   - API: http://localhost:8000
   - Interactive documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### Deactivating Virtual Environment
When done working on the project:
```bash
deactivate
```

## 📱 Desktop GUI Application User Guide

### Getting Started with the GUI

#### First Time Setup
1. **Create Admin User** (via API or GUI registration):
   ```bash
   # Example: Create admin user via curl
   curl -X POST "http://localhost:8000/users" \
        -H "Content-Type: application/json" \
        -d '{
          "name": "Administrator",
          "email": "admin@example.com",
          "password": "admin123",
          "phone": "+1234567890"
        }'
   ```

2. **Launch GUI Application**:
   ```bash
   python main_gui.py
   ```

#### Default Credentials
- **Admin User**: admin@example.com / admin123
- **Test User**: test@example.com / test123 (if created)

### GUI Interface Overview

#### Login Window
- **Email Field**: Enter your registered email address
- **Password Field**: Enter your password (hidden input)
- **Login Button**: Authenticate and enter the application
- **Status Messages**: Shows success/error feedback

**Features**:
- Email format validation
- Secure password input (hidden characters)
- Real-time error feedback
- Session management with 8-hour timeout

#### User Interface (Regular Users)
Regular users see a **User Profile View** with:

**Profile Card Display**:
- 👤 User icon and name
- 📧 Email address
- 📞 Phone number (if provided)
- 📅 Account creation date

**Available Actions**:
- **Edit Profile**: Modify name, email, and phone
- **Change Password**: Update account password
- **Logout**: Exit the application

#### Admin Interface (admin@example.com)
Admins see a **User Management Dashboard** with:

**User List Table**:
- Complete list of all registered users
- Columns: ID, Name, Email, Phone, Created Date
- Real-time user data with refresh capability

**Admin Actions**:
- **Double-click user**: Edit selected user's profile
- **Edit Profile**: Modify any user's information
- **Change Password**: Reset any user's password
- **Delete User**: Remove user from system (with confirmation)
- **Refresh**: Update user list data
- **Logout**: Exit admin interface

### User Operations Guide

#### Profile Management

**Edit Profile**:
1. Click "Edit Profile" button
2. Modify fields as needed:
   - **Name**: 2-100 characters
   - **Email**: Valid email format (must be unique)
   - **Phone**: Optional, Russian phone format
3. Click "Save" to apply changes
4. System validates input and shows status

**Change Password**:
1. Click "Change Password" button
2. Enter new password:
   - Minimum 8 characters
   - Must contain letters and numbers
3. Confirm password (must match)
4. Click "Save" to update
5. Password fields automatically cleared for security

#### Admin Operations Guide

**User Management**:
1. **View All Users**: User list loads automatically
2. **Select User**: Double-click on any user row
3. **Edit User Profile**:
   - Opens admin profile editor
   - Modify any user's information
   - Save changes with validation
4. **Change User Password**:
   - Select user from list
   - Click "Change Password"
   - Enter new password (validation applied)
   - Confirm changes
5. **Delete User**:
   - Select user from list
   - Click "Delete User"
   - Confirm deletion (cannot be undone)
   - User removed from system

**Safety Features**:
- All destructive actions require confirmation
- Password fields auto-clear after operations
- Real-time validation feedback
- Session timeout protection

### GUI Features & Benefits

#### Security Features
- **HTTP Basic Authentication**: Secure API communication
- **Session Management**: 8-hour automatic timeout
- **Input Validation**: Real-time field validation
- **Password Security**: Hidden input, automatic clearing
- **Role-based Access**: Different interfaces for users/admins
- **Confirmation Dialogs**: Protection against accidental actions

#### User Experience
- **Responsive Design**: Non-blocking API calls with threading
- **Real-time Feedback**: Immediate validation and status updates
- **Error Handling**: User-friendly error messages
- **Intuitive Navigation**: Clear action buttons and workflows
- **Data Consistency**: Automatic refresh after changes

#### Technical Features
- **Threaded Operations**: UI remains responsive during API calls
- **Error Recovery**: Network issue handling and retry logic
- **Memory Management**: Secure credential handling
- **State Management**: Proper window lifecycle management

### Troubleshooting

#### Common Issues

**Cannot Connect to Server**:
- Ensure FastAPI server is running on http://localhost:8000
- Check if virtual environment is activated
- Verify no firewall blocking port 8000

**Login Fails**:
- Verify email/password combination
- Check if user exists in database
- Ensure server is responding (check terminal output)

**GUI Doesn't Start**:
- Confirm tkinter is available: `python -c "import tkinter"`
- Check if all dependencies are installed
- Verify Python version (3.11+ required)

**Permission Errors**:
- Admin functions only work with admin@example.com
- Regular users cannot modify other users' data
- Check user role in database

#### Error Messages
| Error Message | Solution |
|---------------|----------|
| "Неверный логин или пароль" | Check credentials, verify user exists |
| "Недостаточно прав" | Use admin account for admin functions |
| "Email уже используется" | Choose different email address |
| "Не удается подключиться к серверу" | Start FastAPI server, check connection |
| "Пароли не совпадают" | Ensure password confirmation matches |

### Advanced Usage

#### Custom Configuration
Modify GUI settings in `app/gui/main_app.py`:
- API base URL (default: http://localhost:8000)
- Session timeout (default: 8 hours)
- Window sizes and positions

#### Development and Testing
- Use test files: `test_gui.py`, `test_gui_manual.py`
- Monitor server logs for debugging
- Check database state: view `users.db` file

### API Integration
The GUI application integrates with all FastAPI endpoints:
- User registration and authentication
- Profile management (CRUD operations)
- Password management
- Admin user management
- Proper error handling and status codes

## ✅ Requirements Compliance
- ✅ FastAPI framework
- ✅ SQLite database with SQLAlchemy ORM
- ✅ HTTP Basic Authentication
- ✅ bcrypt password hashing
- ✅ All 7 required endpoints
- ✅ Proper error handling with custom messages
- ✅ User can only modify own data
- ✅ Structured code organization
- ✅ No alembic (using Base.metadata.create_all())
- ✅ Proper response formats as specified
- ✅ Complete desktop GUI application with role-based interfaces
- ✅ Admin user management capabilities
- ✅ Session management and security features

## 📈 Complete Test Summary

### Backend API Testing ✅
- **User Creation**: ✅ Working with validation
- **Authentication**: ✅ Working with HTTP Basic Auth
- **Profile Updates**: ✅ Working with ownership checks
- **Password Changes**: ✅ Working with bcrypt hashing
- **User Deletion**: ✅ Working with proper authorization
- **Error Handling**: ✅ Working with meaningful messages
- **Security**: ✅ Working with proper access controls

### Desktop GUI Testing ✅
- **Login Interface**: ✅ Email/password authentication working
- **User Profile View**: ✅ Card-style display for regular users
- **Admin Dashboard**: ✅ User list management for admins
- **Profile Editing**: ✅ Real-time validation and updates
- **Password Changes**: ✅ Secure input and confirmation
- **Admin Functions**: ✅ User management and deletion
- **Session Management**: ✅ 8-hour timeout and security
- **Error Handling**: ✅ User-friendly error messages
- **Threading**: ✅ Non-blocking API calls
- **Role Detection**: ✅ Different interfaces for user types

### Integration Testing ✅
- **API-GUI Communication**: ✅ HTTP Basic Auth working
- **Real-time Data Sync**: ✅ Changes reflect immediately
- **Error Propagation**: ✅ Server errors handled gracefully
- **Session Persistence**: ✅ Login state maintained properly
- **Admin Privileges**: ✅ Restricted functions work correctly

Both the microservice and GUI application are fully functional and ready for production use!
