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
            data = {
                'reptile_id': int(request.form.get('reptile_id')),
                'feeding_date': request.form.get('date'),
                'food_type': request.form.get('food_type'),
                'food_size': request.form.get('food_size') or None,
                'quantity': int(request.form.get('quantity', 1)),
                'ate': request.form.get('ate') == 'yes',
                'notes': request.form.get('notes') or None
            }
            db.add_feeding_log(**data)
            
            # Update feeding reminder dates if reminder exists
            db.update_feeding_reminder_dates(data['reptile_id'], data['feeding_date'])
            
            flash('Feeding log added successfully!', 'success')
            return redirect(url_for('feeding_logs'))
        except Exception as e:
            flash(f'Error adding feeding log: {str(e)}', 'error')
    
    reptiles = db.get_all_reptiles()
    return render_template('feeding_form.html', reptiles=reptiles, log=None)

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



