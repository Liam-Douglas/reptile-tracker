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
    
    # ==================== SHED RECORD OPERATIONS ====================
    
    def add_shed_record(self, reptile_id: int, shed_date: str, complete: bool = True,
                       notes: str = None) -> int:
        """Add a shed record"""
        self.cursor.execute('''
            INSERT INTO shed_records (reptile_id, shed_date, complete, notes)
            VALUES (?, ?, ?, ?)
        ''', (reptile_id, shed_date, complete, notes))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_shed_records(self, reptile_id: int = None, start_date: str = None,
                        end_date: str = None) -> List[Dict]:
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
