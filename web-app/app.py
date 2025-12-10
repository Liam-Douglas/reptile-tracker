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
    return render_template('dashboard.html', reptiles=reptiles, stats=stats)

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

if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5001)

# Made with Bob

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
