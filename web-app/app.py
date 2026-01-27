"""
Reptile Tracker Web Application
Flask-based web interface for tracking reptile care
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, send_file, make_response, session, g
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import sys
from datetime import datetime
import pandas as pd
from io import BytesIO

# Import database module from local directory
from reptile_tracker_db import ReptileDatabase
from feeding_schedules import get_feeding_recommendation, suggest_next_feeding_date
from scheduler import init_scheduler, get_scheduler
from auth import init_auth, household_required
from food_recognition import analyze_food_image, format_food_description

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production-CHANGE-ME')

# Use persistent storage path if available (for Render/Railway)
DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(DATA_DIR, 'reptile_tracker.db')
UPLOAD_PATH = os.path.join(DATA_DIR, 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_PATH
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'dng'}

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_PATH, exist_ok=True)

# Log database path for debugging
print(f"[INFO] Database path: {DB_PATH}")
print(f"[INFO] Data directory: {DATA_DIR}")
print(f"[INFO] Upload path: {UPLOAD_PATH}")
print(f"[INFO] Database exists: {os.path.exists(DB_PATH)}")

# Run automatic migration if needed (preserves existing data)
try:
    from auto_migrate import auto_migrate
    auto_migrate()
except Exception as e:
    print(f"[WARNING] Auto-migration check failed: {e}")
    print("[WARNING] If you have existing data, it may not be accessible")

# Initialize authentication system
try:
    bcrypt, login_manager = init_auth(app, DB_PATH)
    print("[INFO] Authentication system initialized successfully")
except Exception as e:
    print(f"[ERROR] Failed to initialize authentication: {e}")
    print("[ERROR] User login will not work")

# Initialize the background scheduler for automated reminders
scheduler = None
try:
    scheduler = init_scheduler(app, DB_PATH)
    print("[INFO] Background scheduler initialized successfully")
except Exception as e:
    print(f"[WARNING] Failed to initialize scheduler: {e}")
    print("[WARNING] Automated reminders will not work")

def get_db():
    """Get database connection for current request (singleton per request)"""
    if 'db' not in g:
        g.db = ReptileDatabase(DB_PATH)
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Close database connection at end of request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.template_filter('format_date')
def format_date_filter(date_string):
    """Format date string to readable format like '15 September 2025'"""
    if not date_string:
        return ''
    try:
        # Convert to string if not already
        date_str = str(date_string).strip()
        
        # Try parsing different date formats including datetime with time
        formats = [
            '%Y-%m-%d %H:%M:%S',  # SQLite datetime format
            '%Y-%m-%d',           # Standard date
            '%d/%m/%Y',           # DD/MM/YYYY
            '%m/%d/%Y'            # MM/DD/YYYY
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%d %B %Y')
            except ValueError:
                continue
        
        # If no format matches, return original
        return date_string
    except Exception:
        return date_string

@app.template_filter('days_difference')
def days_difference_filter(date_obj):
    """Calculate days difference from now"""
    if not date_obj:
        return 0
    try:
        from datetime import datetime
        if isinstance(date_obj, str):
            # Try parsing different date formats
            formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_obj, fmt)
                    break
                except ValueError:
                    continue
        
        if hasattr(date_obj, 'days'):
            return date_obj.days
        
        return (datetime.now() - date_obj).days
    except Exception:
        return 0

@app.template_filter('days_ago')
def days_ago_filter(date_string):
    """Calculate days ago from a date string"""
    if not date_string:
        return ''
    try:
        # Convert to string if not already
        date_str = str(date_string).strip()
        
        # Try parsing different date formats
        formats = [
            '%Y-%m-%d %H:%M:%S',  # SQLite datetime format
            '%Y-%m-%d',           # Standard date
            '%d/%m/%Y',           # DD/MM/YYYY
            '%m/%d/%Y'            # MM/DD/YYYY
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                days = (datetime.now() - date_obj).days
                
                if days == 0:
                    return 'Today'
                elif days == 1:
                    return '1 day ago'
                else:
                    return f'{days} days ago'
            except ValueError:
                continue
        
        return ''
    except Exception:
        return ''

@app.template_filter('days_until')
def days_until_filter(date_string):
    """Calculate days until a future date string"""
    if not date_string:
        return ''
    try:
        # Convert to string if not already
        date_str = str(date_string).strip()
        
        # Try parsing different date formats
        formats = [
            '%Y-%m-%d %H:%M:%S',  # SQLite datetime format
            '%Y-%m-%d',           # Standard date
            '%d/%m/%Y',           # DD/MM/YYYY
            '%m/%d/%Y'            # MM/DD/YYYY
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                days = (date_obj - datetime.now()).days
                
                if days == 0:
                    return 'Today'
                elif days == 1:
                    return 'in 1 day'
                elif days > 1:
                    return f'in {days} days'
                elif days == -1:
                    return '1 day ago'
                else:
                    return f'{abs(days)} days ago'
            except ValueError:
                continue
        
        return ''
    except Exception:
        return ''

@app.template_filter('calculate_age')
def calculate_age_filter(date_string):
    """Calculate age from date of birth"""
    if not date_string:
        return ''
    try:
        # Convert to string if not already
        date_str = str(date_string).strip()
        
        # Try parsing different date formats
        formats = [
            '%Y-%m-%d %H:%M:%S',  # SQLite datetime format
            '%Y-%m-%d',           # Standard date
            '%d/%m/%Y',           # DD/MM/YYYY
            '%m/%d/%Y'            # MM/DD/YYYY
        ]
        
        for fmt in formats:
            try:
                birth_date = datetime.strptime(date_str, fmt)
                today = datetime.now()
                
                years = today.year - birth_date.year
                months = today.month - birth_date.month
                
                # Adjust if birthday hasn't occurred this year
                if months < 0 or (months == 0 and today.day < birth_date.day):
                    years -= 1
                    months += 12
                
                if years > 0:
                    return f'{years}y old'
                elif months > 0:
                    return f'{months}mo old'
                else:
                    days = (today - birth_date).days
                    return f'{days}d old'
            except ValueError:
                continue
        
        return ''
    except Exception:
        return ''

@app.route('/')
def index():
    """Redirect to reptiles page or login if not authenticated"""
    if current_user.is_authenticated:
        return redirect(url_for('reptiles_page'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard - show all reptiles with inventory and expense overview (legacy route)"""
    db = get_db()
    reptiles = db.get_all_reptiles()
    stats = db.get_dashboard_stats()
    overdue_feedings = db.get_overdue_feedings()
    upcoming_feedings = db.get_upcoming_feedings(days_ahead=7)
    
    # Get inventory data
    inventory = db.get_food_inventory()
    low_stock = [item for item in inventory if 0 < item['quantity'] <= 5]
    out_of_stock = [item for item in inventory if item['quantity'] == 0]
    total_inventory_value = sum(
        (item['quantity'] * item.get('cost_per_unit', 0))
        for item in inventory if item.get('cost_per_unit')
    )
    
    # Get expense data (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    recent_receipts = db.get_purchase_receipts()
    monthly_expenses = sum(
        receipt.get('total_cost', 0)
        for receipt in recent_receipts
        if receipt.get('receipt_date', '') >= thirty_days_ago
    )
    
    # Get recent activity (last 7 days) and last feeding for each reptile
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    recent_feedings = []
    recent_sheds = []
    
    for reptile in reptiles:
        # Get recent feedings for this reptile
        feedings = db.get_feeding_logs(reptile['id'], limit=10)
        
        # Add last feeding date to reptile
        if feedings:
            reptile['last_feeding_date'] = feedings[0].get('feeding_date')
        
        for feeding in feedings:
            if feeding.get('feeding_date', '') >= seven_days_ago:
                feeding['reptile_name'] = reptile['name']
                recent_feedings.append(feeding)
        
        # Get recent sheds for this reptile
        sheds = db.get_shed_records(reptile['id'], limit=10)
        for shed in sheds:
            if shed.get('shed_date', '') >= seven_days_ago:
                shed['reptile_name'] = reptile['name']
                recent_sheds.append(shed)
    
    # Sort by date (most recent first)
    recent_feedings.sort(key=lambda x: x.get('feeding_date', ''), reverse=True)
    recent_sheds.sort(key=lambda x: x.get('shed_date', ''), reverse=True)
    
    # Add to stats dict
    stats['recent_feedings'] = recent_feedings
    stats['recent_sheds'] = recent_sheds
    stats['total_feedings'] = len([f for r in reptiles for f in db.get_feeding_logs(r['id'], limit=1000)])
    stats['total_sheds'] = len([s for r in reptiles for s in db.get_shed_records(r['id'], limit=1000)])
    
    return render_template('dashboard.html',
                         reptiles=reptiles,
                         stats=stats,
                         overdue_feedings=overdue_feedings,
                         upcoming_feedings=upcoming_feedings,
                         inventory_count=len(inventory),
                         low_stock_count=len(low_stock),
                         out_of_stock_count=len(out_of_stock),
                         low_stock_items=low_stock[:3],
                         out_of_stock_items=out_of_stock[:3],
                         total_inventory_value=total_inventory_value,
                         monthly_expenses=monthly_expenses,
                         now=datetime.now())

@app.route('/reptiles')
@login_required
@household_required
def reptiles_page():
    """Show all reptiles with records and reminders"""
    db = get_db()
    # Get user's household
    household = db.get_user_household(current_user.id)
    if not household:
        flash('No household found. Please contact support.', 'error')
        return redirect(url_for('auth.profile'))
    
    # Get reptiles for this household
    try:
        reptiles = db.get_reptiles_by_household(household['id'])
    except Exception as e:
        print(f"[ERROR] Failed to get reptiles by household: {e}")
        
        # Check if household_id column exists
        db.cursor.execute("PRAGMA table_info(reptiles)")
        columns = [column[1] for column in db.cursor.fetchall()]
        
        if 'household_id' not in columns:
            print("[ERROR] household_id column missing, adding it now...")
            db.cursor.execute("""
                ALTER TABLE reptiles
                ADD COLUMN household_id INTEGER
                REFERENCES households(id)
            """)
            db.conn.commit()
            print("[SUCCESS] household_id column added")
        
        # Fallback: get all reptiles and filter manually
        all_reptiles = db.get_all_reptiles()
        if all_reptiles is None:
            all_reptiles = []
        
        # Check if any reptiles lack household_id
        orphaned_reptiles = [r for r in all_reptiles if not r.get('household_id')]
        
        if orphaned_reptiles:
            print(f"[WARNING] Found {len(orphaned_reptiles)} reptiles without household_id, assigning to household {household['id']}")
            for reptile in orphaned_reptiles:
                db.cursor.execute("UPDATE reptiles SET household_id = ? WHERE id = ?",
                                (household['id'], reptile['id']))
            db.conn.commit()
            print(f"[SUCCESS] Assigned {len(orphaned_reptiles)} reptiles to household")
            # Refresh the reptile list after assignment
            all_reptiles = db.get_all_reptiles()
        
        reptiles = [r for r in all_reptiles if r.get('household_id') == household['id']]
    
    # Get last feeding, next feeding, tank cleaning, and handling for each reptile
    for reptile in reptiles:
        feedings = db.get_feeding_logs(reptile['id'], limit=1)
        if feedings:
            reptile['last_feeding_date'] = feedings[0].get('feeding_date')
        
        # Get next feeding date from reminders
        reminder = db.get_feeding_reminders(reptile['id'])
        if reminder:
            reptile['next_feeding_date'] = reminder[0].get('next_feeding_date')
        else:
            reptile['next_feeding_date'] = None
        
        # Get last tank cleaning
        last_cleaning = db.get_last_tank_cleaning(reptile['id'])
        reptile['last_tank_cleaning_date'] = last_cleaning.get('cleaning_date') if last_cleaning else None
        
        # Get last handling
        last_handling = db.get_last_handling(reptile['id'])
        reptile['last_handling_date'] = last_handling.get('handling_date') if last_handling else None
    
    # Get all feeding logs and shed records
    all_feeding_logs = db.get_feeding_logs(limit=50)
    all_shed_records = db.get_shed_records(limit=50)
    
    # Get tank cleaning and handling logs
    all_tank_cleaning_logs = db.get_tank_cleaning_logs(limit=50)
    all_handling_logs = db.get_handling_logs(limit=50)
    
    # Get feeding reminders
    reminders = db.get_feeding_reminders()
    overdue_feedings = db.get_overdue_feedings()
    upcoming_feedings = db.get_upcoming_feedings(days_ahead=7)
    
    # Get inventory alerts
    inventory = db.get_food_inventory()
    low_stock = [item for item in inventory if 0 < item['quantity'] <= 5]
    out_of_stock = [item for item in inventory if item['quantity'] == 0]
    
    # Calculate total alerts
    total_alerts = len(overdue_feedings) + len(low_stock) + len(out_of_stock)
    
    # Debug logging
    print(f"DEBUG: Total inventory items: {len(inventory)}")
    print(f"DEBUG: Low stock items: {len(low_stock)}")
    print(f"DEBUG: Out of stock items: {len(out_of_stock)}")
    print(f"DEBUG: Overdue feedings: {len(overdue_feedings)}")
    print(f"DEBUG: Total alerts: {total_alerts}")
    if low_stock:
        print(f"DEBUG: Low stock details: {low_stock}")
    
    return render_template('reptiles.html',
                         reptiles=reptiles,
                         feeding_logs=all_feeding_logs,
                         shed_records=all_shed_records,
                         tank_cleaning_logs=all_tank_cleaning_logs,
                         handling_logs=all_handling_logs,
                         reminders=reminders,
                         overdue_feedings=overdue_feedings,
                         upcoming_feedings=upcoming_feedings,
                         low_stock=low_stock,
                         out_of_stock=out_of_stock,
                         total_alerts=total_alerts)

@app.route('/reptile/<int:reptile_id>')
@login_required
@household_required
def reptile_details(reptile_id):
    """Show detailed reptile information"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        flash('Reptile not found', 'error')
        return redirect(url_for('index'))
    
    feeding_logs = db.get_feeding_logs(reptile_id, limit=10)
    shed_records = db.get_shed_records(reptile_id, limit=10)
    
    # Get last feeding details with food item
    last_feeding = feeding_logs[0] if feeding_logs else None
    last_feeding_days = None
    last_food_item = None
    if last_feeding:
        from datetime import datetime
        last_date = datetime.strptime(last_feeding['feeding_date'], '%Y-%m-%d')
        today = datetime.now()
        last_feeding_days = (today - last_date).days
        # Format food item display
        if last_feeding.get('food_size'):
            last_food_item = f"{last_feeding['food_size']} {last_feeding['food_type']}"
        else:
            last_food_item = last_feeding['food_type']
    
    # Get AI-powered feeding suggestion
    try:
        feeding_suggestion = get_feeding_recommendation(reptile, feeding_logs)
    except Exception as e:
        print(f"[ERROR] Failed to get feeding recommendation: {e}")
        feeding_suggestion = None
    
    # Get next feeding date from reminders
    reminder = db.get_feeding_reminders(reptile_id)
    next_feeding_date = reminder[0].get('next_feeding_date') if reminder else None
    next_food_item = reminder[0].get('food_type') if reminder else None
    
    # Use AI suggestion if no manual reminder is set
    if not next_feeding_date and feeding_suggestion and feeding_suggestion.get('suggested_date'):
        next_feeding_date = feeding_suggestion['suggested_date']
        # Use last food item as suggestion
        next_food_item = last_food_item if last_food_item else None
    
    # Format next food item display
    if next_food_item and reminder and reminder[0].get('food_size'):
        next_food_item = f"{reminder[0]['food_size']} {next_food_item}"
    
    # Calculate days until next feeding
    days_until_feeding = None
    if next_feeding_date:
        from datetime import datetime
        next_date = datetime.strptime(next_feeding_date, '%Y-%m-%d')
        today = datetime.now()
        days_until_feeding = (next_date - today).days
    
    # Get last tank cleaning and handling with days ago
    last_tank_cleaning = db.get_last_tank_cleaning(reptile_id)
    last_tank_cleaning_days = None
    if last_tank_cleaning:
        from datetime import datetime
        cleaning_date = datetime.strptime(last_tank_cleaning['cleaning_date'], '%Y-%m-%d')
        today = datetime.now()
        last_tank_cleaning_days = (today - cleaning_date).days
    
    last_handling = db.get_last_handling(reptile_id)
    last_handling_days = None
    if last_handling:
        from datetime import datetime
        handling_date = datetime.strptime(last_handling['handling_date'], '%Y-%m-%d')
        today = datetime.now()
        last_handling_days = (today - handling_date).days
    
    return render_template('reptile_details.html',
                         reptile=reptile,
                         feeding_logs=feeding_logs,
                         shed_records=shed_records,
                         last_feeding_days=last_feeding_days,
                         last_food_item=last_food_item,
                         feeding_suggestion=feeding_suggestion,
                         next_feeding_date=next_feeding_date,
                         next_food_item=next_food_item,
                         days_until_feeding=days_until_feeding,
                         last_tank_cleaning=last_tank_cleaning,
                         last_tank_cleaning_days=last_tank_cleaning_days,
                         last_handling=last_handling,
                         last_handling_days=last_handling_days)

@app.route('/reptile/add', methods=['GET', 'POST'])
@login_required
@household_required
def add_reptile():
    """Add new reptile"""
    db = get_db()
    # Get user's household
    household = db.get_user_household(current_user.id)
    if not household:
        flash('No household found. Please contact support.', 'error')
        return redirect(url_for('auth.profile'))
    
    if request.method == 'POST':
        try:
            # Handle image upload
            image_path = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to filename to avoid conflicts
                    name, ext = os.path.splitext(filename)
                    filename = f"{name}_{int(datetime.now().timestamp())}{ext}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    image_path = filename
            
            # Get form data
            data = {
                'name': request.form.get('name'),
                'species': request.form.get('species'),
                'morph': request.form.get('morph') or None,
                'sex': request.form.get('sex') or None,
                'date_of_birth': request.form.get('date_of_birth') or None,
                'acquisition_date': request.form.get('acquisition_date') or None,
                'weight_grams': float(request.form.get('weight_grams')) if request.form.get('weight_grams') else None,
                'length_cm': float(request.form.get('length_cm')) if request.form.get('length_cm') else None,
                'notes': request.form.get('notes') or None,
                'image_path': image_path,
                'household_id': household['id']
            }
            
            reptile_id = db.add_reptile(**data)
            flash(f'{data["name"]} has been added successfully!', 'success')
            return redirect(url_for('reptile_details', reptile_id=reptile_id))
        except Exception as e:
            flash(f'Error adding reptile: {str(e)}', 'error')
    
    return render_template('reptile_form.html', mode='add', reptile=None)

@app.route('/reptile/<int:reptile_id>/edit', methods=['GET', 'POST'])
@login_required
@household_required
def edit_reptile(reptile_id):
    """Edit existing reptile"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        flash('Reptile not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Handle image upload
            image_path = reptile['image_path']
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    name, ext = os.path.splitext(filename)
                    filename = f"{name}_{int(datetime.now().timestamp())}{ext}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    image_path = filename
            
            # Get form data
            data = {
                'name': request.form.get('name'),
                'species': request.form.get('species'),
                'morph': request.form.get('morph') or None,
                'sex': request.form.get('sex') or None,
                'date_of_birth': request.form.get('date_of_birth') or None,
                'acquisition_date': request.form.get('acquisition_date') or None,
                'weight_grams': float(request.form.get('weight_grams')) if request.form.get('weight_grams') else None,
                'length_cm': float(request.form.get('length_cm')) if request.form.get('length_cm') else None,
                'notes': request.form.get('notes') or None,
                'image_path': image_path
            }
            
            db.update_reptile(reptile_id, **data)
            flash(f'{data["name"]} has been updated successfully!', 'success')
            return redirect(url_for('reptile_details', reptile_id=reptile_id))
        except Exception as e:
            flash(f'Error updating reptile: {str(e)}', 'error')
    
    return render_template('reptile_form.html', mode='edit', reptile=reptile)

@app.route('/reptile/<int:reptile_id>/delete', methods=['POST'])
@login_required
@household_required
def delete_reptile(reptile_id):
    """Delete reptile"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if reptile:
        db.delete_reptile(reptile_id)
        flash(f'{reptile["name"]} has been deleted', 'success')
    return redirect(url_for('index'))

@app.route('/feeding')
@login_required
@household_required
def feeding_logs():
    """Show all feeding logs with optional reptile filter"""
    db = get_db()
    reptile_id = request.args.get('reptile_id', type=int)
    
    if reptile_id:
        logs = db.get_feeding_logs(reptile_id=reptile_id, limit=100)
    else:
        logs = db.get_all_feeding_logs(limit=100, household_id=current_user.household_id)
    
    reptiles = db.get_reptiles_by_household(current_user.household_id)
    return render_template('feeding_logs.html', logs=logs, reptiles=reptiles, selected_reptile_id=reptile_id)

@app.route('/api/feeding-form/<int:reptile_id>')
def get_feeding_form_data(reptile_id):
    """Get feeding form data as JSON"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        return jsonify({'error': 'Reptile not found'}), 404
    
    inventory_items = db.get_food_inventory(include_zero=False)
    food_types = db.get_distinct_food_types()
    food_sizes = db.get_distinct_food_sizes()
    
    return jsonify({
        'reptile': reptile,
        'inventory_items': inventory_items,
        'food_types': food_types,
        'food_sizes': food_sizes,
        'today': datetime.now().strftime('%Y-%m-%d')
    })

@app.route('/api/feeding/<int:reptile_id>', methods=['POST'])
def api_log_feeding(reptile_id):
    """API endpoint to log feeding"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        return jsonify({'error': 'Reptile not found'}), 404
    
    try:
        # Get inventory_id if using inventory
        use_inventory = request.json.get('use_inventory') == 'yes'
        inventory_id = int(request.json.get('inventory_id')) if use_inventory and request.json.get('inventory_id') else None
        
        # Get quantity
        if use_inventory and request.json.get('inventory_quantity'):
            quantity = int(request.json.get('inventory_quantity'))
        else:
            quantity = int(request.json.get('quantity', 1))
        
        data = {
            'reptile_id': reptile_id,
            'feeding_date': request.json.get('date') or datetime.now().strftime('%Y-%m-%d'),
            'food_type': request.json.get('food_type'),
            'food_size': request.json.get('food_size') or None,
            'quantity': quantity,
            'ate': request.json.get('ate') == 'yes',
            'notes': request.json.get('notes') or None,
            'inventory_id': inventory_id,
            'auto_deduct': True,
            'created_by': current_user.id
        }
        db.add_feeding_log(**data)
        
        # Update feeding reminder dates if reminder exists
        db.update_feeding_reminder_dates(reptile_id, data['feeding_date'])
        
        message = f'Feeding logged for {reptile["name"]}!'
        if inventory_id and data['ate']:
            message += ' Inventory automatically deducted.'
        
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/analyze-food', methods=['POST'])
@login_required
def analyze_food():
    """Analyze food image using AI to identify food items"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Remove data URI prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Analyze the image
        result = analyze_food_image(image_data)
        
        if not result.get('success'):
            return jsonify({
                'error': result.get('error', 'Failed to analyze image'),
                'food_items': [],
                'food_type': 'Unknown'
            }), 400
        
        # Format the response
        food_description = format_food_description(result['food_items'])
        
        return jsonify({
            'success': True,
            'food_items': result['food_items'],
            'food_type': result['food_type'],
            'food_description': food_description,
            'confidence': result['confidence'],
            'description': result.get('description', '')
        })
        
    except Exception as e:
        print(f"Error in analyze_food: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/feeding/<int:reptile_id>', methods=['GET', 'POST'])
def log_feeding(reptile_id):
    """Log feeding for specific reptile"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        flash('Reptile not found', 'error')
        return redirect(url_for('reptiles_page'))
    
    if request.method == 'POST':
        try:
            # Get inventory_id if using inventory
            use_inventory = request.form.get('use_inventory') == 'yes'
            inventory_id = int(request.form.get('inventory_id')) if use_inventory and request.form.get('inventory_id') else None
            
            # Get quantity - use inventory_quantity if using inventory, otherwise use quantity field
            if use_inventory and request.form.get('inventory_quantity'):
                quantity = int(request.form.get('inventory_quantity'))
            else:
                quantity = int(request.form.get('quantity', 1))
            
            data = {
                'reptile_id': reptile_id,
                'feeding_date': request.form.get('date') or datetime.now().strftime('%Y-%m-%d'),
                'food_type': request.form.get('food_type'),
                'food_size': request.form.get('food_size') or None,
                'quantity': quantity,
                'ate': request.form.get('ate') == 'yes',
                'notes': request.form.get('notes') or None,
                'inventory_id': inventory_id,
                'auto_deduct': True  # Always auto-deduct when inventory_id is provided
            }
            db.add_feeding_log(**data)
            
            # Update feeding reminder dates if reminder exists
            db.update_feeding_reminder_dates(reptile_id, data['feeding_date'])
            
            if inventory_id and data['ate']:
                flash(f'Feeding logged for {reptile["name"]} and inventory automatically deducted!', 'success')
            else:
                flash(f'Feeding logged for {reptile["name"]}!', 'success')
            return redirect(url_for('reptile_details', reptile_id=reptile_id))
        except Exception as e:
            flash(f'Error logging feeding: {str(e)}', 'error')
    
    # Get available inventory items for selection
    inventory_items = db.get_food_inventory(include_zero=False)
    # Get distinct food types and sizes for dropdowns
    food_types = db.get_distinct_food_types()
    food_sizes = db.get_distinct_food_sizes()
    return render_template('feeding_form.html', reptile=reptile, log=None,
                         inventory_items=inventory_items, food_types=food_types,
                         food_sizes=food_sizes)

@app.route('/feeding/add', methods=['GET', 'POST'])
def add_feeding():
    """Add feeding log"""
    db = get_db()
    if request.method == 'POST':
        try:
            # Get inventory_id if using inventory
            use_inventory = request.form.get('use_inventory') == 'yes'
            inventory_id = int(request.form.get('inventory_id')) if use_inventory and request.form.get('inventory_id') else None
            
            # Get quantity - use inventory_quantity if using inventory, otherwise use quantity field
            if use_inventory and request.form.get('inventory_quantity'):
                quantity = int(request.form.get('inventory_quantity'))
            else:
                quantity = int(request.form.get('quantity', 1))
            
            data = {
                'reptile_id': int(request.form.get('reptile_id')),
                'feeding_date': request.form.get('date'),
                'food_type': request.form.get('food_type'),
                'food_size': request.form.get('food_size') or None,
                'quantity': quantity,
                'ate': request.form.get('ate') == 'yes',
                'notes': request.form.get('notes') or None,
                'inventory_id': inventory_id,
                'auto_deduct': True  # Always auto-deduct when inventory_id is provided
            }
            db.add_feeding_log(**data)
            
            # Update feeding reminder dates if reminder exists
            db.update_feeding_reminder_dates(data['reptile_id'], data['feeding_date'])
            
            if inventory_id and data['ate']:
                flash('Feeding log added and inventory automatically deducted!', 'success')
            else:
                flash('Feeding log added successfully!', 'success')
            return redirect(url_for('feeding_logs'))
        except Exception as e:
            flash(f'Error adding feeding log: {str(e)}', 'error')
    
    reptiles = db.get_all_reptiles()
    # Get available inventory items for selection
    inventory_items = db.get_food_inventory(include_zero=False)
    # Get distinct food types and sizes for dropdowns
    food_types = db.get_distinct_food_types()
    food_sizes = db.get_distinct_food_sizes()
    return render_template('feeding_form.html', reptiles=reptiles, log=None,
                         inventory_items=inventory_items, food_types=food_types,
                         food_sizes=food_sizes)

@app.route('/feeding/<int:log_id>/delete', methods=['POST'])
def delete_feeding(log_id):
    """Delete feeding log"""
    db = get_db()
    if db.delete_feeding_log(log_id):
        flash('Feeding log deleted successfully!', 'success')
    else:
        flash('Error deleting feeding log', 'error')
    return redirect(url_for('feeding_logs'))

@app.route('/shed')
@login_required
@household_required
def shed_records():
    """Show all shed records"""
    db = get_db()
    records = db.get_all_shed_records(limit=100)
    reptiles = db.get_all_reptiles()
    return render_template('shed_records.html', records=records, reptiles=reptiles)

@app.route('/api/shed-form/<int:reptile_id>')
@login_required
@household_required
def get_shed_form_data(reptile_id):
    """Get shed form data as JSON"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        return jsonify({'error': 'Reptile not found'}), 404
    
    # Verify reptile belongs to user's household
    reptile_household = reptile.get('household_id')
    user_household = current_user.household_id
    
    # Allow access if both are None (legacy data) or if they match
    if reptile_household is not None and user_household is not None:
        if reptile_household != user_household:
            return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'reptile': reptile,
        'today': datetime.now().strftime('%Y-%m-%d')
    })

@app.route('/api/shed/<int:reptile_id>', methods=['POST'])
@login_required
@household_required
def api_log_shed(reptile_id):
    """API endpoint to log shed"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        return jsonify({'error': 'Reptile not found'}), 404
    
    # Verify reptile belongs to user's household
    reptile_household = reptile.get('household_id')
    user_household = current_user.household_id
    
    # Allow access if both are None (legacy data) or if they match
    if reptile_household is not None and user_household is not None:
        if reptile_household != user_household:
            return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = {
            'reptile_id': reptile_id,
            'shed_date': request.json.get('date') or datetime.now().strftime('%Y-%m-%d'),
            'complete': request.json.get('complete') == 'yes',
            'shed_length_cm': float(request.json.get('shed_length_cm')) if request.json.get('shed_length_cm') else None,
            'notes': request.json.get('notes') or None,
            'created_by': current_user.id
        }
        db.add_shed_record(**data)
        return jsonify({'success': True, 'message': f'Shed record logged for {reptile["name"]}!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/shed/<int:reptile_id>', methods=['GET', 'POST'])
@login_required
@household_required
def log_shed(reptile_id):
    """Log shed for specific reptile"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        flash('Reptile not found', 'error')
        return redirect(url_for('reptiles_page'))
    
    # Verify reptile belongs to user's household
    reptile_household = reptile.get('household_id')
    user_household = current_user.household_id
    
    # Allow access if both are None (legacy data) or if they match
    if reptile_household is not None and user_household is not None:
        if reptile_household != user_household:
            flash('Access denied', 'error')
            return redirect(url_for('reptiles_page'))
    
    if request.method == 'POST':
        try:
            data = {
                'reptile_id': reptile_id,
                'shed_date': request.form.get('date') or datetime.now().strftime('%Y-%m-%d'),
                'complete': request.form.get('complete') == 'yes',
                'shed_length_cm': float(request.form.get('shed_length_cm')) if request.form.get('shed_length_cm') else None,
                'notes': request.form.get('notes') or None
            }
            db.add_shed_record(**data)
            flash(f'Shed record logged for {reptile["name"]}!', 'success')
            return redirect(url_for('reptile_details', reptile_id=reptile_id))
        except Exception as e:
            flash(f'Error logging shed: {str(e)}', 'error')
    
    return render_template('shed_form.html', reptile=reptile, record=None)

@app.route('/shed/add', methods=['GET', 'POST'])
@login_required
@household_required
def add_shed():
    """Add shed record"""
    db = get_db()
    if request.method == 'POST':
        try:
            reptile_id = int(request.form.get('reptile_id'))
            # Verify reptile belongs to user's household
            reptile = db.get_reptile(reptile_id)
            if not reptile:
                flash('Reptile not found', 'error')
                return redirect(url_for('shed_records'))
            
            reptile_household = reptile.get('household_id')
            user_household = current_user.household_id
            
            # Allow access if both are None (legacy data) or if they match
            if reptile_household is not None and user_household is not None:
                if reptile_household != user_household:
                    flash('Access denied', 'error')
                    return redirect(url_for('shed_records'))
            
            data = {
                'reptile_id': reptile_id,
                'shed_date': request.form.get('date'),
                'complete': request.form.get('complete') == 'yes',
                'shed_length_cm': float(request.form.get('shed_length_cm')) if request.form.get('shed_length_cm') else None,
                'notes': request.form.get('notes') or None
            }
            db.add_shed_record(**data)
            flash('Shed record added successfully!', 'success')
            return redirect(url_for('shed_records'))
        except Exception as e:
            flash(f'Error adding shed record: {str(e)}', 'error')
    
    # Get reptiles for user's household
    reptiles = db.get_reptiles_by_household(current_user.household_id) or []
    return render_template('shed_form.html', reptiles=reptiles, record=None)

@app.route('/api/tank-cleaning-form/<int:reptile_id>')
def get_tank_cleaning_form_data(reptile_id):
    """Get tank cleaning form data as JSON"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        return jsonify({'error': 'Reptile not found'}), 404
    
    return jsonify({
        'reptile': reptile,
        'today': datetime.now().strftime('%Y-%m-%d')
    })

@app.route('/api/tank-cleaning/<int:reptile_id>', methods=['POST'])
def api_log_tank_cleaning(reptile_id):
    """API endpoint to log tank cleaning"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        return jsonify({'error': 'Reptile not found'}), 404
    
    try:
        data = {
            'reptile_id': reptile_id,
            'cleaning_date': request.json.get('cleaning_date') or datetime.now().strftime('%Y-%m-%d'),
            'cleaning_type': request.json.get('cleaning_type'),
            'notes': request.json.get('notes') or None,
            'created_by': current_user.id
        }
        db.add_tank_cleaning_log(**data)
        return jsonify({'success': True, 'message': f'Tank cleaning logged for {reptile["name"]}!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/tank-cleaning/<int:reptile_id>', methods=['GET', 'POST'])
def log_tank_cleaning(reptile_id):
    """Log tank cleaning"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        flash('Reptile not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            data = {
                'reptile_id': reptile_id,
                'cleaning_date': request.form.get('cleaning_date') or datetime.now().strftime('%Y-%m-%d'),
                'cleaning_type': request.form.get('cleaning_type'),
                'notes': request.form.get('notes') or None
            }
            db.add_tank_cleaning_log(**data)
            flash(f'Tank cleaning logged for {reptile["name"]}!', 'success')
            return redirect(url_for('reptile_details', reptile_id=reptile_id))
        except Exception as e:
            flash(f'Error logging tank cleaning: {str(e)}', 'error')
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('tank_cleaning_form.html', reptile=reptile, today=today)

@app.route('/api/handling-form/<int:reptile_id>')
def get_handling_form_data(reptile_id):
    """Get handling form data as JSON"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        return jsonify({'error': 'Reptile not found'}), 404
    
    return jsonify({
        'reptile': reptile,
        'today': datetime.now().strftime('%Y-%m-%d')
    })

@app.route('/api/handling/<int:reptile_id>', methods=['POST'])
def api_log_handling(reptile_id):
    """API endpoint to log handling"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        return jsonify({'error': 'Reptile not found'}), 404
    
    try:
        data = {
            'reptile_id': reptile_id,
            'handling_date': request.json.get('handling_date') or datetime.now().strftime('%Y-%m-%d'),
            'duration_minutes': int(request.json.get('duration_minutes')) if request.json.get('duration_minutes') else None,
            'behavior': request.json.get('behavior') or None,
            'notes': request.json.get('notes') or None,
            'created_by': current_user.id
        }
        db.add_handling_log(**data)
        return jsonify({'success': True, 'message': f'Handling session logged for {reptile["name"]}!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/handling/<int:reptile_id>', methods=['GET', 'POST'])
def log_handling(reptile_id):
    """Log handling session"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        flash('Reptile not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            data = {
                'reptile_id': reptile_id,
                'handling_date': request.form.get('handling_date') or datetime.now().strftime('%Y-%m-%d'),
                'duration_minutes': int(request.form.get('duration_minutes')) if request.form.get('duration_minutes') else None,
                'behavior': request.form.get('behavior') or None,
                'notes': request.form.get('notes') or None,
                'created_by': current_user.id
            }
            db.add_handling_log(**data)
            flash(f'Handling session logged for {reptile["name"]}!', 'success')
            return redirect(url_for('reptile_details', reptile_id=reptile_id))
        except Exception as e:
            flash(f'Error logging handling: {str(e)}', 'error')
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('handling_form.html', reptile=reptile, today=today)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ==================== IMPORT/EXPORT ROUTES ====================

@app.route('/import')
def import_page():
    """Show import page"""
    return render_template('import_data.html')

@app.route('/import/template/<data_type>')
def download_template(data_type):
    """Download Excel template for data import"""
    
    if data_type == 'reptiles':
        # Create reptiles template
        df = pd.DataFrame(columns=[
            'name', 'species', 'morph', 'sex', 'date_of_birth', 
            'acquisition_date', 'weight_grams', 'length_cm', 'notes'
        ])
        # Add example row
        df.loc[0] = [
            'Example Snake', 'Ball Python', 'Banana', 'Male', '2023-01-15',
            '2023-06-20', 250.5, 90.0, 'Example notes here'
        ]
        filename = 'reptiles_import_template.xlsx'
        
    elif data_type == 'feeding':
        # Create feeding logs template
        df = pd.DataFrame(columns=[
            'reptile_name', 'feeding_date', 'food_type', 'food_size', 
            'quantity', 'ate', 'notes'
        ])
        # Add example row
        df.loc[0] = [
            'Example Snake', '2024-01-15', 'Mouse', 'Medium', 1, 'yes', 'Ate well'
        ]
        filename = 'feeding_logs_import_template.xlsx'
        
    elif data_type == 'sheds':
        # Create shed records template
        df = pd.DataFrame(columns=[
            'reptile_name', 'shed_date', 'complete', 'shed_length_cm', 'notes'
        ])
        # Add example row
        df.loc[0] = [
            'Example Snake', '2024-01-20', 'yes', 95.0, 'Complete shed'
        ]
        filename = 'shed_records_import_template.xlsx'
    else:
        flash('Invalid template type', 'error')
        return redirect(url_for('import_page'))
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@app.route('/import/upload', methods=['POST'])
def upload_import():
    """Process uploaded import file"""
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('import_page'))
    
    file = request.files['file']
    data_type = request.form.get('data_type')
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('import_page'))
    
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        flash('Invalid file type. Please upload Excel (.xlsx, .xls) or CSV file', 'error')
        return redirect(url_for('import_page'))
    
    try:
        # Read file based on type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # Convert DataFrame to list of dictionaries
        data = df.to_dict('records')
        
        # Remove example rows (first row if it contains 'Example')
        if data and any('Example' in str(v) for v in data[0].values()):
            data = data[1:]
        
        if not data:
            flash('No data found in file', 'error')
            return redirect(url_for('import_page'))
        
        db = get_db()
        
        # Import based on data type
        if data_type == 'reptiles':
            imported, errors = db.bulk_import_reptiles(data)
            flash(f'Successfully imported {imported} reptile(s)', 'success')
            
        elif data_type == 'feeding':
            imported, errors = db.bulk_import_feeding_logs(data)
            flash(f'Successfully imported {imported} feeding log(s)', 'success')
            
        elif data_type == 'sheds':
            imported, errors = db.bulk_import_shed_records(data)
            flash(f'Successfully imported {imported} shed record(s)', 'success')
        else:
            flash('Invalid data type', 'error')
            return redirect(url_for('import_page'))
        
        # Show errors if any
        if errors:
            for error in errors[:10]:  # Show first 10 errors
                flash(error, 'warning')
            if len(errors) > 10:
                flash(f'... and {len(errors) - 10} more errors', 'warning')
        
        return redirect(url_for('import_page'))
        
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('import_page'))

# ==================== HELP & GUIDE SYSTEM ====================
@app.route('/records')
@login_required
@household_required
def records_page():
    """Records hub page with feeding and shed records"""
    db = get_db()
    
    # Get stats
    stats = db.get_dashboard_stats()
    
    # Get recent activity filtered by household
    recent_feedings = db.get_all_feeding_logs(limit=5, household_id=current_user.household_id)
    recent_sheds = db.get_shed_records(limit=5, household_id=current_user.household_id)
    
    return render_template('records.html',
                         stats=stats,
                         recent_feedings=recent_feedings,
                         recent_sheds=recent_sheds)

@app.route('/settings')
@login_required
def settings_page():
    """Settings page with data management options"""
    return render_template('settings.html')


@app.route('/settings/notifications', methods=['GET', 'POST'])
def notification_settings():
    """Notification settings page for email and SMS alerts"""
    db = get_db()
    
    if request.method == 'POST':
        try:
            settings = {
                'email_enabled': request.form.get('email_enabled') == 'on',
                'email': request.form.get('email'),
                'sms_enabled': request.form.get('sms_enabled') == 'on',
                'phone': request.form.get('phone'),
                'reminder_time': request.form.get('reminder_time', '09:00'),
                'notify_overdue_only': request.form.get('notify_overdue_only') == 'on'
            }
            
            db.save_notification_settings(**settings)
            flash('Notification settings saved successfully!', 'success')
            return redirect(url_for('notification_settings'))
        except Exception as e:
            print(f"[ERROR] Failed to save notification settings: {e}")
            flash(f'Error saving settings: {str(e)}', 'error')
    
    # Get current settings or use defaults
    try:
        settings = db.get_notification_settings()
        if not settings:
            # Provide default settings if none exist
            settings = {
                'email_enabled': False,
                'email': '',
                'sms_enabled': False,
                'phone': '',
                'reminder_time': '09:00',
                'notify_overdue_only': False
            }
    except Exception as e:
        print(f"[ERROR] Failed to get notification settings: {e}")
        # Provide default settings on error
        settings = {
            'email_enabled': False,
            'email': '',
            'sms_enabled': False,
            'phone': '',
            'reminder_time': '09:00',
            'notify_overdue_only': False
        }
        flash('Using default settings. Save to create your notification preferences.', 'info')
    
    return render_template('notification_settings.html', settings=settings)

@app.route('/api/send-test-notification', methods=['POST'])
@login_required
def send_test_notification():
    """Send a test notification to verify settings"""
    try:
        notification_type = request.json.get('type', 'push')
        
        if notification_type == 'push':
            # Send test push notification
            from notifications import send_push_notification
            
            db = get_db()
            subscriptions = db.get_push_subscriptions(user_id=current_user.id)
            
            if not subscriptions:
                return jsonify({
                    'success': False,
                    'message': 'No push subscriptions found. Please enable notifications in your browser.'
                }), 400
            
            success_count = 0
            for sub in subscriptions:
                try:
                    send_push_notification(
                        sub,
                        'Test Notification',
                        'This is a test notification from Reptile Tracker! 🦎'
                    )
                    success_count += 1
                except Exception as e:
                    print(f"Failed to send to subscription {sub.get('id')}: {e}")
            
            if success_count > 0:
                return jsonify({
                    'success': True,
                    'message': f'Test notification sent to {success_count} device(s)!'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to send test notification. Please check your subscription.'
                }), 500
                
        elif notification_type == 'email':
            return jsonify({
                'success': False,
                'message': 'Email notifications are not yet implemented.'
            }), 501
            
        elif notification_type == 'sms':
            return jsonify({
                'success': False,
                'message': 'SMS notifications are not yet implemented.'
            }), 501
        
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid notification type.'
            }), 400
            
    except Exception as e:
        print(f"Error sending test notification: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/help')
def help_page():
    """Interactive help and guide system"""
    return render_template('help.html')

@app.route('/api/dismiss-tutorial', methods=['POST'])
def dismiss_tutorial():
    """API endpoint to dismiss tutorial overlay"""
    tutorial_id = request.json.get('tutorial_id')
    # Store in cookie that tutorial has been dismissed
    response = make_response(jsonify({'success': True}))
    response.set_cookie(f'tutorial_dismissed_{tutorial_id}', 'true', max_age=365*24*60*60)  # 1 year
    return response


if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5001)

# Made with Bob


# ==================== WEIGHT TRACKING ROUTES ====================

@app.route('/reptile/<int:reptile_id>/weight')
def weight_tracking(reptile_id):
    """Weight tracking page with graphs"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        flash('Reptile not found', 'error')
        return redirect(url_for('index'))
    
    weight_history = db.get_weight_history(reptile_id)
    chart_data = db.get_weight_chart_data(reptile_id)
    
    return render_template('weight_tracking.html', 
                         reptile=reptile,
                         weight_history=weight_history,
                         chart_data=chart_data)

@app.route('/reptile/<int:reptile_id>/weight/add', methods=['POST'])
def add_weight(reptile_id):
    """Add weight measurement"""
    db = get_db()
    try:
        data = {
            'reptile_id': reptile_id,
            'measurement_date': request.form.get('measurement_date'),
            'weight_grams': float(request.form.get('weight_grams')),
            'notes': request.form.get('notes') or None,
            'created_by': current_user.id
        }
        db.add_weight_measurement(**data)
        
        # Also update the reptile's current weight
        db.update_reptile(reptile_id, weight_grams=data['weight_grams'])
        
        flash('Weight measurement added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding weight: {str(e)}', 'error')
    
    return redirect(url_for('weight_tracking', reptile_id=reptile_id))

@app.route('/weight/chart-data/<int:reptile_id>')
def weight_chart_data(reptile_id):
    """API endpoint for chart data"""
    db = get_db()
    data = db.get_weight_chart_data(reptile_id)
    return jsonify(data)


# ==================== LENGTH TRACKING ROUTES ====================

@app.route('/reptile/<int:reptile_id>/length')
def length_tracking(reptile_id):
    """Length tracking page with graphs"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        flash('Reptile not found', 'error')
        return redirect(url_for('index'))
    
    length_history = db.get_length_history(reptile_id)
    chart_data = db.get_length_chart_data(reptile_id)
    
    return render_template('length_tracking.html', 
                         reptile=reptile,
                         length_history=length_history,
                         chart_data=chart_data)

@app.route('/reptile/<int:reptile_id>/length/add', methods=['POST'])
def add_length(reptile_id):
    """Add length measurement"""
    db = get_db()
    try:
        data = {
            'reptile_id': reptile_id,
            'measurement_date': request.form.get('measurement_date'),
            'length_cm': float(request.form.get('length_cm')),
            'notes': request.form.get('notes') or None,
            'created_by': current_user.id
        }
        db.add_length_measurement(**data)
        
        # Also update the reptile's current length
        db.update_reptile(reptile_id, length_cm=data['length_cm'])
        
        flash('Length measurement added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding length: {str(e)}', 'error')
    

# ==================== PHOTO GALLERY ROUTES ====================

@app.route('/reptile/<int:reptile_id>/photos')
def photo_gallery(reptile_id):
    """Display photo gallery for a reptile"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        flash('Reptile not found', 'error')
        return redirect(url_for('dashboard'))
    
    photos = db.get_photos(reptile_id)
    
    return render_template('photo_gallery.html',
                         reptile=reptile,
                         photos=photos)

@app.route('/reptile/<int:reptile_id>/photos/upload', methods=['POST'])
def upload_photo(reptile_id):
    """Upload a new photo for a reptile"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        flash('Reptile not found', 'error')
        return redirect(url_for('dashboard'))
    
    if 'photo' not in request.files:
        flash('No photo file provided', 'error')
        return redirect(url_for('photo_gallery', reptile_id=reptile_id))
    
    file = request.files['photo']
    if file.filename == '':
        flash('No photo selected', 'error')
        return redirect(url_for('photo_gallery', reptile_id=reptile_id))
    
    if file and allowed_file(file.filename):
        try:
            # Create uploads directory if it doesn't exist
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            # Generate unique filename
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{reptile_id}_{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save file
            file.save(filepath)
            
            # Get caption from form
            caption = request.form.get('caption', '')
            is_primary = request.form.get('is_primary') == 'on'
            
            # Add to database
            db.add_photo(reptile_id, filename, caption, is_primary)
            
            flash('Photo uploaded successfully!', 'success')
        except Exception as e:
            flash(f'Error uploading photo: {str(e)}', 'error')
    else:
        flash('Invalid file type. Allowed types: png, jpg, jpeg, gif', 'error')
    
    return redirect(url_for('photo_gallery', reptile_id=reptile_id))

@app.route('/reptile/<int:reptile_id>/photos/<int:photo_id>/set-primary', methods=['POST'])
def set_primary_photo(reptile_id, photo_id):
    """Set a photo as the primary photo"""
    db = get_db()
    try:
        db.set_primary_photo(photo_id, reptile_id)
        flash('Primary photo updated!', 'success')
    except Exception as e:
        flash(f'Error setting primary photo: {str(e)}', 'error')
    
    return redirect(url_for('photo_gallery', reptile_id=reptile_id))

@app.route('/reptile/<int:reptile_id>/photos/<int:photo_id>/delete', methods=['POST'])
def delete_photo(reptile_id, photo_id):
    """Delete a photo"""
    db = get_db()
    try:
        # Get photo info before deleting
        photos = db.get_photos(reptile_id)
        photo = next((p for p in photos if p['id'] == photo_id), None)
        
        if photo:
            # Delete from database
            db.delete_photo(photo_id)
            
            # Delete file from filesystem
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], photo['image_path'])
            if os.path.exists(filepath):
                os.remove(filepath)
            
            flash('Photo deleted successfully!', 'success')
        else:
            flash('Photo not found', 'error')
    except Exception as e:
        flash(f'Error deleting photo: {str(e)}', 'error')
    
    return redirect(url_for('photo_gallery', reptile_id=reptile_id))
# ==================== FEEDING REMINDER ROUTES ====================

@app.route('/feeding-reminders')
def feeding_reminders():
    """Display all feeding reminders and overdue feedings"""
    db = get_db()
    all_reminders = db.get_feeding_reminders()
    overdue = db.get_overdue_feedings()
    
    return render_template('feeding_reminders.html',
                         reminders=all_reminders,
                         overdue=overdue)

@app.route('/reptile/<int:reptile_id>/feeding-reminder/set', methods=['GET', 'POST'])
def set_feeding_reminder(reptile_id):
    """Set or update feeding reminder for a reptile"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        flash('Reptile not found', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            feeding_interval_days = int(request.form.get('feeding_interval_days'))
            
            if feeding_interval_days < 1:
                flash('Feeding interval must be at least 1 day', 'error')
                return redirect(url_for('set_feeding_reminder', reptile_id=reptile_id))
            
            db.add_feeding_reminder(reptile_id, feeding_interval_days)
            
            # Update dates if there's a recent feeding
            recent_feeding = db.get_feeding_logs(reptile_id, limit=1)
            if recent_feeding:
                db.update_feeding_reminder_dates(reptile_id, recent_feeding[0]['feeding_date'])
            
            flash(f'Feeding reminder set to every {feeding_interval_days} days', 'success')
            return redirect(url_for('reptile_details', reptile_id=reptile_id))
        except Exception as e:
            flash(f'Error setting reminder: {str(e)}', 'error')
    
    # Get existing reminder if any
    existing_reminders = db.get_feeding_reminders(reptile_id)
    existing_reminder = existing_reminders[0] if existing_reminders else None
    
    return render_template('set_feeding_reminder.html',
                         reptile=reptile,
                         existing_reminder=existing_reminder)

@app.route('/reptile/<int:reptile_id>/upgrade-food', methods=['GET', 'POST'])
def upgrade_food(reptile_id):
    """Upgrade food type/size for a reptile"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        flash('Reptile not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Standard food options
    food_types = ['Rat', 'Mouse', 'Rabbit', 'Cricket', 'Dubia Roach', 'Quail']
    food_sizes = ['Pinkie', 'Fuzzie', 'Hopper', 'Weaner', 'Juvenile', 'Small', 'Adult', 'Medium', 'Large', 'X Large', 'Jumbo']
    
    if request.method == 'POST':
        try:
            food_type = request.form.get('food_type')
            food_size = request.form.get('food_size')
            quantity_per_feeding = int(request.form.get('quantity_per_feeding', 1))
            
            if not food_type or not food_size:
                flash('Please select both food type and size', 'error')
                return redirect(url_for('upgrade_food', reptile_id=reptile_id))
            
            if quantity_per_feeding < 1:
                flash('Quantity must be at least 1', 'error')
                return redirect(url_for('upgrade_food', reptile_id=reptile_id))
            
            # Upgrade the food
            success = db.upgrade_reptile_food(reptile_id, food_type, food_size, quantity_per_feeding)
            
            if success:
                flash(f'Successfully upgraded {reptile["name"]} to {food_size} {food_type}!', 'success')
                return redirect(url_for('reptile_details', reptile_id=reptile_id))
            else:
                flash('No feeding reminder found. Please set up a feeding reminder first.', 'warning')
                return redirect(url_for('set_feeding_reminder', reptile_id=reptile_id))
                
        except Exception as e:
            flash(f'Error upgrading food: {str(e)}', 'error')
    
    # Get current food preference
    current_food = db.get_reptile_food_preference(reptile_id)
    
    # Get recent feeding history
    recent_feedings = db.get_feeding_logs(reptile_id, limit=10)
    
    return render_template('upgrade_food.html',
                         reptile=reptile,
                         current_food=current_food,
                         recent_feedings=recent_feedings,
                         food_types=food_types,
                         food_sizes=food_sizes)

@app.route('/reptile/<int:reptile_id>/feeding-reminder/disable', methods=['POST'])
def disable_feeding_reminder(reptile_id):
    """Disable feeding reminder for a reptile"""
    db = get_db()
    try:
        db.cursor.execute('''
            UPDATE feeding_reminders 
            SET is_active = 0 
            WHERE reptile_id = ?
        ''', (reptile_id,))
        db.conn.commit()
        flash('Feeding reminder disabled', 'success')
    except Exception as e:
        flash(f'Error disabling reminder: {str(e)}', 'error')
    
    return redirect(url_for('reptile_details', reptile_id=reptile_id))

# ==================== EXPENSE TRACKING ROUTES ====================

@app.route('/expenses')
def expenses_list():
    """Redirect to finance page with expenses tab"""
    # Preserve query parameters
    args = request.args.to_dict()
    args['tab'] = 'expenses'
    return redirect(url_for('finance', **args))

@app.route('/expense/add', methods=['GET', 'POST'])
def add_expense():
    """Add new expense"""
    db = get_db()
    
    if request.method == 'POST':
        try:
            # Handle receipt upload
            receipt_path = None
            if 'receipt' in request.files:
                file = request.files['receipt']
                if file and file.filename:
                    # Check file type
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'pdf'}
                    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                    
                    if ext in allowed_extensions:
                        filename = secure_filename(file.filename)
                        # Add timestamp to filename
                        name, extension = os.path.splitext(filename)
                        filename = f"receipt_{int(datetime.now().timestamp())}_{name}{extension}"
                        
                        # Create receipts directory if it doesn't exist
                        receipts_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'receipts')
                        os.makedirs(receipts_dir, exist_ok=True)
                        
                        filepath = os.path.join(receipts_dir, filename)
                        file.save(filepath)
                        receipt_path = f"receipts/{filename}"
            
            # Get form data
            reptile_id = request.form.get('reptile_id')
            reptile_id = int(reptile_id) if reptile_id else None
            
            expense_id = db.add_expense(
                expense_date=request.form.get('expense_date'),
                category=request.form.get('category'),
                amount=float(request.form.get('amount')),
                reptile_id=reptile_id,
                currency=request.form.get('currency', 'USD'),
                vendor=request.form.get('vendor') or None,
                description=request.form.get('description') or None,
                receipt_path=receipt_path,
                payment_method=request.form.get('payment_method') or None,
                is_recurring=bool(request.form.get('is_recurring')),
                tags=request.form.get('tags') or None,
                notes=request.form.get('notes') or None
            )
            
            flash('Expense added successfully!', 'success')
            return redirect(url_for('expenses_list'))
        except Exception as e:
            flash(f'Error adding expense: {str(e)}', 'error')
    
    # Get all reptiles for dropdown
    reptiles = db.get_all_reptiles()
    
    # Pre-defined categories
    categories = [
        'Food & Feeders',
        'Supplements & Vitamins',
        'Veterinary Care',
        'Medications',
        'Enclosure & Habitat',
        'Heating & Lighting',
        'Substrate & Bedding',
        'Décor & Enrichment',
        'Cleaning Supplies',
        'Equipment & Tools',
        'Breeding Supplies',
        'Other'
    ]
    
    return render_template('add_expense.html',
                         reptiles=reptiles,
                         categories=categories)

@app.route('/expense/<int:expense_id>')
def expense_details(expense_id):
    """View expense details"""
    db = get_db()
    expense = db.get_expense(expense_id)
    
    if not expense:
        flash('Expense not found', 'error')
        return redirect(url_for('expenses_list'))
    
    return render_template('expense_details.html', expense=expense)

@app.route('/expense/<int:expense_id>/edit', methods=['GET', 'POST'])
def edit_expense(expense_id):
    """Edit expense"""
    db = get_db()
    expense = db.get_expense(expense_id)
    
    if not expense:
        flash('Expense not found', 'error')
        return redirect(url_for('expenses_list'))
    
    if request.method == 'POST':
        try:
            # Handle receipt upload
            receipt_path = expense['receipt_path']
            if 'receipt' in request.files:
                file = request.files['receipt']
                if file and file.filename:
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'pdf'}
                    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                    
                    if ext in allowed_extensions:
                        # Delete old receipt if exists
                        if receipt_path:
                            old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], receipt_path)
                            if os.path.exists(old_filepath):
                                os.remove(old_filepath)
                        
                        filename = secure_filename(file.filename)
                        name, extension = os.path.splitext(filename)
                        filename = f"receipt_{int(datetime.now().timestamp())}_{name}{extension}"
                        
                        receipts_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'receipts')
                        os.makedirs(receipts_dir, exist_ok=True)
                        
                        filepath = os.path.join(receipts_dir, filename)
                        file.save(filepath)
                        receipt_path = f"receipts/{filename}"
            
            # Update expense
            reptile_id = request.form.get('reptile_id')
            reptile_id = int(reptile_id) if reptile_id else None
            
            db.update_expense(
                expense_id,
                expense_date=request.form.get('expense_date'),
                category=request.form.get('category'),
                amount=float(request.form.get('amount')),
                reptile_id=reptile_id,
                currency=request.form.get('currency', 'USD'),
                vendor=request.form.get('vendor') or None,
                description=request.form.get('description') or None,
                receipt_path=receipt_path,
                payment_method=request.form.get('payment_method') or None,
                is_recurring=bool(request.form.get('is_recurring')),
                tags=request.form.get('tags') or None,
                notes=request.form.get('notes') or None
            )
            
            flash('Expense updated successfully!', 'success')
            return redirect(url_for('expense_details', expense_id=expense_id))
        except Exception as e:
            flash(f'Error updating expense: {str(e)}', 'error')
    
    reptiles = db.get_all_reptiles()
    categories = [
        'Food & Feeders', 'Supplements & Vitamins', 'Veterinary Care',
        'Medications', 'Enclosure & Habitat', 'Heating & Lighting',
        'Substrate & Bedding', 'Décor & Enrichment', 'Cleaning Supplies',
        'Equipment & Tools', 'Breeding Supplies', 'Other'
    ]
    
    return render_template('edit_expense.html',
                         expense=expense,
                         reptiles=reptiles,
                         categories=categories)

@app.route('/expense/<int:expense_id>/delete', methods=['POST'])
def delete_expense(expense_id):
    """Delete expense"""
    db = get_db()
    
    try:
        # Get expense to delete receipt file
        expense = db.get_expense(expense_id)
        if expense and expense['receipt_path']:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], expense['receipt_path'])
            if os.path.exists(filepath):
                os.remove(filepath)
        
        db.delete_expense(expense_id)
        flash('Expense deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting expense: {str(e)}', 'error')
    
    return redirect(url_for('expenses_list'))

@app.route('/expenses/reports')
def expense_reports():
    """Expense analytics and reports"""
    db = get_db()
    
    # Get date range from query params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    reptile_id = request.args.get('reptile_id', type=int)
    
    # Get summary statistics
    summary = db.get_expense_summary(start_date, end_date, reptile_id)
    
    # Get expenses by category
    by_category = db.get_expenses_by_category(start_date, end_date, reptile_id)
    
    # Get monthly expenses
    year = int(request.args.get('year', datetime.now().year))
    monthly = db.get_monthly_expenses(year, reptile_id)
    
    # Get all reptiles for filter
    reptiles = db.get_all_reptiles()
    if reptiles is None:
        reptiles = []
    
    return render_template('expense_reports.html',
                         summary=summary,
                         by_category=by_category,
                         monthly=monthly,
                         reptiles=reptiles,
                         selected_reptile=reptile_id,
                         selected_year=year,
                         start_date=start_date,
                         end_date=end_date)

# ==================== FOOD INVENTORY ROUTES ====================

@app.route('/finance')
def finance():
    """Unified Finance page - Inventory & Expenses combined"""
    db = get_db()
    
    # Get active tab from query parameter (default: inventory)
    active_tab = request.args.get('tab', 'inventory')
    
    # === INVENTORY DATA ===
    days_ahead = request.args.get('days', 30, type=int)
    inventory = db.get_food_inventory(include_zero=True)
    low_stock = db.get_low_stock_items(threshold=5)
    out_of_stock = db.get_out_of_stock_items()
    forecasts = db.get_inventory_forecast(days_lookback=30)
    forecast_dict = {f['inventory_id']: f for f in forecasts}
    shopping_list_data = db.get_shopping_list(days_ahead=days_ahead)
    
    # Calculate inventory value
    total_inventory_value = sum(
        (item['quantity'] * item.get('cost_per_unit', 0))
        for item in inventory if item.get('cost_per_unit')
    )
    
    # === EXPENSES DATA ===
    reptile_id = request.args.get('reptile_id', type=int)
    category = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    expenses = db.get_expenses(
        reptile_id=reptile_id,
        category=category,
        start_date=start_date,
        end_date=end_date
    )
    
    expense_summary = db.get_expense_summary(
        start_date=start_date,
        end_date=end_date,
        reptile_id=reptile_id
    )
    
    reptiles = db.get_all_reptiles()
    if reptiles is None:
        reptiles = []
    categories = db.get_expense_categories()
    
    # Calculate monthly expenses (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    recent_receipts = db.get_purchase_receipts()
    monthly_expenses = sum(
        receipt.get('total_cost', 0)
        for receipt in recent_receipts
        if receipt.get('receipt_date', '') >= thirty_days_ago
    )
    
    return render_template('finance.html',
                         active_tab=active_tab,
                         # Inventory data
                         inventory=inventory,
                         low_stock=low_stock,
                         out_of_stock=out_of_stock,
                         forecasts=forecast_dict,
                         shopping_list=shopping_list_data,
                         days_ahead=days_ahead,
                         total_inventory_value=total_inventory_value,
                         inventory_count=len(inventory),
                         # Expenses data
                         expenses=expenses,
                         expense_summary=expense_summary,
                         reptiles=reptiles,
                         expense_categories=categories,
                         selected_reptile=reptile_id,
                         selected_category=category,
                         start_date=start_date,
                         end_date=end_date,
                         monthly_expenses=monthly_expenses)

@app.route('/inventory')
def food_inventory():
    """Redirect to finance page with inventory tab"""
    return redirect(url_for('finance', tab='inventory'))

@app.route('/shopping-list')
def shopping_list():
    """Display shopping list based on feeding schedules"""
    db = get_db()
    
    # Get days ahead parameter (default 30)
    days_ahead = request.args.get('days', 30, type=int)
    
    # Get shopping list
    shopping_list_data = db.get_shopping_list(days_ahead=days_ahead)
    
    return render_template('shopping_list.html',
                         shopping_list=shopping_list_data,
                         days_ahead=days_ahead)

@app.route('/inventory/add', methods=['GET', 'POST'])
def add_inventory_item():
    """Add or update food inventory"""
    db = get_db()
    
    if request.method == 'POST':
        try:
            food_type = request.form.get('food_type')
            food_size = request.form.get('food_size')
            quantity = int(request.form.get('quantity'))
            
            # Check if item already exists
            existing = db.get_food_item_by_type(food_type, food_size)
            
            if existing:
                # Update existing item
                db.update_food_quantity(
                    existing['id'],
                    quantity,
                    transaction_type='purchase',
                    notes=f'Added {quantity} items'
                )
                flash(f'Added {quantity} to existing stock', 'success')
            else:
                # Add new item
                cost_per_unit = request.form.get('cost_per_unit')
                cost_per_unit = float(cost_per_unit) if cost_per_unit else None
                
                db.add_food_item(
                    food_type=food_type,
                    food_size=food_size,
                    quantity=quantity,
                    unit=request.form.get('unit', 'items'),
                    cost_per_unit=cost_per_unit,
                    supplier=request.form.get('supplier') or None,
                    purchase_date=request.form.get('purchase_date') or None,
                    expiry_date=request.form.get('expiry_date') or None,
                    notes=request.form.get('notes') or None
                )
                flash('Food item added to inventory!', 'success')
            
            return redirect(url_for('food_inventory'))
        except Exception as e:
            flash(f'Error adding inventory: {str(e)}', 'error')
    
    # Get food types and sizes (includes standard options from supplier)
    food_types = db.get_distinct_food_types()
    food_sizes = db.get_distinct_food_sizes()
    
    return render_template('add_inventory_item.html',
                         food_types=food_types,
                         food_sizes=food_sizes)
@app.route('/inventory/add-bulk', methods=['GET', 'POST'])
def add_inventory_bulk():
    """Add multiple inventory items at once with expense tracking"""
    db = get_db()
    
    if request.method == 'POST':
        try:
            # Get common purchase info
            purchase_date = request.form.get('purchase_date')
            supplier = request.form.get('supplier')
            payment_method = request.form.get('payment_method')
            notes = request.form.get('notes')
            
            # Parse all items from form data
            items = []
            item_index = 0
            total_cost = 0
            
            while True:
                food_type = request.form.get(f'food_type_{item_index}')
                if not food_type:
                    break
                
                food_size = request.form.get(f'food_size_{item_index}')
                quantity = int(request.form.get(f'quantity_{item_index}', 1))
                unit = request.form.get(f'unit_{item_index}', 'items')
                cost_per_unit = request.form.get(f'cost_per_unit_{item_index}')
                expiry_date = request.form.get(f'expiry_date_{item_index}')
                
                cost_per_unit = float(cost_per_unit) if cost_per_unit else None
                item_total = (quantity * cost_per_unit) if cost_per_unit else 0
                total_cost += item_total
                
                items.append({
                    'food_type': food_type,
                    'food_size': food_size,
                    'quantity': quantity,
                    'unit': unit,
                    'cost_per_unit': cost_per_unit,
                    'expiry_date': expiry_date or None,
                    'item_total': item_total
                })
                
                item_index += 1
            
            if not items:
                flash('Please add at least one item', 'error')
                return redirect(url_for('add_inventory_bulk'))
            
            # Add all items to inventory
            for item in items:
                # Check if item already exists
                existing_item = db.get_food_item_by_type_size(item['food_type'], item['food_size'])
                
                if existing_item:
                    # Update existing item
                    new_quantity = existing_item['quantity'] + item['quantity']
                    db.update_food_quantity(
                        existing_item['id'],
                        new_quantity,
                        notes=f"Bulk purchase: Added {item['quantity']} {item['unit']}"
                    )
                else:
                    # Add new item
                    db.add_food_item(
                        food_type=item['food_type'],
                        food_size=item['food_size'],
                        quantity=item['quantity'],
                        unit=item['unit'],
                        cost_per_unit=item['cost_per_unit'],
                        supplier=supplier,
                        purchase_date=purchase_date,
                        expiry_date=item['expiry_date'],
                        notes=notes
                    )
            
            # Create a purchase receipt record if there's cost info
            if total_cost > 0:
                receipt_items = [
                    {
                        'food_type': item['food_type'],
                        'food_size': item['food_size'],
                        'quantity': item['quantity'],
                        'cost_per_unit': item['cost_per_unit'],
                        'total_cost': item['item_total']
                    }
                    for item in items if item['cost_per_unit']
                ]
                
                if receipt_items:
                    db.add_purchase_receipt(
                        receipt_date=purchase_date or datetime.now().strftime('%Y-%m-%d'),
                        items=receipt_items,
                        supplier=supplier,
                        total_cost=total_cost,
                        payment_method=payment_method,
                        notes=notes
                    )
            
            flash(f'Successfully added {len(items)} item(s) to inventory!', 'success')
            if total_cost > 0:
                flash(f'Total expense tracked: ${total_cost:.2f}', 'info')
            
            return redirect(url_for('food_inventory'))
            
        except Exception as e:
            flash(f'Error adding items: {str(e)}', 'error')
            return redirect(url_for('add_inventory_bulk'))
    
    # GET request - show form
    food_types = db.get_distinct_food_types()
    food_sizes = db.get_distinct_food_sizes()
    
    return render_template('add_inventory_bulk.html',
                         food_types=food_types,
                         food_sizes=food_sizes)


@app.route('/inventory/<int:inventory_id>')
def inventory_item_details(inventory_id):
    """View inventory item details"""
    db = get_db()
    
    item = db.get_food_item(inventory_id)
    if not item:
        flash('Inventory item not found', 'error')
        return redirect(url_for('food_inventory'))
    
    # Get transaction history
    transactions = db.get_inventory_transactions(inventory_id, limit=50)
    
    return render_template('inventory_item_details.html',
                         item=item,
                         transactions=transactions)

@app.route('/inventory/<int:inventory_id>/adjust', methods=['POST'])
def adjust_inventory(inventory_id):
    """Adjust inventory quantity"""
    db = get_db()
    
    try:
        quantity_change = int(request.form.get('quantity_change'))
        notes = request.form.get('notes', 'Manual adjustment')
        
        db.update_food_quantity(
            inventory_id,
            quantity_change,
            transaction_type='adjustment',
            notes=notes
        )
        
        flash('Inventory adjusted successfully!', 'success')
    except Exception as e:
        flash(f'Error adjusting inventory: {str(e)}', 'error')
    
    return redirect(url_for('inventory_item_details', inventory_id=inventory_id))

@app.route('/inventory/<int:inventory_id>/delete', methods=['POST'])
def delete_inventory_item(inventory_id):
    """Delete inventory item"""
    db = get_db()
    
    try:
        db.delete_food_item(inventory_id)
        flash('Inventory item deleted!', 'success')
    except Exception as e:
        flash(f'Error deleting item: {str(e)}', 'error')
    
    return redirect(url_for('food_inventory'))

@app.route('/inventory/transactions')
def inventory_transactions():
    """View all inventory transactions"""
    db = get_db()
    
    # Get filter parameters
    inventory_id = request.args.get('inventory_id', type=int)
    limit = request.args.get('limit', 100, type=int)
    
    transactions = db.get_inventory_transactions(inventory_id, limit)
    
    # Get all inventory items for filter
    inventory = db.get_food_inventory(include_zero=True)
    
    return render_template('inventory_transactions.html',
                         transactions=transactions,
                         inventory=inventory,
                         selected_item=inventory_id)

# ==================== PURCHASE RECEIPT ROUTES ====================

@app.route('/inventory/receipt/scan', methods=['GET', 'POST'])
def scan_receipt():
    """Scan a receipt image using OCR"""
    from receipt_ocr import ReceiptOCR
    import os
    
    db = get_db()
    
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'receipt_image' not in request.files:
                flash('No file uploaded', 'error')
                return redirect(url_for('scan_receipt'))
            
            file = request.files['receipt_image']
            
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(url_for('scan_receipt'))
            
            if file:
                # Save uploaded file
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"receipt_{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'receipts', filename)
                
                # Create receipts directory if it doesn't exist
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                file.save(filepath)
                
                # Process with OCR
                try:
                    ocr = ReceiptOCR()
                    result = ocr.process_receipt_image(filepath)
                    
                    if not result.get('success'):
                        error_msg = result.get('error', 'Unknown error')
                        print(f"OCR Error: {error_msg}")
                        # Proceed anyway with empty data - user can enter manually
                        result = {
                            'success': True,
                            'supplier': None,
                            'date': None,
                            'total': None,
                            'items': [],
                            'raw_text': f'OCR failed: {error_msg}'
                        }
                    
                    # Check if any text was extracted
                    raw_text = result.get('raw_text', '').strip()
                    if not raw_text or len(raw_text) < 5:
                        print("OCR extracted insufficient text")
                        # Proceed anyway - user can enter manually
                        raw_text = 'No text extracted by OCR'
                        result['items'] = []
                    
                    # Store parsed data in session for review
                    session['scanned_receipt'] = {
                        'image_path': filename,
                        'supplier': result.get('supplier'),
                        'date': result.get('date'),
                        'total': result.get('total'),
                        'items': result.get('items', []),
                        'raw_text': raw_text
                    }
                    
                    items_found = len(result.get("items", []))
                    if items_found > 0:
                        flash(f'Receipt scanned! Found {items_found} items. Please review and edit before saving.', 'success')
                    else:
                        flash('Receipt image saved. OCR could not detect items automatically - please add them manually below.', 'warning')
                    
                    return redirect(url_for('review_scanned_receipt'))
                    
                except Exception as e:
                    print(f"OCR Exception: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    # Still proceed - let user enter manually
                    session['scanned_receipt'] = {
                        'image_path': filename,
                        'supplier': None,
                        'date': None,
                        'total': None,
                        'items': [],
                        'raw_text': f'OCR error: {str(e)}'
                    }
                    flash('Receipt image saved. Please add items manually (OCR unavailable).', 'warning')
                    return redirect(url_for('review_scanned_receipt'))
                
        except Exception as e:
            flash(f'Error scanning receipt: {str(e)}', 'error')
            import traceback
            print(traceback.format_exc())
    
    return render_template('scan_receipt.html')

@app.route('/inventory/receipt/review', methods=['GET', 'POST'])
def review_scanned_receipt():
    """Review and edit scanned receipt data before saving"""
    db = get_db()
    
    # Get scanned data from session
    scanned_data = session.get('scanned_receipt')
    if not scanned_data:
        flash('No scanned receipt data found', 'error')
        return redirect(url_for('scan_receipt'))
    
    if request.method == 'POST':
        try:
            # Get edited receipt data
            receipt_date = request.form.get('receipt_date')
            supplier = request.form.get('supplier') or None
            payment_method = request.form.get('payment_method') or None
            notes = request.form.get('notes') or None
            
            # Get items from form
            items = []
            item_count = int(request.form.get('item_count', 0))
            
            for i in range(item_count):
                food_type = request.form.get(f'food_type_{i}')
                food_size = request.form.get(f'food_size_{i}')
                quantity = request.form.get(f'quantity_{i}')
                cost_per_unit = request.form.get(f'cost_per_unit_{i}')
                
                if food_type and food_size and quantity:
                    items.append({
                        'food_type': food_type,
                        'food_size': food_size,
                        'quantity': int(quantity),
                        'cost_per_unit': float(cost_per_unit) if cost_per_unit else 0
                    })
            
            if not items:
                flash('Please add at least one item to the receipt', 'error')
                return redirect(url_for('review_scanned_receipt'))
            
            # Add receipt with image path and OCR text
            receipt_id = db.add_purchase_receipt(
                receipt_date=receipt_date,
                items=items,
                supplier=supplier,
                payment_method=payment_method,
                notes=notes,
                image_path=scanned_data.get('image_path'),
                ocr_text=scanned_data.get('raw_text')
            )
            
            # Clear session data
            session.pop('scanned_receipt', None)
            
            flash(f'Receipt saved successfully! {len(items)} items added to inventory.', 'success')
            return redirect(url_for('view_purchase_receipt', receipt_id=receipt_id))
            
        except Exception as e:
            flash(f'Error saving receipt: {str(e)}', 'error')
    
    # Get existing food types and sizes for suggestions
    existing_inventory = db.get_food_inventory(include_zero=True)
    food_types = sorted(list(set([item['food_type'] for item in existing_inventory])))
    food_sizes = sorted(list(set([item['food_size'] for item in existing_inventory])))
    
    return render_template('review_scanned_receipt.html',
                         scanned_data=scanned_data,
                         food_types=food_types,
                         food_sizes=food_sizes)

@app.route('/inventory/receipt/add', methods=['GET', 'POST'])
def add_purchase_receipt():
    """Add a purchase receipt with multiple items"""
    db = get_db()
    
    if request.method == 'POST':
        try:
            # Get receipt data
            receipt_date = request.form.get('receipt_date')
            supplier = request.form.get('supplier') or None
            payment_method = request.form.get('payment_method') or None
            notes = request.form.get('notes') or None
            
            # Get items from form (dynamic fields)
            items = []
            item_count = int(request.form.get('item_count', 0))
            
            for i in range(item_count):
                food_type = request.form.get(f'food_type_{i}')
                food_size = request.form.get(f'food_size_{i}')
                quantity = request.form.get(f'quantity_{i}')
                cost_per_unit = request.form.get(f'cost_per_unit_{i}')
                
                if food_type and food_size and quantity:
                    items.append({
                        'food_type': food_type,
                        'food_size': food_size,
                        'quantity': int(quantity),
                        'cost_per_unit': float(cost_per_unit) if cost_per_unit else 0
                    })
            
            if not items:
                flash('Please add at least one item to the receipt', 'error')
                return redirect(url_for('add_purchase_receipt'))
            
            # Add receipt and update inventory
            receipt_id = db.add_purchase_receipt(
                receipt_date=receipt_date,
                items=items,
                supplier=supplier,
                payment_method=payment_method,
                notes=notes
            )
            
            flash(f'Receipt added successfully! {len(items)} items added to inventory.', 'success')
            return redirect(url_for('view_purchase_receipt', receipt_id=receipt_id))
            
        except Exception as e:
            flash(f'Error adding receipt: {str(e)}', 'error')
    
    # Get existing food types and sizes for suggestions
    existing_inventory = db.get_food_inventory(include_zero=True)
    food_types = sorted(list(set([item['food_type'] for item in existing_inventory])))
    food_sizes = sorted(list(set([item['food_size'] for item in existing_inventory])))
    
    return render_template('add_purchase_receipt.html',
                         food_types=food_types,
                         food_sizes=food_sizes)

@app.route('/inventory/receipts')
def purchase_receipts():
    """View all purchase receipts"""
    db = get_db()
    receipts = db.get_purchase_receipts(limit=100)
    return render_template('purchase_receipts.html', receipts=receipts)

@app.route('/inventory/receipt/<int:receipt_id>')
def view_purchase_receipt(receipt_id):
    """View a single purchase receipt"""
    db = get_db()
    receipt = db.get_purchase_receipt(receipt_id)
    
    if not receipt:
        flash('Receipt not found', 'error')
        return redirect(url_for('purchase_receipts'))
    
    return render_template('view_purchase_receipt.html', receipt=receipt)

@app.route('/inventory/receipt/<int:receipt_id>/delete', methods=['POST'])
def delete_purchase_receipt(receipt_id):
    """Delete a purchase receipt"""
    db = get_db()
    if db.delete_purchase_receipt(receipt_id):
        flash('Receipt deleted successfully', 'success')
    else:
        flash('Error deleting receipt', 'error')
    return redirect(url_for('purchase_receipts'))

# ==================== DATA BACKUP & RESTORE ROUTES ====================

@app.route('/backup')
def backup_data():
    """Export all data as JSON"""
    db = get_db()
    
    try:
        # Gather all data
        backup_data = {
            'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.2.0',
            'reptiles': db.get_all_reptiles(),
            'feeding_logs': db.get_all_feeding_logs(),
            'shed_records': db.get_all_shed_records(),
            'weight_history': [],
            'length_history': [],
            'photos': [],
            'feeding_reminders': db.get_feeding_reminders()
        }
        
        # Get weight and length history for all reptiles
        for reptile in backup_data['reptiles']:
            weight_hist = db.get_weight_history(reptile['id'])
            length_hist = db.get_length_history(reptile['id'])
            photos = db.get_photos(reptile['id'])
            
            for record in weight_hist:
                record['reptile_id'] = reptile['id']
                backup_data['weight_history'].append(record)
            
            for record in length_hist:
                record['reptile_id'] = reptile['id']
                backup_data['length_history'].append(record)
            
            for photo in photos:
                backup_data['photos'].append(photo)
        
        # Create JSON response
        json_data = jsonify(backup_data)
        response = make_response(json_data)
        response.headers['Content-Disposition'] = f'attachment; filename=reptile_tracker_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        response.headers['Content-Type'] = 'application/json'
        
        return response
    except Exception as e:
        flash(f'Error creating backup: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/restore', methods=['GET', 'POST'])
def restore_data():
    """Restore data from JSON backup"""
    if request.method == 'POST':
        if 'backup_file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('restore_data'))
        
        file = request.files['backup_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('restore_data'))
        
        if not file.filename.endswith('.json'):
            flash('Invalid file type. Please upload a JSON backup file', 'error')
            return redirect(url_for('restore_data'))
        
        try:
            # Read and parse JSON
            import json
            backup_data = json.load(file)
            
            # Validate backup structure
            required_keys = ['reptiles', 'feeding_logs', 'shed_records']
            if not all(key in backup_data for key in required_keys):
                flash('Invalid backup file format', 'error')
                return redirect(url_for('restore_data'))
            
            db = get_db()
            restore_mode = request.form.get('restore_mode', 'merge')
            
            if restore_mode == 'replace':
                # Clear existing data (dangerous!)
                if request.form.get('confirm_replace') != 'yes':
                    flash('Please confirm data replacement', 'error')
                    return redirect(url_for('restore_data'))
                
                # Delete all existing data
                db.cursor.execute('DELETE FROM feeding_logs')
                db.cursor.execute('DELETE FROM shed_records')
                db.cursor.execute('DELETE FROM weight_history')
                db.cursor.execute('DELETE FROM length_history')
                db.cursor.execute('DELETE FROM photos')
                db.cursor.execute('DELETE FROM feeding_reminders')
                db.cursor.execute('DELETE FROM reptiles')
                db.conn.commit()
            
            # Restore reptiles
            reptile_id_map = {}  # Map old IDs to new IDs
            for reptile in backup_data['reptiles']:
                old_id = reptile['id']
                new_id = db.add_reptile(
                    name=reptile['name'],
                    species=reptile['species'],
                    morph=reptile.get('morph'),
                    sex=reptile.get('sex'),
                    date_of_birth=reptile.get('date_of_birth'),
                    acquisition_date=reptile.get('acquisition_date'),
                    weight_grams=reptile.get('weight_grams'),
                    length_cm=reptile.get('length_cm'),
                    notes=reptile.get('notes'),
                    image_path=reptile.get('image_path')
                )
                reptile_id_map[old_id] = new_id
            
            # Restore feeding logs
            for log in backup_data['feeding_logs']:
                if log['reptile_id'] in reptile_id_map:
                    db.add_feeding_log(
                        reptile_id=reptile_id_map[log['reptile_id']],
                        feeding_date=log['feeding_date'],
                        food_type=log['food_type'],
                        food_size=log.get('food_size'),
                        quantity=log.get('quantity', 1),
                        ate=log.get('ate', True),
                        notes=log.get('notes')
                    )
            
            # Restore shed records
            for record in backup_data['shed_records']:
                if record['reptile_id'] in reptile_id_map:
                    db.add_shed_record(
                        reptile_id=reptile_id_map[record['reptile_id']],
                        shed_date=record['shed_date'],
                        complete=record.get('complete', True),
                        notes=record.get('notes')
                    )
            
            # Restore weight history
            if 'weight_history' in backup_data:
                for record in backup_data['weight_history']:
                    if record['reptile_id'] in reptile_id_map:
                        db.add_weight_measurement(
                            reptile_id=reptile_id_map[record['reptile_id']],
                            weight_grams=record['weight_grams'],
                            measurement_date=record['measurement_date'],
                            notes=record.get('notes')
                        )
            
            # Restore length history
            if 'length_history' in backup_data:
                for record in backup_data['length_history']:
                    if record['reptile_id'] in reptile_id_map:
                        db.add_length_measurement(
                            reptile_id=reptile_id_map[record['reptile_id']],
                            length_cm=record['length_cm'],
                            measurement_date=record['measurement_date'],
                            notes=record.get('notes')
                        )
            
            # Restore feeding reminders
            if 'feeding_reminders' in backup_data:
                for reminder in backup_data['feeding_reminders']:
                    if reminder['reptile_id'] in reptile_id_map:
                        db.add_feeding_reminder(
                            reptile_id=reptile_id_map[reminder['reptile_id']],
                            feeding_interval_days=reminder['feeding_interval_days']
                        )
            
            flash(f'Data restored successfully! Imported {len(reptile_id_map)} reptiles.', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Error restoring data: {str(e)}', 'error')
            return redirect(url_for('restore_data'))
    
    return render_template('restore_data.html')



