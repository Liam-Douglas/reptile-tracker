"""
Authentication Module for Reptile Tracker
Handles user login, registration, and session management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from functools import wraps
import re

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Will be initialized in app.py
bcrypt = None
login_manager = None


class User(UserMixin):
    """User class for Flask-Login"""
    def __init__(self, user_dict):
        self.id = user_dict['id']
        self.email = user_dict['email']
        self.name = user_dict['name']
        self._is_active = user_dict.get('is_active', True)
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_active(self):
        """Override UserMixin's is_active property"""
        return self._is_active


def init_auth(app, db_path):
    """Initialize authentication system"""
    global bcrypt, login_manager
    
    # Initialize Bcrypt
    bcrypt = Bcrypt(app)
    
    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        from reptile_tracker_db import ReptileDatabase
        db = ReptileDatabase(db_path)
        user_dict = db.get_user_by_id(int(user_id))
        if user_dict:
            return User(user_dict)
        return None
    
    # Register blueprint
    app.register_blueprint(auth_bp)
    
    return bcrypt, login_manager


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        from reptile_tracker_db import ReptileDatabase
        from app import DB_PATH
        
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        name = request.form.get('name', '').strip()
        invite_code = request.form.get('invite_code', '').strip()
        
        # Validation
        if not email or not password or not name:
            flash('All fields are required', 'error')
            return render_template('auth/register.html')
        
        if not validate_email(email):
            flash('Invalid email address', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        valid, message = validate_password(password)
        if not valid:
            flash(message, 'error')
            return render_template('auth/register.html')
        
        # Create user
        db = ReptileDatabase(DB_PATH)
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user_id = db.create_user(email, password_hash, name)
        
        if not user_id:
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
        
        # Handle household
        if invite_code:
            # Join existing household
            household_id = db.validate_invite_code(invite_code)
            if household_id:
                db.add_household_member(household_id, user_id, role='member')
                flash(f'Welcome {name}! You\'ve joined the household.', 'success')
            else:
                flash('Invalid invite code. Creating your own household.', 'warning')
                household_id = db.create_household(f"{name}'s Reptiles", user_id)
        else:
            # Create new household
            household_id = db.create_household(f"{name}'s Reptiles", user_id)
        
        # Log user in
        user_dict = db.get_user_by_id(user_id)
        user = User(user_dict)
        login_user(user)
        db.update_last_login(user_id)
        
        flash(f'Welcome to Reptile Tracker, {name}!', 'success')
        return redirect(url_for('index'))
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        from reptile_tracker_db import ReptileDatabase
        from app import DB_PATH
        
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('auth/login.html')
        
        # Get user
        db = ReptileDatabase(DB_PATH)
        user_dict = db.get_user_by_email(email)
        
        if not user_dict:
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html')
        
        # Check password
        if not bcrypt.check_password_hash(user_dict['password_hash'], password):
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html')
        
        # Check if user is active
        if not user_dict.get('is_active', True):
            flash('Your account has been deactivated', 'error')
            return render_template('auth/login.html')
        
        # Log user in
        try:
            user = User(user_dict)
            login_user(user, remember=remember)
            db.update_last_login(user_dict['id'])
            
            print(f"[AUTH] User {user.name} logged in successfully")
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            print(f"[AUTH ERROR] Login failed: {e}")
            import traceback
            traceback.print_exc()
            flash('An error occurred during login. Please try again.', 'error')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    name = current_user.name
    logout_user()
    flash(f'Goodbye, {name}!', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    from reptile_tracker_db import ReptileDatabase
    from app import DB_PATH
    
    db = ReptileDatabase(DB_PATH)
    
    # Get user's household
    household = db.get_user_household(current_user.id)
    
    # Get household members
    members = []
    if household:
        members = db.get_household_members(household['id'])
    
    # Get user's devices
    devices = db.get_push_subscriptions(current_user.id)
    
    return render_template('auth/profile.html', 
                         household=household,
                         members=members,
                         devices=devices)


@auth_bp.route('/household/invite', methods=['POST'])
@login_required
def generate_invite():
    """Generate household invite code"""
    from reptile_tracker_db import ReptileDatabase
    from app import DB_PATH
    
    db = ReptileDatabase(DB_PATH)
    household = db.get_user_household(current_user.id)
    
    if not household:
        flash('You are not part of a household', 'error')
        return redirect(url_for('auth.profile'))
    
    invite_code = db.generate_invite_code(household['id'])
    
    flash(f'Invite code: {invite_code}', 'success')
    return redirect(url_for('auth.profile'))


def household_required(f):
    """Decorator to require user to be in a household"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        from reptile_tracker_db import ReptileDatabase
        from app import DB_PATH
        
        db = ReptileDatabase(DB_PATH)
        household = db.get_user_household(current_user.id)
        
        if not household:
            flash('You must be part of a household to access this page', 'error')
            return redirect(url_for('auth.profile'))
        
        return f(*args, **kwargs)
    return decorated_function

# Made with Bob
