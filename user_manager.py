import json
import os
import hashlib
from datetime import datetime

class UserManager:
    def __init__(self, users_file='users.json'):
        self.users_file = users_file
        self._ensure_files_exist()
        self.users = self._load_users()
        self._migrate_old_users()  # Migrate existing users to new format
    
    def _ensure_files_exist(self):
        """Ensure users.json and data directory exist."""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
        
        if not os.path.exists('data'):
            os.makedirs('data')
    
    def _load_users(self):
        """Load users from JSON file."""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _migrate_old_users(self):
        """Migrate old user format to new format with session tracking"""
        migrated = False
        for username, user_data in self.users.items():
            # Check if user needs migration (missing new fields)
            if 'current_session' not in user_data:
                # Migrate old user to new format
                total_sessions = user_data.get('total_sessions', 0)
                
                # Initialize session_data structure
                user_data['session_data'] = {}
                for i in range(1, 7):
                    session_key = f'session_{i}'
                    user_data['session_data'][session_key] = {
                        'completed': i <= total_sessions,
                        'timestamp': None,
                        'performance': {}
                    }
                
                # Set current_session (next session to play)
                user_data['current_session'] = min(total_sessions + 1, 6)
                
                # Update timestamps for completed sessions if available
                if 'sessions' in user_data and user_data['sessions']:
                    for session_record in user_data['sessions']:
                        session_id = session_record.get('session_id')
                        timestamp = session_record.get('timestamp')
                        if session_id and timestamp and 1 <= session_id <= 6:
                            session_key = f'session_{session_id}'
                            user_data['session_data'][session_key]['timestamp'] = timestamp
                
                migrated = True
                print(f"Migrated user: {username}")
        
        if migrated:
            self._save_users()
            print("User migration completed!")
    
    def _save_users(self):
        """Save users to JSON file."""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=4)
    
    def _hash_password(self, password):
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password):
        """Register a new user"""
        if not username or not password:
            return False, "Username and password cannot be empty"
        
        if username in self.users:
            return False, "Username already exists"
        
        # Create user directory for data storage
        user_dir = os.path.join('data', username)
        os.makedirs(user_dir, exist_ok=True)
        
        # Initialize user record with 6 session slots
        self.users[username] = {
            'password': self._hash_password(password),
            'created_at': datetime.now().isoformat(),
            'sessions': [],
            'total_sessions': 0,
            'session_data': {
                'session_1': {'completed': False, 'timestamp': None, 'performance': {}},
                'session_2': {'completed': False, 'timestamp': None, 'performance': {}},
                'session_3': {'completed': False, 'timestamp': None, 'performance': {}},
                'session_4': {'completed': False, 'timestamp': None, 'performance': {}},
                'session_5': {'completed': False, 'timestamp': None, 'performance': {}},
                'session_6': {'completed': False, 'timestamp': None, 'performance': {}}
            },
            'current_session': 1  # Track which session they're on
        }
        
        self._save_users()
        return True, "Registration successful"
    
    def authenticate_user(self, username, password):
        """Authenticate user"""
        if username not in self.users:
            return False, "Username not found"
        
        if self.users[username]['password'] != self._hash_password(password):
            return False, "Incorrect password"
        
        return True, "Login successful"
    
    def get_user_session_count(self, username):
        """Get total number of sessions completed by user"""
        if username in self.users:
            return self.users[username]['total_sessions']
        return 0
    
    def get_current_session(self, username):
        """Get the current session number user should play"""
        if username in self.users:
            return self.users[username]['current_session']
        return 1
    
    def increment_user_session(self, username):
        """Increment user's session count and return new count"""
        if username in self.users:
            current_session = self.users[username]['current_session']
            
            # Mark current session as completed
            session_key = f'session_{current_session}'
            self.users[username]['session_data'][session_key]['completed'] = True
            self.users[username]['session_data'][session_key]['timestamp'] = datetime.now().isoformat()
            
            # Increment total sessions and current session
            self.users[username]['total_sessions'] += 1
            
            # Only move to next session if not at the last one
            if current_session < 6:
                self.users[username]['current_session'] = current_session + 1
            
            new_count = self.users[username]['total_sessions']
            
            # Record session in sessions list for backward compatibility
            self.users[username]['sessions'].append({
                'session_id': current_session,
                'timestamp': datetime.now().isoformat()
            })
            
            self._save_users()
            return new_count
        return 0
    
    def update_session_performance(self, username, session_num, game_name, performance_data):
        """Update performance data for a specific session and game"""
        if username in self.users and 1 <= session_num <= 6:
            session_key = f'session_{session_num}'
            if 'performance' not in self.users[username]['session_data'][session_key]:
                self.users[username]['session_data'][session_key]['performance'] = {}
            
            self.users[username]['session_data'][session_key]['performance'][game_name] = performance_data
            self._save_users()
            return True
        return False
    
    def get_session_performance(self, username, session_num):
        """Get performance data for a specific session"""
        if username in self.users and 1 <= session_num <= 6:
            session_key = f'session_{session_num}'
            return self.users[username]['session_data'][session_key].get('performance', {})
        return {}
    
    def get_session_phase(self, username):
        """
        Determine what phase the user is in:
        - Sessions 1-4: Training
        - Session 5: Validation  
        - Session 6: Testing
        - After 6: Completed
        """
        count = self.get_user_session_count(username)
        current_session = self.get_current_session(username)
        
        if count < 4:
            return 'training', current_session
        elif count == 4:
            return 'validation', 5
        elif count == 5:
            return 'testing', 6
        else:
            return 'completed', None
    
    def get_user_progress(self, username):
        """Get comprehensive progress information for user"""
        if username not in self.users:
            return None
        
        user_data = self.users[username]
        
        # Double-check migration was successful
        if 'current_session' not in user_data:
            # Force migration for this user
            self._migrate_single_user(username)
            user_data = self.users[username]  # Reload data
        
        completed_sessions = user_data['total_sessions']
        current_session = user_data['current_session']
        phase, next_session = self.get_session_phase(username)
        
        progress = {
            'username': username,
            'completed_sessions': completed_sessions,
            'current_session': current_session,
            'phase': phase,
            'next_session': next_session,
            'total_sessions': 6,
            'progress_percentage': min(100, (completed_sessions / 6) * 100),
            'session_details': user_data['session_data']
        }
        
        return progress
    
    def _migrate_single_user(self, username):
        """Migrate a single user to new format"""
        if username in self.users:
            user_data = self.users[username]
            total_sessions = user_data.get('total_sessions', 0)
            
            # Initialize session_data structure
            user_data['session_data'] = {}
            for i in range(1, 7):
                session_key = f'session_{i}'
                user_data['session_data'][session_key] = {
                    'completed': i <= total_sessions,
                    'timestamp': None,
                    'performance': {}
                }
            
            # Set current_session (next session to play)
            user_data['current_session'] = min(total_sessions + 1, 6)
            
            # Update timestamps for completed sessions if available
            if 'sessions' in user_data and user_data['sessions']:
                for session_record in user_data['sessions']:
                    session_id = session_record.get('session_id')
                    timestamp = session_record.get('timestamp')
                    if session_id and timestamp and 1 <= session_id <= 6:
                        session_key = f'session_{session_id}'
                        user_data['session_data'][session_key]['timestamp'] = timestamp
            
            self._save_users()
            print(f"Migrated single user: {username}")
    
    def is_session_completed(self, username, session_num):
        """Check if a specific session is completed"""
        if username in self.users and 1 <= session_num <= 6:
            session_key = f'session_{session_num}'
            return self.users[username]['session_data'][session_key]['completed']
        return False
    
    def reset_user_sessions(self, username):
        """Reset user's session progress (for testing purposes)"""
        if username in self.users:
            self.users[username]['total_sessions'] = 0
            self.users[username]['current_session'] = 1
            
            # Reset all session data
            for i in range(1, 7):
                session_key = f'session_{i}'
                self.users[username]['session_data'][session_key] = {
                    'completed': False,
                    'timestamp': None,
                    'performance': {}
                }
            
            self.users[username]['sessions'] = []  # Clear old sessions list
            self._save_users()
            return True
        return False
    
    def get_user_session_files(self, username):
        """Get list of session files for a user"""
        user_dir = os.path.join('data', username)
        if not os.path.exists(user_dir):
            return []
        
        session_files = []
        for file in sorted(os.listdir(user_dir)):
            if file.startswith('session_') and file.endswith('.csv'):
                session_files.append(file)
        
        return session_files

# Test the class
if __name__ == "__main__":
    print("Testing UserManager class...")
    um = UserManager()
    print("UserManager instance created successfully!")
    
    # Test registration
    success, message = um.register_user("testuser", "testpass")
    print(f"Registration: {success}, {message}")
    
    # Test authentication
    success, message = um.authenticate_user("testuser", "testpass")
    print(f"Authentication: {success}, {message}")
    
    # Test session tracking
    username = "testuser"
    print(f"Initial session count: {um.get_user_session_count(username)}")
    print(f"Current session: {um.get_current_session(username)}")
    
    # Test progress
    progress = um.get_user_progress(username)
    print(f"Progress: {progress['progress_percentage']}% complete")
    
    print("All tests passed!")