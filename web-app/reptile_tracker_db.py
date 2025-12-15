"""
Reptile Tracker Database Module
Handles all database operations for the reptile tracking application
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReptileDatabase:
    """Database manager for reptile tracking application"""
    
    def __init__(self, db_path: str = "reptile_tracker.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        self.migrate_database()
    
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
                inventory_id INTEGER,
                auto_deducted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reptile_id) REFERENCES reptiles (id) ON DELETE CASCADE,
                FOREIGN KEY (inventory_id) REFERENCES food_inventory (id) ON DELETE SET NULL
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
        
        # Length history table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS length_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reptile_id INTEGER NOT NULL,
                measurement_date DATE NOT NULL,
                length_cm REAL NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reptile_id) REFERENCES reptiles (id) ON DELETE CASCADE
            )
        ''')
        
        # Tank cleaning logs table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tank_cleaning_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reptile_id INTEGER NOT NULL,
                cleaning_date DATE NOT NULL,
                cleaning_type TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reptile_id) REFERENCES reptiles (id) ON DELETE CASCADE
            )
        ''')
        
        # Handling logs table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS handling_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reptile_id INTEGER NOT NULL,
                handling_date DATE NOT NULL,
                duration_minutes INTEGER,
                behavior TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reptile_id) REFERENCES reptiles (id) ON DELETE CASCADE
            )
        ''')
        ''')
        
        # Feeding reminders table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS feeding_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reptile_id INTEGER NOT NULL,
                feeding_interval_days INTEGER NOT NULL,
                food_type TEXT,
                food_size TEXT,
                quantity_per_feeding INTEGER DEFAULT 1,
                last_fed_date DATE,
                next_feeding_date DATE,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reptile_id) REFERENCES reptiles (id) ON DELETE CASCADE
            )
        ''')
        
        # Notification settings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_enabled BOOLEAN DEFAULT 0,
                email TEXT,
                sms_enabled BOOLEAN DEFAULT 0,
                phone TEXT,
                reminder_time TEXT DEFAULT '09:00',
                advance_notice INTEGER DEFAULT 0,
                notify_overdue_only BOOLEAN DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Expenses table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reptile_id INTEGER,
                expense_date DATE NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                vendor TEXT,
                description TEXT,
                receipt_path TEXT,
                payment_method TEXT,
                is_recurring BOOLEAN DEFAULT 0,
                tags TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reptile_id) REFERENCES reptiles (id) ON DELETE SET NULL
            )
        ''')
        
        # Food inventory table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS food_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                food_type TEXT NOT NULL,
                food_size TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                unit TEXT DEFAULT 'items',
                cost_per_unit REAL,
                supplier TEXT,
                purchase_date DATE,
                expiry_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(food_type, food_size)
            )
        ''')
        
        # Food inventory transactions table (for tracking stock changes)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                transaction_date DATE NOT NULL,
                reference_id INTEGER,
                reference_type TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inventory_id) REFERENCES food_inventory (id) ON DELETE CASCADE
            )
        ''')
        
        # Purchase receipts table (for bulk inventory additions)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_date DATE NOT NULL,
                supplier TEXT,
                total_cost REAL,
                payment_method TEXT,
                notes TEXT,
                image_path TEXT,
                ocr_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Receipt items table (line items for each receipt)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS receipt_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_id INTEGER NOT NULL,
                food_type TEXT NOT NULL,
                food_size TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                cost_per_unit REAL,
                total_cost REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (receipt_id) REFERENCES purchase_receipts (id) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()
    
    
    def migrate_database(self):
        """Run database migrations to add new columns to existing tables"""
        try:
            # Check if inventory_id column exists in feeding_logs
            self.cursor.execute("PRAGMA table_info(feeding_logs)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            # Add inventory_id column if it doesn't exist
            if 'inventory_id' not in columns:
                print("[MIGRATION] Adding inventory_id column to feeding_logs table...")
                self.cursor.execute('''
                    ALTER TABLE feeding_logs 
                    ADD COLUMN inventory_id INTEGER 
                    REFERENCES food_inventory(id) ON DELETE SET NULL
                ''')
                self.conn.commit()
                print("[MIGRATION] inventory_id column added successfully")
            
            # Add auto_deducted column if it doesn't exist
            if 'auto_deducted' not in columns:
                print("[MIGRATION] Adding auto_deducted column to feeding_logs table...")
                self.cursor.execute('''
                    ALTER TABLE feeding_logs 
                    ADD COLUMN auto_deducted BOOLEAN DEFAULT 0
                ''')
                self.conn.commit()
                print("[MIGRATION] auto_deducted column added successfully")
            
            # Check if new columns exist in feeding_reminders
            self.cursor.execute("PRAGMA table_info(feeding_reminders)")
            reminder_columns = [column[1] for column in self.cursor.fetchall()]
            
            # Add food_type column if it doesn't exist
            if 'food_type' not in reminder_columns:
                print("[MIGRATION] Adding food_type column to feeding_reminders table...")
                self.cursor.execute('''
                    ALTER TABLE feeding_reminders
                    ADD COLUMN food_type TEXT
                ''')
                self.conn.commit()
                print("[MIGRATION] food_type column added successfully")
            
            # Add food_size column if it doesn't exist
            if 'food_size' not in reminder_columns:
                print("[MIGRATION] Adding food_size column to feeding_reminders table...")
                self.cursor.execute('''
                    ALTER TABLE feeding_reminders
                    ADD COLUMN food_size TEXT
                ''')
                self.conn.commit()
                print("[MIGRATION] food_size column added successfully")
            
            # Add quantity_per_feeding column if it doesn't exist
            if 'quantity_per_feeding' not in reminder_columns:
                print("[MIGRATION] Adding quantity_per_feeding column to feeding_reminders table...")
                self.cursor.execute('''
                    ALTER TABLE feeding_reminders
                    ADD COLUMN quantity_per_feeding INTEGER DEFAULT 1
                ''')
                self.conn.commit()
                print("[MIGRATION] quantity_per_feeding column added successfully")
            
            # Populate food data for existing reminders from recent feeding logs
            if 'food_type' not in reminder_columns or 'food_size' not in reminder_columns:
                print("[MIGRATION] Populating food data for existing reminders...")
                self.cursor.execute('''
                    UPDATE feeding_reminders
                    SET food_type = (
                        SELECT food_type FROM feeding_logs
                        WHERE feeding_logs.reptile_id = feeding_reminders.reptile_id
                        ORDER BY feeding_date DESC LIMIT 1
                    ),
                    food_size = (
                        SELECT food_size FROM feeding_logs
                        WHERE feeding_logs.reptile_id = feeding_reminders.reptile_id
                        ORDER BY feeding_date DESC LIMIT 1
                    )
                    WHERE food_type IS NULL OR food_size IS NULL
                ''')
                self.conn.commit()
                print("[MIGRATION] Food data populated successfully")
                
        except Exception as e:
            print(f"[MIGRATION ERROR] {str(e)}")
            # Don't fail if migration has issues, just log it
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
                       notes: str = None, inventory_id: int = None, auto_deduct: bool = True) -> int:
        """Add a feeding log entry and optionally deduct from inventory"""
        
        # Insert feeding log first to get the ID
        self.cursor.execute('''
            INSERT INTO feeding_logs (reptile_id, feeding_date, food_type,
                                     food_size, quantity, ate, notes, inventory_id, auto_deducted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (reptile_id, feeding_date, food_type, food_size, quantity, ate, notes, inventory_id, False))
        self.conn.commit()
        feeding_log_id = self.cursor.lastrowid
        
        # If inventory_id is provided and reptile ate, deduct from inventory
        auto_deducted = False
        if inventory_id and ate and auto_deduct:
            try:
                # Deduct from inventory using update_food_quantity
                success = self.update_food_quantity(
                    inventory_id,
                    -quantity,  # Negative to subtract
                    transaction_type='feeding',
                    reference_id=feeding_log_id,
                    reference_type='feeding_log',
                    notes=f'Fed to reptile (Feeding Log #{feeding_log_id})'
                )
                if success:
                    auto_deducted = True
                    # Update the feeding log to mark as auto_deducted
                    self.cursor.execute('''
                        UPDATE feeding_logs SET auto_deducted = ? WHERE id = ?
                    ''', (True, feeding_log_id))
                    self.conn.commit()
                else:
                    print(f"Warning: Could not deduct {quantity} items from inventory {inventory_id}")
            except Exception as e:
                print(f"Error deducting inventory: {str(e)}")
        
        return feeding_log_id
    
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
    
    def get_food_item_by_type_size(self, food_type: str, food_size: str) -> Optional[Dict]:
        """Get a food inventory item by type and size"""
        self.cursor.execute('''
            SELECT * FROM food_inventory 
            WHERE food_type = ? AND food_size = ?
        ''', (food_type, food_size))
        row = self.cursor.fetchone()
        return dict(row) if row else None
        return [dict(row) for row in self.cursor.fetchall()]
    def get_distinct_food_types(self) -> List[str]:
        """Get list of unique food types from inventory and feeding logs"""
        # Standard food types based on frozen food supplier
        standard_types = ['Rat', 'Mouse', 'Rabbit', 'Cricket', 'Dubia Roach', 'Quail']
        
        # Get from inventory
        self.cursor.execute('SELECT DISTINCT food_type FROM food_inventory ORDER BY food_type')
        inventory_types = [row['food_type'] for row in self.cursor.fetchall()]
        
        # Get from feeding logs
        self.cursor.execute('SELECT DISTINCT food_type FROM feeding_logs WHERE food_type IS NOT NULL ORDER BY food_type')
        log_types = [row['food_type'] for row in self.cursor.fetchall()]
        
        # Combine standard types with existing data, maintaining order and removing duplicates
        all_types = []
        seen = set()
        
        # Add standard types first
        for food_type in standard_types:
            if food_type not in seen:
                all_types.append(food_type)
                seen.add(food_type)
        
        # Add any additional types from database
        for food_type in inventory_types + log_types:
            if food_type and food_type not in seen:
                all_types.append(food_type)
                seen.add(food_type)
        
        return all_types
    
    def get_distinct_food_sizes(self) -> List[str]:
        """Get list of unique food sizes from inventory and feeding logs"""
        # Standard food sizes based on frozen food supplier (in logical order)
        standard_sizes = [
            'Pinkie',
            'Fuzzie',
            'Hopper',
            'Weaner',
            'Juvenile',
            'Small',
            'Adults',
            'Medium',
            'Large',
            'X Large',
            'Jumbo'
        ]
        
        # Get from inventory
        self.cursor.execute('SELECT DISTINCT food_size FROM food_inventory WHERE food_size IS NOT NULL ORDER BY food_size')
        inventory_sizes = [row['food_size'] for row in self.cursor.fetchall()]
        
        # Get from feeding logs
        self.cursor.execute('SELECT DISTINCT food_size FROM feeding_logs WHERE food_size IS NOT NULL ORDER BY food_size')
        log_sizes = [row['food_size'] for row in self.cursor.fetchall()]
        
        # Combine standard sizes with existing data, maintaining order and removing duplicates
        all_sizes = []
        seen = set()
        
        # Add standard sizes first (in proper order)
        for food_size in standard_sizes:
            if food_size not in seen:
                all_sizes.append(food_size)
                seen.add(food_size)
        
        # Add any additional sizes from database
        for food_size in inventory_sizes + log_sizes:
            if food_size and food_size not in seen:
                all_sizes.append(food_size)
                seen.add(food_size)
        
        return all_sizes
    
    def delete_feeding_log(self, log_id: int) -> bool:
        """Delete a feeding log entry"""
        self.cursor.execute('DELETE FROM feeding_logs WHERE id = ?', (log_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    
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
    
    # ==================== TANK CLEANING LOGS ====================
    
    def add_tank_cleaning_log(self, reptile_id: int, cleaning_date: str, 
                             cleaning_type: str, notes: str = None) -> int:
        """Add a tank cleaning log"""
        self.cursor.execute('''
            INSERT INTO tank_cleaning_logs (reptile_id, cleaning_date, cleaning_type, notes)
            VALUES (?, ?, ?, ?)
        ''', (reptile_id, cleaning_date, cleaning_type, notes))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_tank_cleaning_logs(self, reptile_id: int = None, limit: int = None) -> List[Dict]:
        """Get tank cleaning logs with optional filters"""
        query = '''
            SELECT tcl.*, r.name as reptile_name 
            FROM tank_cleaning_logs tcl
            JOIN reptiles r ON tcl.reptile_id = r.id
            WHERE 1=1
        '''
        params = []
        
        if reptile_id:
            query += ' AND tcl.reptile_id = ?'
            params.append(reptile_id)
        
        query += ' ORDER BY tcl.cleaning_date DESC'
        
        if limit:
            query += f' LIMIT {limit}'
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_last_tank_cleaning(self, reptile_id: int) -> Dict:
        """Get the most recent tank cleaning for a reptile"""
        logs = self.get_tank_cleaning_logs(reptile_id, limit=1)
        return logs[0] if logs else None
    
    def delete_tank_cleaning_log(self, log_id: int) -> bool:
        """Delete a tank cleaning log"""
        self.cursor.execute('DELETE FROM tank_cleaning_logs WHERE id = ?', (log_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    # ==================== HANDLING LOGS ====================
    
    def add_handling_log(self, reptile_id: int, handling_date: str, 
                        duration_minutes: int = None, behavior: str = None, 
                        notes: str = None) -> int:
        """Add a handling log"""
        self.cursor.execute('''
            INSERT INTO handling_logs (reptile_id, handling_date, duration_minutes, behavior, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (reptile_id, handling_date, duration_minutes, behavior, notes))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_handling_logs(self, reptile_id: int = None, limit: int = None) -> List[Dict]:
        """Get handling logs with optional filters"""
        query = '''
            SELECT hl.*, r.name as reptile_name 
            FROM handling_logs hl
            JOIN reptiles r ON hl.reptile_id = r.id
            WHERE 1=1
        '''
        params = []
        
        if reptile_id:
            query += ' AND hl.reptile_id = ?'
            params.append(reptile_id)
        
        query += ' ORDER BY hl.handling_date DESC'
        
        if limit:
            query += f' LIMIT {limit}'
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_last_handling(self, reptile_id: int) -> Dict:
        """Get the most recent handling for a reptile"""
        logs = self.get_handling_logs(reptile_id, limit=1)
        return logs[0] if logs else None
    
    def delete_handling_log(self, log_id: int) -> bool:
        """Delete a handling log"""
        self.cursor.execute('DELETE FROM handling_logs WHERE id = ?', (log_id,))
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
            
            # Try parsing with different date formats
            last_fed = None
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    last_fed = datetime.strptime(last_fed_date, fmt)
                    break
                except ValueError:
                    continue
            
            if not last_fed:
                # If parsing fails, use current date
                last_fed = datetime.now()
            
            next_feeding = last_fed + timedelta(days=reminder['feeding_interval_days'])
            
            # Store only the date part (no time)
            last_fed_date_only = last_fed.strftime('%Y-%m-%d')
            
            self.cursor.execute('''
                UPDATE feeding_reminders
                SET last_fed_date = ?, next_feeding_date = ?
                WHERE reptile_id = ?
            ''', (last_fed_date_only, next_feeding.strftime('%Y-%m-%d'), reptile_id))
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
            SELECT fr.*, r.name as reptile_name, r.species,
                   julianday(?) - julianday(fr.next_feeding_date) as days_overdue
            FROM feeding_reminders fr
            JOIN reptiles r ON fr.reptile_id = r.id
            WHERE fr.is_active = 1
            AND fr.next_feeding_date IS NOT NULL
            AND fr.next_feeding_date <= ?
            ORDER BY fr.next_feeding_date ASC
        ''', (today, today))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_upcoming_feedings(self, days_ahead: int = 7) -> List[Dict]:
        """Get reptiles with upcoming feedings in the next X days (not overdue)"""
        from datetime import datetime, timedelta
        today = datetime.now().strftime('%Y-%m-%d')
        future_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        
        self.cursor.execute('''
            SELECT fr.*, r.name as reptile_name, r.species,
                   julianday(fr.next_feeding_date) - julianday(?) as days_until
            FROM feeding_reminders fr
            JOIN reptiles r ON fr.reptile_id = r.id
            WHERE fr.is_active = 1
            AND fr.next_feeding_date IS NOT NULL
            AND fr.next_feeding_date > ?
            AND fr.next_feeding_date <= ?
            ORDER BY fr.next_feeding_date ASC
        ''', (today, today, future_date))
        
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
    
    # ==================== SHOPPING LIST & FOOD UPGRADE OPERATIONS ====================
    
    def get_shopping_list(self, days_ahead: int = 30) -> List[Dict]:
        """
        Calculate food needs based on feeding schedules for the next X days
        Returns list of food items needed with quantities
        """
        from datetime import datetime, timedelta
        
        logger.info(f"=== SHOPPING LIST CALCULATION START (days_ahead={days_ahead}) ===")
        
        today = get_current_date()
        future_date = (datetime.strptime(today, '%Y-%m-%d') + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        
        # Get all active feeding reminders with food preferences
        self.cursor.execute('''
            SELECT
                fr.reptile_id,
                r.name as reptile_name,
                fr.food_type,
                fr.food_size,
                fr.quantity_per_feeding,
                fr.feeding_interval_days,
                fr.next_feeding_date
            FROM feeding_reminders fr
            JOIN reptiles r ON fr.reptile_id = r.id
            WHERE fr.is_active = 1
                AND fr.food_type IS NOT NULL
                AND fr.food_size IS NOT NULL
                AND fr.next_feeding_date IS NOT NULL
        ''')
        
        reminders = [dict(row) for row in self.cursor.fetchall()]
        logger.info(f"Found {len(reminders)} active feeding reminders with food preferences")
        
        for reminder in reminders:
            logger.info(f"  - {reminder['reptile_name']}: {reminder['food_type']} {reminder['food_size']}, "
                       f"next feeding: {reminder['next_feeding_date']}, interval: {reminder['feeding_interval_days']} days")
        
        # Calculate total feedings for each reptile in the time period
        food_needs = {}
        today_date = datetime.strptime(today, '%Y-%m-%d')
        
        for reminder in reminders:
            # Calculate how many feedings will occur in the time period
            next_feeding = datetime.strptime(reminder['next_feeding_date'], '%Y-%m-%d')
            end_date = datetime.strptime(future_date, '%Y-%m-%d')
            interval_days = reminder['feeding_interval_days']
            
            # Start counting from today or next feeding date, whichever is later
            start_date = max(today_date, next_feeding)
            
            feedings_count = 0
            current_date = start_date
            
            while current_date <= end_date:
                feedings_count += 1
                current_date += timedelta(days=interval_days)
            
            logger.info(f"  {reminder['reptile_name']}: {feedings_count} feedings calculated")
            
            if feedings_count > 0:
                food_key = (reminder['food_type'], reminder['food_size'])
                quantity_needed = feedings_count * reminder['quantity_per_feeding']
                
                if food_key in food_needs:
                    food_needs[food_key]['quantity_needed'] += quantity_needed
                    food_needs[food_key]['reptiles'].append({
                        'name': reminder['reptile_name'],
                        'feedings': feedings_count,
                        'quantity': quantity_needed
                    })
                else:
                    food_needs[food_key] = {
                        'food_type': reminder['food_type'],
                        'food_size': reminder['food_size'],
                        'quantity_needed': quantity_needed,
                        'reptiles': [{
                            'name': reminder['reptile_name'],
                            'feedings': feedings_count,
                            'quantity': quantity_needed
                        }]
                    }
        
        logger.info(f"Total unique food types needed: {len(food_needs)}")
        
        # Get current inventory levels
        shopping_list = []
        for food_key, needs in food_needs.items():
            food_type, food_size = food_key
            
            # Check current inventory
            inventory_item = self.get_food_item_by_type(food_type, food_size)
            current_stock = inventory_item['quantity'] if inventory_item else 0
            
            # Debug logging
            if not inventory_item:
                logger.warning(f"No inventory found for: {food_type} - {food_size}")
            else:
                logger.info(f"Found inventory: {food_type} - {food_size} = {current_stock}")
            
            shortage = needs['quantity_needed'] - current_stock
            
            shopping_list.append({
                'food_type': food_type,
                'food_size': food_size,
                'quantity_needed': needs['quantity_needed'],
                'current_stock': current_stock,
                'shortage': max(0, shortage),
                'reptiles': needs['reptiles']
            })
        
        # Sort by shortage (highest first)
        shopping_list.sort(key=lambda x: x['shortage'], reverse=True)
        
        return shopping_list
    
    def get_reptile_food_preference(self, reptile_id: int) -> Optional[Dict]:
        """Get current food preference from feeding reminder"""
        self.cursor.execute('''
            SELECT food_type, food_size, quantity_per_feeding
            FROM feeding_reminders
            WHERE reptile_id = ?
        ''', (reptile_id,))
        
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def upgrade_reptile_food(self, reptile_id: int, new_food_type: str, 
                            new_food_size: str, quantity_per_feeding: int = 1) -> bool:
        """
        Upgrade a reptile's food type/size and update their feeding schedule
        Returns True if successful
        """
        try:
            # Update feeding reminder with new food preferences
            self.cursor.execute('''
                UPDATE feeding_reminders
                SET food_type = ?,
                    food_size = ?,
                    quantity_per_feeding = ?
                WHERE reptile_id = ?
            ''', (new_food_type, new_food_size, quantity_per_feeding, reptile_id))
            
            self.conn.commit()
            return self.cursor.rowcount > 0
            
        except Exception as e:
            print(f"[ERROR] Failed to upgrade food: {str(e)}")
            return False

    
    # ==================== LENGTH HISTORY OPERATIONS ====================
    
    def add_length_measurement(self, reptile_id: int, measurement_date: str,
                              length_cm: float, notes: str = None) -> int:
        """Add a length measurement"""
        self.cursor.execute('''
            INSERT INTO length_history (reptile_id, measurement_date, length_cm, notes)
            VALUES (?, ?, ?, ?)
        ''', (reptile_id, measurement_date, length_cm, notes))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_length_history(self, reptile_id: int, limit: int = None) -> List[Dict]:
        """Get length history for a reptile"""
        query = '''
            SELECT * FROM length_history 
            WHERE reptile_id = ?
            ORDER BY measurement_date DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        self.cursor.execute(query, (reptile_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_length_chart_data(self, reptile_id: int) -> Dict:
        """Get length data formatted for charts"""
        self.cursor.execute('''
            SELECT measurement_date, length_cm 
            FROM length_history 
            WHERE reptile_id = ?
            ORDER BY measurement_date ASC
        ''', (reptile_id,))
        
        data = self.cursor.fetchall()
        return {
            'dates': [row['measurement_date'] for row in data],
            'lengths': [row['length_cm'] for row in data]
        }
    
    # ==================== NOTIFICATION SETTINGS OPERATIONS ====================
    
    def get_notification_settings(self) -> Optional[Dict]:
        """Get notification settings"""
        self.cursor.execute('SELECT * FROM notification_settings LIMIT 1')
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def save_notification_settings(self, email_enabled: bool = False, email: str = None,
                                   sms_enabled: bool = False, phone: str = None,
                                   reminder_time: str = '09:00', advance_notice: int = 0,
                                   notify_overdue_only: bool = False) -> bool:
        """Save or update notification settings"""
        # Check if settings exist
        existing = self.get_notification_settings()
        
        if existing:
            # Update existing settings
            self.cursor.execute('''
                UPDATE notification_settings 
                SET email_enabled = ?, email = ?, sms_enabled = ?, phone = ?,
                    reminder_time = ?, advance_notice = ?, notify_overdue_only = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (email_enabled, email, sms_enabled, phone, reminder_time, 
                  advance_notice, notify_overdue_only, existing['id']))
        else:
            # Insert new settings
            self.cursor.execute('''
                INSERT INTO notification_settings 
                (email_enabled, email, sms_enabled, phone, reminder_time, 
                 advance_notice, notify_overdue_only)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (email_enabled, email, sms_enabled, phone, reminder_time,
                  advance_notice, notify_overdue_only))
        
        self.conn.commit()
        return True
    
    # ==================== EXPENSE OPERATIONS ====================
    
    def add_expense(self, expense_date: str, category: str, amount: float,
                   reptile_id: int = None, currency: str = 'USD', vendor: str = None,
                   description: str = None, receipt_path: str = None,
                   payment_method: str = None, is_recurring: bool = False,
                   tags: str = None, notes: str = None) -> int:
        """Add a new expense record"""
        self.cursor.execute('''
            INSERT INTO expenses (reptile_id, expense_date, category, amount, currency,
                                vendor, description, receipt_path, payment_method,
                                is_recurring, tags, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (reptile_id, expense_date, category, amount, currency, vendor,
              description, receipt_path, payment_method, is_recurring, tags, notes))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_expense(self, expense_id: int) -> Optional[Dict]:
        """Get a single expense by ID"""
        self.cursor.execute('''
            SELECT e.*, r.name as reptile_name
            FROM expenses e
            LEFT JOIN reptiles r ON e.reptile_id = r.id
            WHERE e.id = ?
        ''', (expense_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_expenses(self, reptile_id: int = None, category: str = None,
                    start_date: str = None, end_date: str = None,
                    limit: int = None, offset: int = 0) -> List[Dict]:
        """Get expenses with optional filtering"""
        query = '''
            SELECT e.*, r.name as reptile_name
            FROM expenses e
            LEFT JOIN reptiles r ON e.reptile_id = r.id
            WHERE 1=1
        '''
        params = []
        
        if reptile_id:
            query += ' AND e.reptile_id = ?'
            params.append(reptile_id)
        
        if category:
            query += ' AND e.category = ?'
            params.append(category)
        
        if start_date:
            query += ' AND e.expense_date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND e.expense_date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY e.expense_date DESC, e.created_at DESC'
        
        if limit:
            query += ' LIMIT ? OFFSET ?'
            params.extend([limit, offset])
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_expense(self, expense_id: int, **kwargs) -> bool:
        """Update expense information"""
        allowed_fields = ['reptile_id', 'expense_date', 'category', 'amount', 'currency',
                         'vendor', 'description', 'receipt_path', 'payment_method',
                         'is_recurring', 'tags', 'notes']
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [expense_id]
        
        self.cursor.execute(f'''
            UPDATE expenses 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', values)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense record"""
        self.cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def get_expense_categories(self) -> List[str]:
        """Get list of unique expense categories"""
        self.cursor.execute('SELECT DISTINCT category FROM expenses ORDER BY category')
        return [row['category'] for row in self.cursor.fetchall()]
    
    def get_expense_summary(self, start_date: str = None, end_date: str = None,
                           reptile_id: int = None) -> Dict:
        """Get expense summary statistics"""
        query = 'SELECT COUNT(*) as count, SUM(amount) as total, AVG(amount) as average FROM expenses WHERE 1=1'
        params = []
        
        if reptile_id:
            query += ' AND reptile_id = ?'
            params.append(reptile_id)
        
        if start_date:
            query += ' AND expense_date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND expense_date <= ?'
            params.append(end_date)
        
        self.cursor.execute(query, params)
        row = self.cursor.fetchone()
        
        return {
            'count': row['count'] or 0,
            'total': row['total'] or 0.0,
            'average': row['average'] or 0.0
        }
    
    def get_expenses_by_category(self, start_date: str = None, end_date: str = None,
                                 reptile_id: int = None) -> List[Dict]:
        """Get expense totals grouped by category"""
        query = '''
            SELECT category, COUNT(*) as count, SUM(amount) as total
            FROM expenses
            WHERE 1=1
        '''
        params = []
        
        if reptile_id:
            query += ' AND reptile_id = ?'
            params.append(reptile_id)
        
        if start_date:
            query += ' AND expense_date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND expense_date <= ?'
            params.append(end_date)
        
        query += ' GROUP BY category ORDER BY total DESC'
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== FOOD INVENTORY OPERATIONS ====================
    
    def add_food_item(self, food_type: str, food_size: str, quantity: int,
                     unit: str = 'items', cost_per_unit: float = None,
                     supplier: str = None, purchase_date: str = None,
                     expiry_date: str = None, notes: str = None) -> int:
        """Add or update food inventory item"""
        # Check if item already exists
        self.cursor.execute('''
            SELECT id, quantity FROM food_inventory 
            WHERE food_type = ? AND food_size = ?
        ''', (food_type, food_size))
        existing = self.cursor.fetchone()
        
        if existing:
            # Update existing item - add to quantity
            new_quantity = existing['quantity'] + quantity
            self.cursor.execute('''
                UPDATE food_inventory 
                SET quantity = ?, cost_per_unit = ?, supplier = ?,
                    purchase_date = ?, expiry_date = ?, notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_quantity, cost_per_unit, supplier, purchase_date,
                  expiry_date, notes, existing['id']))
            inventory_id = existing['id']
        else:
            # Insert new item
            self.cursor.execute('''
                INSERT INTO food_inventory (food_type, food_size, quantity, unit,
                                          cost_per_unit, supplier, purchase_date,
                                          expiry_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (food_type, food_size, quantity, unit, cost_per_unit,
                  supplier, purchase_date, expiry_date, notes))
            inventory_id = self.cursor.lastrowid
        
        # Log transaction
        self.cursor.execute('''
            INSERT INTO inventory_transactions (inventory_id, transaction_type,
                                               quantity, transaction_date, notes)
            VALUES (?, 'purchase', ?, ?, ?)
        ''', (inventory_id, quantity, purchase_date or get_current_date(),
              f'Added {quantity} {unit}'))
        
        self.conn.commit()
        return inventory_id
    
    def get_food_inventory(self, include_zero: bool = False) -> List[Dict]:
        """Get all food inventory items"""
        query = 'SELECT * FROM food_inventory'
        if not include_zero:
            query += ' WHERE quantity > 0'
        query += ' ORDER BY food_type, food_size'
        
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_food_item(self, inventory_id: int) -> Optional[Dict]:
        """Get a single food inventory item"""
        self.cursor.execute('SELECT * FROM food_inventory WHERE id = ?', (inventory_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_food_item_by_type(self, food_type: str, food_size: str) -> Optional[Dict]:
        """Get food item by type and size (case-insensitive)"""
        # Debug: show what we're searching for
        logger.info(f"Searching inventory for: type='{food_type}', size='{food_size}'")
        
        # Debug: show all inventory items
        self.cursor.execute('SELECT food_type, food_size, quantity FROM food_inventory')
        all_items = self.cursor.fetchall()
        logger.info(f"All inventory items in database:")
        for item in all_items:
            logger.info(f"  - type='{item[0]}', size='{item[1]}', qty={item[2]}")
        
        self.cursor.execute('''
            SELECT * FROM food_inventory
            WHERE LOWER(food_type) = LOWER(?) AND LOWER(food_size) = LOWER(?)
        ''', (food_type, food_size))
        row = self.cursor.fetchone()
        
        if row:
            logger.info(f"Match found: {dict(row)}")
        else:
            logger.warning(f"No match found for: {food_type} - {food_size}")
        
        return dict(row) if row else None
    
    def update_food_quantity(self, inventory_id: int, quantity_change: int,
                            transaction_type: str = 'adjustment',
                            reference_id: int = None, reference_type: str = None,
                            notes: str = None) -> bool:
        """Update food inventory quantity (positive to add, negative to subtract)"""
        # Get current quantity
        item = self.get_food_item(inventory_id)
        if not item:
            return False
        
        new_quantity = item['quantity'] + quantity_change
        if new_quantity < 0:
            new_quantity = 0  # Don't allow negative quantities
        
        # Update quantity
        self.cursor.execute('''
            UPDATE food_inventory 
            SET quantity = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_quantity, inventory_id))
        
        # Log transaction
        self.cursor.execute('''
            INSERT INTO inventory_transactions (inventory_id, transaction_type,
                                               quantity, transaction_date,
                                               reference_id, reference_type, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (inventory_id, transaction_type, quantity_change, get_current_date(),
              reference_id, reference_type, notes))
        
        self.conn.commit()
        return True
    
    def deduct_food_from_feeding(self, food_type: str, food_size: str,
                                quantity: int, feeding_log_id: int) -> bool:
        """Deduct food from inventory when logging a feeding"""
        item = self.get_food_item_by_type(food_type, food_size)
        if not item:
            return False
        
        return self.update_food_quantity(
            item['id'],
            -quantity,  # Negative to subtract
            transaction_type='feeding',
            reference_id=feeding_log_id,
            reference_type='feeding_log',
            notes=f'Fed {quantity} {food_size} {food_type}'
        )
    
    def get_inventory_transactions(self, inventory_id: int = None,
                                   limit: int = None) -> List[Dict]:
        """Get inventory transaction history"""
        query = '''
            SELECT t.*, i.food_type, i.food_size
            FROM inventory_transactions t
            JOIN food_inventory i ON t.inventory_id = i.id
        '''
        params = []
        
        if inventory_id:
            query += ' WHERE t.inventory_id = ?'
            params.append(inventory_id)
        
        query += ' ORDER BY t.transaction_date DESC, t.created_at DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_low_stock_items(self, threshold: int = 5) -> List[Dict]:
        """Get food items with low stock"""
        self.cursor.execute('''
            SELECT * FROM food_inventory 
            WHERE quantity <= ? AND quantity > 0
            ORDER BY quantity ASC
        ''', (threshold,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_out_of_stock_items(self) -> List[Dict]:
        """Get food items that are out of stock"""
        self.cursor.execute('''
            SELECT * FROM food_inventory 
            WHERE quantity = 0
            ORDER BY food_type, food_size
        ''')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_inventory_forecast(self, inventory_id: int = None, days_lookback: int = 30) -> List[Dict]:
        """
        Calculate consumption forecast for inventory items
        Returns forecast data including consumption rate and estimated days until depletion
        """
        forecasts = []
        
        # Get inventory items to forecast
        if inventory_id:
            items = [self.get_food_item(inventory_id)]
            if not items[0]:
                return []
        else:
            items = self.get_food_inventory(include_zero=False)
        
        # Calculate forecast for each item
        for item in items:
            # Get consumption data from feeding logs (last N days)
            self.cursor.execute('''
                SELECT 
                    COUNT(*) as feeding_count,
                    SUM(quantity) as total_consumed,
                    MIN(feeding_date) as first_feeding,
                    MAX(feeding_date) as last_feeding
                FROM feeding_logs
                WHERE inventory_id = ?
                    AND auto_deducted = 1
                    AND ate = 1
                    AND feeding_date >= date('now', '-' || ? || ' days')
            ''', (item['id'], days_lookback))
            
            consumption_data = dict(self.cursor.fetchone())
            
            # Calculate consumption rate
            total_consumed = consumption_data['total_consumed'] or 0
            feeding_count = consumption_data['feeding_count'] or 0
            
            if feeding_count > 0 and consumption_data['first_feeding'] and consumption_data['last_feeding']:
                # Calculate days between first and last feeding
                from datetime import datetime
                first_date = datetime.strptime(consumption_data['first_feeding'], '%Y-%m-%d')
                last_date = datetime.strptime(consumption_data['last_feeding'], '%Y-%m-%d')
                days_span = (last_date - first_date).days + 1  # +1 to include both days
                
                if days_span > 0:
                    # Average consumption per day
                    consumption_per_day = total_consumed / days_span
                    
                    # Days until depletion
                    if consumption_per_day > 0:
                        days_remaining = item['quantity'] / consumption_per_day
                    else:
                        days_remaining = None
                    
                    # Estimated depletion date
                    if days_remaining:
                        from datetime import timedelta
                        depletion_date = datetime.now() + timedelta(days=days_remaining)
                        depletion_date_str = depletion_date.strftime('%Y-%m-%d')
                    else:
                        depletion_date_str = None
                else:
                    consumption_per_day = 0
                    days_remaining = None
                    depletion_date_str = None
            else:
                consumption_per_day = 0
                days_remaining = None
                depletion_date_str = None
            
            # Determine status
            if days_remaining is None:
                status = 'unknown'
                status_class = 'secondary'
            elif days_remaining <= 7:
                status = 'critical'
                status_class = 'danger'
            elif days_remaining <= 14:
                status = 'low'
                status_class = 'warning'
            else:
                status = 'good'
                status_class = 'success'
            
            # Calculate reorder suggestion
            if consumption_per_day > 0:
                # Suggest reordering when 14 days of stock remain
                reorder_threshold = consumption_per_day * 14
                needs_reorder = item['quantity'] <= reorder_threshold
                suggested_order_qty = max(int(consumption_per_day * 30), 10)  # 30 days worth, minimum 10
            else:
                needs_reorder = False
                suggested_order_qty = 10
            
            forecasts.append({
                'inventory_id': item['id'],
                'food_type': item['food_type'],
                'food_size': item['food_size'],
                'current_quantity': item['quantity'],
                'feeding_count': feeding_count,
                'total_consumed': total_consumed,
                'days_analyzed': days_lookback,
                'consumption_per_day': round(consumption_per_day, 2),
                'days_remaining': int(days_remaining) if days_remaining else None,
                'depletion_date': depletion_date_str,
                'status': status,
                'status_class': status_class,
                'needs_reorder': needs_reorder,
                'suggested_order_qty': suggested_order_qty
            })
        
        return forecasts
    
    def delete_food_item(self, inventory_id: int) -> bool:
        """Delete a food inventory item"""
        self.cursor.execute('DELETE FROM food_inventory WHERE id = ?', (inventory_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    # ==================== PURCHASE RECEIPT OPERATIONS ====================
    
    def add_purchase_receipt(self, receipt_date: str, items: List[Dict],
                            supplier: str = None, payment_method: str = None,
                            notes: str = None, image_path: str = None,
                            ocr_text: str = None) -> int:
        """
        Add a purchase receipt with multiple items and update inventory
        
        items format: [
            {'food_type': 'Rat', 'food_size': 'Large', 'quantity': 10, 'cost_per_unit': 5.00},
            ...
        ]
        """
        # Calculate total cost
        total_cost = sum(item['quantity'] * item.get('cost_per_unit', 0) for item in items)
        
        # Insert receipt
        self.cursor.execute('''
            INSERT INTO purchase_receipts (receipt_date, supplier, total_cost, payment_method, notes, image_path, ocr_text)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (receipt_date, supplier, total_cost, payment_method, notes, image_path, ocr_text))
        self.conn.commit()
        receipt_id = self.cursor.lastrowid
        
        # Insert receipt items and update inventory
        for item in items:
            food_type = item['food_type']
            food_size = item['food_size']
            quantity = item['quantity']
            cost_per_unit = item.get('cost_per_unit', 0)
            item_total = quantity * cost_per_unit
            
            # Insert receipt item
            self.cursor.execute('''
                INSERT INTO receipt_items (receipt_id, food_type, food_size, quantity, cost_per_unit, total_cost)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (receipt_id, food_type, food_size, quantity, cost_per_unit, item_total))
            
            # Add to inventory (this will auto-increment if exists)
            self.add_food_item(
                food_type=food_type,
                food_size=food_size,
                quantity=quantity,
                cost_per_unit=cost_per_unit,
                supplier=supplier,
                purchase_date=receipt_date
            )
        
        self.conn.commit()
        return receipt_id
    
    def get_purchase_receipt(self, receipt_id: int) -> Optional[Dict]:
        """Get a single purchase receipt with its items"""
        # Get receipt
        self.cursor.execute('SELECT * FROM purchase_receipts WHERE id = ?', (receipt_id,))
        receipt_row = self.cursor.fetchone()
        if not receipt_row:
            return None
        
        receipt = dict(receipt_row)
        
        # Get receipt items
        self.cursor.execute('''
            SELECT * FROM receipt_items WHERE receipt_id = ? ORDER BY id
        ''', (receipt_id,))
        receipt['items'] = [dict(row) for row in self.cursor.fetchall()]
        
        return receipt
    
    def get_purchase_receipts(self, limit: int = None) -> List[Dict]:
        """Get all purchase receipts"""
        query = 'SELECT * FROM purchase_receipts ORDER BY receipt_date DESC, id DESC'
        if limit:
            query += f' LIMIT {limit}'
        
        self.cursor.execute(query)
        receipts = [dict(row) for row in self.cursor.fetchall()]
        
        # Get item count for each receipt
        for receipt in receipts:
            self.cursor.execute('''
                SELECT COUNT(*) as item_count, SUM(quantity) as total_items
                FROM receipt_items WHERE receipt_id = ?
            ''', (receipt['id'],))
            counts = self.cursor.fetchone()
            receipt['item_count'] = counts['item_count']
            receipt['total_items'] = counts['total_items']
        
        return receipts
    
    def delete_purchase_receipt(self, receipt_id: int) -> bool:
        """Delete a purchase receipt (items will be cascade deleted)"""
        self.cursor.execute('DELETE FROM purchase_receipts WHERE id = ?', (receipt_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    
    def get_monthly_expenses(self, year: int = None, reptile_id: int = None) -> List[Dict]:
        """Get expense totals by month"""
        if not year:
            year = datetime.now().year
        
        query = '''
            SELECT 
                strftime('%m', expense_date) as month,
                strftime('%Y-%m', expense_date) as year_month,
                COUNT(*) as count,
                SUM(amount) as total
            FROM expenses
            WHERE strftime('%Y', expense_date) = ?
        '''
        params = [str(year)]
        
        if reptile_id:
            query += ' AND reptile_id = ?'
            params.append(reptile_id)
        
        query += ' GROUP BY year_month ORDER BY year_month'
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]



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
