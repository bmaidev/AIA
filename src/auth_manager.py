# auth_manager.py
# Role-based authorization system for AIA application

import json
import os
import datetime
from typing import Dict, List, Optional, Union, Literal

# Define role types with proper type hints
RoleType = Literal['admin', 'reviewer', 'assessor', 'viewer']

# Define permission structure
class Permissions:
    """Defines the permissions available in the system"""
    # System level permissions
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_REGISTER = "view_register"
    ADD_SYSTEM = "add_system"
    DELETE_SYSTEM = "delete_system"
    
    # AIA level permissions
    VIEW_AIA = "view_aia"
    EDIT_AIA = "edit_aia"
    CHANGE_STATUS = "change_status"
    APPROVE_AIA = "approve_aia"
    EXPORT_AIA = "export_aia"
    
    # User management permissions
    MANAGE_USERS = "manage_users"
    
    @classmethod
    def get_all_permissions(cls) -> List[str]:
        """Returns all available permissions"""
        return [attr for attr in dir(cls) if not attr.startswith('__') and attr.isupper()]

# Role definitions with associated permissions
ROLE_PERMISSIONS = {
    'admin': [
        Permissions.VIEW_DASHBOARD, Permissions.VIEW_REGISTER, 
        Permissions.ADD_SYSTEM, Permissions.DELETE_SYSTEM,
        Permissions.VIEW_AIA, Permissions.EDIT_AIA, 
        Permissions.CHANGE_STATUS, Permissions.APPROVE_AIA, 
        Permissions.EXPORT_AIA, Permissions.MANAGE_USERS
    ],
    'reviewer': [
        Permissions.VIEW_DASHBOARD, Permissions.VIEW_REGISTER,
        Permissions.VIEW_AIA, Permissions.EDIT_AIA,
        Permissions.CHANGE_STATUS, Permissions.APPROVE_AIA,
        Permissions.EXPORT_AIA
    ],
    'assessor': [
        Permissions.VIEW_DASHBOARD, Permissions.VIEW_REGISTER,
        Permissions.ADD_SYSTEM, Permissions.VIEW_AIA, 
        Permissions.EDIT_AIA, Permissions.EXPORT_AIA
    ],
    'viewer': [
        Permissions.VIEW_DASHBOARD, Permissions.VIEW_REGISTER,
        Permissions.VIEW_AIA, Permissions.EXPORT_AIA
    ]
}

class User:
    """User class with role-based permissions"""
    def __init__(self, email: str, name: str, role: RoleType = 'viewer', agency: str = ''):
        self.email = email
        self.name = name
        self.role = role
        self.agency = agency
        self.created_at = datetime.datetime.now().isoformat()
        self.last_login = None
        
    def to_dict(self) -> Dict:
        """Convert user object to dictionary for storage"""
        return {
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'agency': self.agency,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create user object from dictionary"""
        user = cls(data['email'], data['name'], data['role'], data['agency'])
        user.created_at = data.get('created_at', user.created_at)
        user.last_login = data.get('last_login')
        return user
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        if self.role not in ROLE_PERMISSIONS:
            return False
        return permission in ROLE_PERMISSIONS[self.role]
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.datetime.now().isoformat()

class AuthManager:
    """Manages users and authentication"""
    def __init__(self, users_file: str = 'users.json'):
        self.users_file = users_file
        self.users: Dict[str, User] = {}
        self._load_users()
        
        # Create default admin if no users exist
        if not self.users:
            self._create_default_admin()
    
    def _load_users(self):
        """Load users from JSON file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    user_data = json.load(f)
                    for email, data in user_data.items():
                        self.users[email] = User.from_dict(data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading users: {e}")
                # Create a backup of the corrupted file
                if os.path.exists(self.users_file):
                    os.rename(self.users_file, f"{self.users_file}.bak.{datetime.datetime.now().timestamp()}")
    
    def _save_users(self):
        """Save users to JSON file"""
        try:
            user_data = {email: user.to_dict() for email, user in self.users.items()}
            with open(self.users_file, 'w') as f:
                json.dump(user_data, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving users: {e}")
            return False
    
    def _create_default_admin(self):
        """Create a default admin user"""
        admin = User("admin@example.com", "Default Admin", "admin", "System")
        self.users[admin.email] = admin
        self._save_users()
        print("Created default admin user: admin@example.com")
    
    def get_user(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.users.get(email)
    
    def add_user(self, email: str, name: str, role: RoleType = 'viewer', agency: str = '') -> bool:
        """Add a new user"""
        if email in self.users:
            return False  # User already exists
        
        self.users[email] = User(email, name, role, agency)
        return self._save_users()
    
    def update_user(self, email: str, name: str = None, role: RoleType = None, agency: str = None) -> bool:
        """Update an existing user"""
        if email not in self.users:
            return False  # User doesn't exist
        
        user = self.users[email]
        if name is not None:
            user.name = name
        if role is not None:
            user.role = role
        if agency is not None:
            user.agency = agency
            
        return self._save_users()
    
    def delete_user(self, email: str) -> bool:
        """Delete a user"""
        if email not in self.users:
            return False  # User doesn't exist
        
        del self.users[email]
        return self._save_users()
    
    def authenticate_user(self, email: str) -> Optional[User]:
        """Authenticate a user by email (OAuth already verified identity)"""
        user = self.get_user(email)
        if user:
            user.update_last_login()
            self._save_users()
        return user
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        return list(self.users.values())
    
    def user_has_permission(self, email: str, permission: str) -> bool:
        """Check if a user has a specific permission"""
        user = self.get_user(email)
        if not user:
            return False
        return user.has_permission(permission)

# Helper functions for use in the main app
def get_auth_manager() -> AuthManager:
    """Get or create the AuthManager instance"""
    # Use a file in the same directory as the app
    users_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.json')
    return AuthManager(users_file)

def get_user_role_display(role: RoleType) -> str:
    """Get a display-friendly version of the role name"""
    role_display = {
        'admin': 'Administrator',
        'reviewer': 'Reviewer',
        'assessor': 'Assessor',
        'viewer': 'Viewer'
    }
    return role_display.get(role, role.capitalize())
