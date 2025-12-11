"""
Reptile Tracker Web Application
Flask-based web interface for tracking reptile care
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, send_file, make_response
from werkzeug.utils import secure_filename
import os
import sys
from datetime import datetime
import pandas as pd
from io import BytesIO

# Import database module from local directory
from reptile_tracker_db import ReptileDatabase

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Use persistent storage path if available (for Render/Railway)
DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(DATA_DIR, 'reptile_tracker.db')
UPLOAD_PATH = os.path.join(DATA_DIR, 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_PATH
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_PATH, exist_ok=True)

# Log database path for debugging
print(f"[INFO] Database path: {DB_PATH}")
print(f"[INFO] Data directory: {DATA_DIR}")
print(f"[INFO] Upload path: {UPLOAD_PATH}")
print(f"[INFO] Database exists: {os.path.exists(DB_PATH)}")

def get_db():
    """Get database connection for current request"""
    return ReptileDatabase(DB_PATH)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Dashboard - show all reptiles"""
    db = get_db()
    reptiles = db.get_all_reptiles()
    stats = db.get_dashboard_stats()
    overdue_feedings = db.get_overdue_feedings()
    return render_template('dashboard.html',
                         reptiles=reptiles,
                         stats=stats,
                         overdue_feedings=overdue_feedings)

@app.route('/reptile/<int:reptile_id>')
def reptile_details(reptile_id):
    """Show detailed reptile information"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if not reptile:
        flash('Reptile not found', 'error')
        return redirect(url_for('index'))
    
    feeding_logs = db.get_feeding_logs(reptile_id, limit=10)
    shed_records = db.get_shed_records(reptile_id, limit=10)
    
    return render_template('reptile_details.html', 
                         reptile=reptile, 
                         feeding_logs=feeding_logs,
                         shed_records=shed_records)

@app.route('/reptile/add', methods=['GET', 'POST'])
def add_reptile():
    """Add new reptile"""
    db = get_db()
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
                'image_path': image_path
            }
            
            reptile_id = db.add_reptile(**data)
            flash(f'{data["name"]} has been added successfully!', 'success')
            return redirect(url_for('reptile_details', reptile_id=reptile_id))
        except Exception as e:
            flash(f'Error adding reptile: {str(e)}', 'error')
    
    return render_template('reptile_form.html', mode='add', reptile=None)

@app.route('/reptile/<int:reptile_id>/edit', methods=['GET', 'POST'])
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
def delete_reptile(reptile_id):
    """Delete reptile"""
    db = get_db()
    reptile = db.get_reptile(reptile_id)
    if reptile:
        db.delete_reptile(reptile_id)
        flash(f'{reptile["name"]} has been deleted', 'success')
    return redirect(url_for('index'))

@app.route('/feeding')
def feeding_logs():
    """Show all feeding logs"""
    db = get_db()
    logs = db.get_all_feeding_logs(limit=100)
    reptiles = db.get_all_reptiles()
    return render_template('feeding_logs.html', logs=logs, reptiles=reptiles)

@app.route('/feeding/add', methods=['GET', 'POST'])
def add_feeding():
    """Add feeding log"""
    db = get_db()
    if request.method == 'POST':
        try:
            # Get inventory_id if using inventory
            use_inventory = request.form.get('use_inventory') == 'yes'
            inventory_id = int(request.form.get('inventory_id')) if use_inventory and request.form.get('inventory_id') else None
            
            data = {
                'reptile_id': int(request.form.get('reptile_id')),
                'feeding_date': request.form.get('date'),
                'food_type': request.form.get('food_type'),
                'food_size': request.form.get('food_size') or None,
                'quantity': int(request.form.get('quantity', 1)),
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
    return render_template('feeding_form.html', reptiles=reptiles, log=None, inventory_items=inventory_items)

@app.route('/shed')
def shed_records():
    """Show all shed records"""
    db = get_db()
    records = db.get_all_shed_records(limit=100)
    reptiles = db.get_all_reptiles()
    return render_template('shed_records.html', records=records, reptiles=reptiles)

@app.route('/shed/add', methods=['GET', 'POST'])
def add_shed():
    """Add shed record"""
    db = get_db()
    if request.method == 'POST':
        try:
            data = {
                'reptile_id': int(request.form.get('reptile_id')),
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
    
    reptiles = db.get_all_reptiles()
    return render_template('shed_form.html', reptiles=reptiles, record=None)

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
def records_page():
    """Records hub page with feeding and shed records"""
    db = get_db()
    
    # Get stats
    stats = db.get_dashboard_stats()
    
    # Get recent activity
    recent_feedings = db.get_all_feeding_logs(limit=5)
    recent_sheds = db.get_shed_records(limit=5)
    
    return render_template('records.html', 
                         stats=stats,
                         recent_feedings=recent_feedings,
                         recent_sheds=recent_sheds)

@app.route('/settings')
def settings_page():
    """Settings page with data management options"""
    return render_template('settings.html')


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
            'notes': request.form.get('notes') or None
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
            'notes': request.form.get('notes') or None
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
    """Display all expenses with filtering"""
    db = get_db()
    
    # Get filter parameters
    reptile_id = request.args.get('reptile_id', type=int)
    category = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Get expenses with filters
    expenses = db.get_expenses(
        reptile_id=reptile_id,
        category=category,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get summary statistics
    summary = db.get_expense_summary(
        start_date=start_date,
        end_date=end_date,
        reptile_id=reptile_id
    )
    
    # Get all reptiles for filter dropdown
    reptiles = db.get_all_reptiles()
    
    # Get unique categories
    categories = db.get_expense_categories()
    
    return render_template('expenses.html',
                         expenses=expenses,
                         summary=summary,
                         reptiles=reptiles,
                         categories=categories,
                         selected_reptile=reptile_id,
                         selected_category=category,
                         start_date=start_date,
                         end_date=end_date)

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

@app.route('/inventory')
def food_inventory():
    """Display food inventory"""
    db = get_db()
    
    # Get all inventory items
    inventory = db.get_food_inventory(include_zero=True)
    
    # Get low stock items
    low_stock = db.get_low_stock_items(threshold=5)
    
    # Get out of stock items
    out_of_stock = db.get_out_of_stock_items()
    
    # Get inventory forecasts
    forecasts = db.get_inventory_forecast(days_lookback=30)
    
    # Create a forecast lookup dictionary by inventory_id
    forecast_dict = {f['inventory_id']: f for f in forecasts}
    
    return render_template('food_inventory.html',
                         inventory=inventory,
                         low_stock=low_stock,
                         out_of_stock=out_of_stock,
                         forecasts=forecast_dict)

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
    
    # Get existing food types for suggestions
    existing_inventory = db.get_food_inventory(include_zero=True)
    food_types = list(set([item['food_type'] for item in existing_inventory]))
    food_sizes = list(set([item['food_size'] for item in existing_inventory]))
    
    return render_template('add_inventory_item.html',
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



