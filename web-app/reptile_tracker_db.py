"""
Reptile Tracker Database Module
Handles all database operations for the reptile tracking application
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import os


class ReptileDatabase:
    """Database manager for reptile tracking application"""
    
    def __init__(self, db_path: str = "reptile_tracker.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Create all necessary database tables"""
        
        # Reptiles table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reptiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                species TEXT NOT NULL,
                morph TEXT,
                sex TEXT,
                date_of_birth DATE,
                acquisition_date DATE,
                weight_grams REAL,
                length_cm REAL,
                notes TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Feeding logs table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS feeding_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reptile_id INTEGER NOT NULL,
                feeding_date DATE NOT NULL,
                food_type TEXT NOT NULL,
                food_size TEXT,
                quantity INTEGER DEFAULT 1,
                ate BOOLEAN NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reptile_id) REFERENCES reptiles (id) ON DELETE CASCADE
            )
        ''')
        
        # Shed records table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS shed_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reptile_id INTEGER NOT NULL,
                shed_date DATE NOT NULL,
                complete BOOLEAN NOT NULL,
                shed_length_cm REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reptile_id) REFERENCES reptiles (id) ON DELETE CASCADE
            )
        ''')
        
        # Weight history table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS weight_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reptile_id INTEGER NOT NULL,
                measurement_date DATE NOT NULL,
                weight_grams REAL NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reptile_id) REFERENCES reptiles (id) ON DELETE CASCADE
            )
        ''')
        
        # Photos table (for photo gallery)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reptile_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                caption TEXT,
                is_primary BOOLEAN DEFAULT 0,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reptile_id) REFERENCES reptiles (id) ON DELETE CASCADE
            )
        ''')
        
        # Feeding reminders table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS feeding_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reptile_id INTEGER NOT NULL,
                feeding_interval_days INTEGER NOT NULL,
                last_fed_date DATE,
                next_feeding_date DATE,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reptile_id) REFERENCES reptiles (id) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()
    
    # ==================== REPTILE OPERATIONS ====================
    
    def add_reptile(self, name: str, species: str, morph: str = None, sex: str = None,
                   date_of_birth: str = None, acquisition_date: str = None,
                   weight_grams: float = None, length_cm: float = None,
                   notes: str = None, image_path: str = None) -> int:
        """Add a new reptile to the database"""
        self.cursor.execute('''
            INSERT INTO reptiles (name, species, morph, sex, date_of_birth, 
                                acquisition_date, weight_grams, length_cm, notes, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, species, morph, sex, date_of_birth, acquisition_date,
              weight_grams, length_cm, notes, image_path))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_reptile(self, reptile_id: int) -> Optional[Dict]:
        """Get a single reptile by ID"""
        self.cursor.execute('SELECT * FROM reptiles WHERE id = ?', (reptile_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_reptiles(self) -> List[Dict]:
        """Get all reptiles"""
        self.cursor.execute('SELECT * FROM reptiles ORDER BY name')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_reptile(self, reptile_id: int, **kwargs) -> bool:
        """Update reptile information"""
        allowed_fields = ['name', 'species', 'morph', 'sex', 'date_of_birth',
                         'acquisition_date', 'weight_grams', 'length_cm', 'notes', 'image_path']
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [reptile_id]
        
        self.cursor.execute(f'''
            UPDATE reptiles 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', values)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_reptile(self, reptile_id: int) -> bool:
        """Delete a reptile and all associated records"""
        self.cursor.execute('DELETE FROM reptiles WHERE id = ?', (reptile_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    # ==================== FEEDING LOG OPERATIONS ====================
    
    def add_feeding_log(self, reptile_id: int, feeding_date: str, food_type: str,
                       food_size: str = None, quantity: int = 1, ate: bool = True,
                       notes: str = None) -> int:
        """Add a feeding log entry"""
        self.cursor.execute('''
            INSERT INTO feeding_logs (reptile_id, feeding_date, food_type, 
                                     food_size, quantity, ate, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (reptile_id, feeding_date, food_type, food_size, quantity, ate, notes))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_feeding_logs(self, reptile_id: int = None, start_date: str = None,
                        end_date: str = None, limit: int = None) -> List[Dict]:
        """Get feeding logs with optional filters"""
        query = '''
            SELECT fl.*, r.name as reptile_name 
            FROM feeding_logs fl
            JOIN reptiles r ON fl.reptile_id = r.id
            WHERE 1=1
        '''
        params = []
        
        if reptile_id:
            query += ' AND fl.reptile_id = ?'
            params.append(reptile_id)
        
        if start_date:
            query += ' AND fl.feeding_date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND fl.feeding_date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY fl.feeding_date DESC'
        
        if limit:
            query += f' LIMIT {limit}'
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_feeding_log(self, log_id: int, **kwargs) -> bool:
        """Update a feeding log entry"""
        allowed_fields = ['feeding_date', 'food_type', 'food_size', 'quantity', 'ate', 'notes']
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [log_id]
        
        self.cursor.execute(f'UPDATE feeding_logs SET {set_clause} WHERE id = ?', values)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_feeding_log(self, log_id: int) -> bool:
        """Delete a feeding log entry"""
        self.cursor.execute('DELETE FROM feeding_logs WHERE id = ?', (log_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def get_all_feeding_logs(self, limit: int = None) -> List[Dict]:
        """Get all feeding logs across all reptiles"""
        query = '''
            SELECT fl.*, r.name as reptile_name
            FROM feeding_logs fl
            JOIN reptiles r ON fl.reptile_id = r.id
            ORDER BY fl.feeding_date DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== SHED RECORD OPERATIONS ====================
    
    def add_shed_record(self, reptile_id: int, shed_date: str, complete: bool = True,
                       shed_length_cm: float | None = None, notes: str | None = None) -> int:
        """Add a shed record"""
        self.cursor.execute('''
            INSERT INTO shed_records (reptile_id, shed_date, complete, shed_length_cm, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (reptile_id, shed_date, complete, shed_length_cm, notes))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_shed_records(self, reptile_id: int = None, start_date: str = None,
                        end_date: str = None, limit: int = None) -> List[Dict]:
        """Get shed records with optional filters"""
        query = '''
            SELECT sr.*, r.name as reptile_name 
            FROM shed_records sr
            JOIN reptiles r ON sr.reptile_id = r.id
            WHERE 1=1
        '''
        params = []
        
        if reptile_id:
            query += ' AND sr.reptile_id = ?'
            params.append(reptile_id)
        
        if start_date:
            query += ' AND sr.shed_date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND sr.shed_date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY sr.shed_date DESC'
        
        if limit:
            query += f' LIMIT {limit}'
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_shed_record(self, record_id: int, **kwargs) -> bool:
        """Update a shed record"""
        allowed_fields = ['shed_date', 'complete', 'notes']
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [record_id]
        
        self.cursor.execute(f'UPDATE shed_records SET {set_clause} WHERE id = ?', values)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_shed_record(self, record_id: int) -> bool:
        """Delete a shed record"""
        self.cursor.execute('DELETE FROM shed_records WHERE id = ?', (record_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def get_all_shed_records(self, limit: int = None) -> List[Dict]:
        """Get all shed records across all reptiles"""
        query = '''
            SELECT sr.*, r.name as reptile_name
            FROM shed_records sr
            JOIN reptiles r ON sr.reptile_id = r.id
            ORDER BY sr.shed_date DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== STATISTICS & ANALYTICS ====================
    
    def get_reptile_stats(self, reptile_id: int) -> Dict:
        """Get statistics for a specific reptile"""
        stats = {}
        
        # Total feedings
        self.cursor.execute('''
            SELECT COUNT(*) as total, SUM(CASE WHEN ate = 1 THEN 1 ELSE 0 END) as ate
            FROM feeding_logs WHERE reptile_id = ?
        ''', (reptile_id,))
        feeding_stats = dict(self.cursor.fetchone())
        stats['total_feedings'] = feeding_stats['total']
        stats['successful_feedings'] = feeding_stats['ate']
        stats['feeding_success_rate'] = (
            (feeding_stats['ate'] / feeding_stats['total'] * 100) 
            if feeding_stats['total'] > 0 else 0
        )
        
        # Last feeding
        self.cursor.execute('''
            SELECT feeding_date, food_type, ate 
            FROM feeding_logs 
            WHERE reptile_id = ? 
            ORDER BY feeding_date DESC LIMIT 1
        ''', (reptile_id,))
        last_feeding = self.cursor.fetchone()
        stats['last_feeding'] = dict(last_feeding) if last_feeding else None
        
        # Total sheds
        self.cursor.execute('''
            SELECT COUNT(*) as total, SUM(CASE WHEN complete = 1 THEN 1 ELSE 0 END) as complete
            FROM shed_records WHERE reptile_id = ?
        ''', (reptile_id,))
        shed_stats = dict(self.cursor.fetchone())
        stats['total_sheds'] = shed_stats['total']
        stats['complete_sheds'] = shed_stats['complete']
        
        # Last shed
        self.cursor.execute('''
            SELECT shed_date, complete 
            FROM shed_records 
            WHERE reptile_id = ? 
            ORDER BY shed_date DESC LIMIT 1
        ''', (reptile_id,))
        last_shed = self.cursor.fetchone()
        stats['last_shed'] = dict(last_shed) if last_shed else None
        
        return stats
    
    def get_dashboard_stats(self) -> Dict:
        """Get overall dashboard statistics"""
        stats = {}
        
        # Total reptiles
        self.cursor.execute('SELECT COUNT(*) as count FROM reptiles')
        stats['total_reptiles'] = self.cursor.fetchone()['count']
        
        # Total feedings
        self.cursor.execute('SELECT COUNT(*) as count FROM feeding_logs')
        stats['total_feedings'] = self.cursor.fetchone()['count']
        
        # Total sheds
        self.cursor.execute('SELECT COUNT(*) as count FROM shed_records')
        stats['total_sheds'] = self.cursor.fetchone()['count']
        
        # Feeding success rate
        self.cursor.execute('''
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN ate = 1 THEN 1 ELSE 0 END) as successful
            FROM feeding_logs
        ''')
        feeding_data = self.cursor.fetchone()
        if feeding_data['total'] > 0:
            stats['feeding_success_rate'] = (feeding_data['successful'] / feeding_data['total']) * 100
        else:
            stats['feeding_success_rate'] = 0
        
        # Recent feedings (last 7 days)
        self.cursor.execute('''
            SELECT COUNT(*) as count
            FROM feeding_logs
            WHERE feeding_date >= date('now', '-7 days')
        ''')
        stats['recent_feedings'] = self.cursor.fetchone()['count']
        
        # Recent sheds (last 30 days)
        self.cursor.execute('''
            SELECT COUNT(*) as count
            FROM shed_records
            WHERE shed_date >= date('now', '-30 days')
        ''')
        stats['recent_sheds'] = self.cursor.fetchone()['count']
        
        # Reptiles needing feeding (no feeding in last 7 days)
        self.cursor.execute('''
            SELECT COUNT(DISTINCT r.id) as count
            FROM reptiles r
            LEFT JOIN feeding_logs fl ON r.id = fl.reptile_id
                AND fl.feeding_date >= date('now', '-7 days')
            WHERE fl.id IS NULL
        ''')
        stats['needs_feeding'] = self.cursor.fetchone()['count']
        
        return stats
    
    # ==================== BULK IMPORT OPERATIONS ====================
    
    def bulk_import_reptiles(self, reptiles_data: List[Dict]) -> Tuple[int, List[str]]:
        """
        Bulk import reptiles from a list of dictionaries
        Returns: (number_imported, list_of_errors)
        """
        imported = 0
        errors = []
        
        for idx, reptile in enumerate(reptiles_data, start=2):  # Start at 2 (row 1 is header)
            try:
                # Validate required fields
                if not reptile.get('name') or not reptile.get('species'):
                    errors.append(f"Row {idx}: Missing required fields (name or species)")
                    continue
                
                # Add reptile
                self.add_reptile(
                    name=str(reptile.get('name', '')),
                    species=str(reptile.get('species', '')),
                    morph=str(reptile.get('morph', '')) if reptile.get('morph') else None,
                    sex=str(reptile.get('sex', '')) if reptile.get('sex') else None,
                    date_of_birth=str(reptile.get('date_of_birth', '')) if reptile.get('date_of_birth') else None,
                    acquisition_date=str(reptile.get('acquisition_date', '')) if reptile.get('acquisition_date') else None,
                    weight_grams=float(reptile.get('weight_grams')) if reptile.get('weight_grams') else None,
                    length_cm=float(reptile.get('length_cm')) if reptile.get('length_cm') else None,
                    notes=str(reptile.get('notes', '')) if reptile.get('notes') else None,
                    image_path=None  # Images not supported in bulk import
                )
                imported += 1
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
        
        return imported, errors
    
    def bulk_import_feeding_logs(self, logs_data: List[Dict]) -> Tuple[int, List[str]]:
        """
        Bulk import feeding logs from a list of dictionaries
        Returns: (number_imported, list_of_errors)
        """
        imported = 0
        errors = []
        
        for idx, log in enumerate(logs_data, start=2):
            try:
                # Validate required fields
                if not log.get('reptile_name') or not log.get('feeding_date') or not log.get('food_type'):
                    errors.append(f"Row {idx}: Missing required fields")
                    continue
                
                # Find reptile by name
                self.cursor.execute('SELECT id FROM reptiles WHERE name = ?', (log.get('reptile_name'),))
                reptile = self.cursor.fetchone()
                
                if not reptile:
                    errors.append(f"Row {idx}: Reptile '{log.get('reptile_name')}' not found")
                    continue
                
                # Add feeding log
                self.add_feeding_log(
                    reptile_id=reptile['id'],
                    feeding_date=str(log.get('feeding_date')),
                    food_type=str(log.get('food_type')),
                    food_size=str(log.get('food_size', '')) if log.get('food_size') else None,
                    quantity=int(log.get('quantity', 1)),
                    ate=str(log.get('ate', 'yes')).lower() in ['yes', 'true', '1', 'y'],
                    notes=str(log.get('notes', '')) if log.get('notes') else None
                )
                imported += 1
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
        
        return imported, errors
    
    def bulk_import_shed_records(self, records_data: List[Dict]) -> Tuple[int, List[str]]:
        """
        Bulk import shed records from a list of dictionaries
        Returns: (number_imported, list_of_errors)
        """
        imported = 0
        errors = []
        
        for idx, record in enumerate(records_data, start=2):
            try:
                # Validate required fields
                if not record.get('reptile_name') or not record.get('shed_date'):
                    errors.append(f"Row {idx}: Missing required fields")
                    continue
                
                # Find reptile by name
                self.cursor.execute('SELECT id FROM reptiles WHERE name = ?', (record.get('reptile_name'),))
                reptile = self.cursor.fetchone()
                
                if not reptile:
                    errors.append(f"Row {idx}: Reptile '{record.get('reptile_name')}' not found")
                    continue
                
                # Add shed record
                self.add_shed_record(
                    reptile_id=reptile['id'],
                    shed_date=str(record.get('shed_date')),
                    complete=str(record.get('complete', 'yes')).lower() in ['yes', 'true', '1', 'y', 'complete'],
                    shed_length_cm=float(record.get('shed_length_cm')) if record.get('shed_length_cm') else None,
                    notes=str(record.get('notes', '')) if record.get('notes') else None
                )
                imported += 1
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
        
        return imported, errors


# Utility functions for date handling
def get_current_date() -> str:
    """Get current date in YYYY-MM-DD format"""
    return datetime.now().strftime('%Y-%m-%d')


def calculate_age(date_of_birth: str) -> Optional[str]:
    """Calculate age from date of birth"""
    if not date_of_birth:
        return None
    
    try:
        dob = datetime.strptime(date_of_birth, '%Y-%m-%d')
        today = datetime.now()
        age_days = (today - dob).days
        
        if age_days < 30:
            return f"{age_days} days"
        elif age_days < 365:
            months = age_days // 30
            return f"{months} month{'s' if months != 1 else ''}"
        else:
            years = age_days // 365
            months = (age_days % 365) // 30
            if months > 0:
                return f"{years} year{'s' if years != 1 else ''}, {months} month{'s' if months != 1 else ''}"
            return f"{years} year{'s' if years != 1 else ''}"
    except ValueError:
        return None

# Made with Bob

    
    # ==================== WEIGHT HISTORY OPERATIONS ====================
    
    def add_weight_measurement(self, reptile_id: int, measurement_date: str, 
                              weight_grams: float, notes: str = None) -> int:
        """Add a weight measurement"""
        self.cursor.execute('''
            INSERT INTO weight_history (reptile_id, measurement_date, weight_grams, notes)
            VALUES (?, ?, ?, ?)
        ''', (reptile_id, measurement_date, weight_grams, notes))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_weight_history(self, reptile_id: int, limit: int = None) -> List[Dict]:
        """Get weight history for a reptile"""
        query = '''
            SELECT * FROM weight_history 
            WHERE reptile_id = ?
            ORDER BY measurement_date DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        self.cursor.execute(query, (reptile_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_weight_chart_data(self, reptile_id: int) -> Dict:
        """Get weight data formatted for charts"""
        self.cursor.execute('''
            SELECT measurement_date, weight_grams 
            FROM weight_history 
            WHERE reptile_id = ?
            ORDER BY measurement_date ASC
        ''', (reptile_id,))
        
        data = self.cursor.fetchall()
        return {
            'dates': [row['measurement_date'] for row in data],
            'weights': [row['weight_grams'] for row in data]
        }
    
    # ==================== PHOTO GALLERY OPERATIONS ====================
    
    def add_photo(self, reptile_id: int, image_path: str, caption: str = None, 
                  is_primary: bool = False) -> int:
        """Add a photo to reptile's gallery"""
        # If this is set as primary, unset other primary photos
        if is_primary:
            self.cursor.execute('''
                UPDATE photos SET is_primary = 0 WHERE reptile_id = ?
            ''', (reptile_id,))
        
        self.cursor.execute('''
            INSERT INTO photos (reptile_id, image_path, caption, is_primary)
            VALUES (?, ?, ?, ?)
        ''', (reptile_id, image_path, caption, is_primary))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_photos(self, reptile_id: int) -> List[Dict]:
        """Get all photos for a reptile"""
        self.cursor.execute('''
            SELECT * FROM photos 
            WHERE reptile_id = ?
            ORDER BY is_primary DESC, upload_date DESC
        ''', (reptile_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_primary_photo(self, reptile_id: int) -> Optional[Dict]:
        """Get the primary photo for a reptile"""
        self.cursor.execute('''
            SELECT * FROM photos 
            WHERE reptile_id = ? AND is_primary = 1
            LIMIT 1
        ''', (reptile_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def set_primary_photo(self, photo_id: int, reptile_id: int) -> bool:
        """Set a photo as primary"""
        # Unset all primary photos for this reptile
        self.cursor.execute('''
            UPDATE photos SET is_primary = 0 WHERE reptile_id = ?
        ''', (reptile_id,))
        
        # Set the new primary photo
        self.cursor.execute('''
            UPDATE photos SET is_primary = 1 WHERE id = ?
        ''', (photo_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_photo(self, photo_id: int) -> bool:
        """Delete a photo"""
        self.cursor.execute('DELETE FROM photos WHERE id = ?', (photo_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    # ==================== FEEDING REMINDER OPERATIONS ====================
    
    def add_feeding_reminder(self, reptile_id: int, feeding_interval_days: int) -> int:
        """Add or update feeding reminder for a reptile"""
        # Check if reminder already exists
        self.cursor.execute('''
            SELECT id FROM feeding_reminders WHERE reptile_id = ?
        ''', (reptile_id,))
        existing = self.cursor.fetchone()
        
        if existing:
            # Update existing reminder
            self.cursor.execute('''
                UPDATE feeding_reminders 
                SET feeding_interval_days = ?, is_active = 1
                WHERE reptile_id = ?
            ''', (feeding_interval_days, reptile_id))
            self.conn.commit()
            return existing['id']
        else:
            # Create new reminder
            self.cursor.execute('''
                INSERT INTO feeding_reminders (reptile_id, feeding_interval_days)
                VALUES (?, ?)
            ''', (reptile_id, feeding_interval_days))
            self.conn.commit()
            return self.cursor.lastrowid
    
    def update_feeding_reminder_dates(self, reptile_id: int, last_fed_date: str):
        """Update reminder dates after feeding"""
        self.cursor.execute('''
            SELECT feeding_interval_days FROM feeding_reminders 
            WHERE reptile_id = ? AND is_active = 1
        ''', (reptile_id,))
        reminder = self.cursor.fetchone()
        
        if reminder:
            from datetime import datetime, timedelta
            last_fed = datetime.strptime(last_fed_date, '%Y-%m-%d')
            next_feeding = last_fed + timedelta(days=reminder['feeding_interval_days'])
            
            self.cursor.execute('''
                UPDATE feeding_reminders 
                SET last_fed_date = ?, next_feeding_date = ?
                WHERE reptile_id = ?
            ''', (last_fed_date, next_feeding.strftime('%Y-%m-%d'), reptile_id))
            self.conn.commit()
    
    def get_feeding_reminders(self, reptile_id: int = None) -> List[Dict]:
        """Get feeding reminders"""
        if reptile_id:
            query = '''
                SELECT fr.*, r.name as reptile_name
                FROM feeding_reminders fr
                JOIN reptiles r ON fr.reptile_id = r.id
                WHERE fr.reptile_id = ? AND fr.is_active = 1
            '''
            self.cursor.execute(query, (reptile_id,))
        else:
            query = '''
                SELECT fr.*, r.name as reptile_name
                FROM feeding_reminders fr
                JOIN reptiles r ON fr.reptile_id = r.id
                WHERE fr.is_active = 1
                ORDER BY fr.next_feeding_date ASC
            '''
            self.cursor.execute(query)
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_overdue_feedings(self) -> List[Dict]:
        """Get reptiles with overdue feedings"""
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute('''
            SELECT fr.*, r.name as reptile_name, r.species
            FROM feeding_reminders fr
            JOIN reptiles r ON fr.reptile_id = r.id
            WHERE fr.is_active = 1 
            AND fr.next_feeding_date IS NOT NULL
            AND fr.next_feeding_date <= ?
            ORDER BY fr.next_feeding_date ASC
        ''', (today,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def toggle_feeding_reminder(self, reptile_id: int, is_active: bool) -> bool:
        """Enable or disable feeding reminder"""
        self.cursor.execute('''
            UPDATE feeding_reminders 
            SET is_active = ?
            WHERE reptile_id = ?
        ''', (is_active, reptile_id))
        self.conn.commit()
        return self.cursor.rowcount > 0
