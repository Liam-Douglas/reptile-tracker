"""
Reptile Tracker Web Application
Flask-based web interface for tracking reptile care
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import sys
from datetime import datetime

# Import database module from local directory
from reptile_tracker_db import ReptileDatabase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def get_db():
    """Get database connection for current request"""
    return ReptileDatabase('reptile_tracker.db')

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
                'date': request.form.get('date'),
                'food_type': request.form.get('food_type'),
                'amount': request.form.get('amount') or None,
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
