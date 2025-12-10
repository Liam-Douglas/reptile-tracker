"""
Reptile Tracker - Main GUI Application
A comprehensive desktop application for tracking reptile care, feeding, and shedding
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import csv
import os
import shutil
from reptile_tracker_db import ReptileDatabase, get_current_date, calculate_age
from typing import Optional
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ReptileTrackerApp:
    """Main application class for Reptile Tracker"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Reptile Tracker")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2C2C2C')
        
        # Initialize database
        self.db = ReptileDatabase()
        
        # Current view state
        self.current_view = None
        self.selected_reptile_id = None
        
        # Color scheme
        self.colors = {
            'bg_dark': '#2C2C2C',
            'bg_medium': '#3A3A3A',
            'bg_light': '#4A4A4A',
            'accent': '#4ECDC4',
            'accent_hover': '#71D7D0',
            'success': '#96CEB4',
            'warning': '#FFD93D',
            'danger': '#FF6B6B',
            'text': 'white',
            'text_secondary': '#CCCCCC'
        }
        
        # Setup UI
        self.create_menu_bar()
        self.create_sidebar()
        self.create_main_content_area()
        
        # Show dashboard by default
    
    # ==================== IMAGE HANDLING METHODS ====================
    
    def select_reptile_image(self, fields):
        """Open file dialog to select an image for a reptile"""
        if not PIL_AVAILABLE:
            messagebox.showwarning(
                "PIL Not Available",
                "Image support requires Pillow library.\n\n"
                "Install with: pip install Pillow"
            )
            return None
        
        file_path = filedialog.askopenfilename(
            title="Select Reptile Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            fields['selected_image_path'] = file_path
            # Update button text to show image selected
            if 'image_button' in fields:
                filename = os.path.basename(file_path)
                fields['image_button'].config(text=f"✓ {filename[:20]}...")
        
        return file_path
    
    def save_reptile_image(self, source_path, reptile_id):
        """Copy image to reptile_images folder with unique name"""
        if not source_path or not os.path.exists(source_path):
            return None
        
        try:
            # Create reptile_images directory if it doesn't exist
            images_dir = "reptile_images"
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
            
            # Get file extension
            _, ext = os.path.splitext(source_path)
            
            # Create unique filename
            filename = f"reptile_{reptile_id}{ext}"
            dest_path = os.path.join(images_dir, filename)
            
            # Copy and resize image
            if PIL_AVAILABLE:
                img = Image.open(source_path)
                # Resize if too large (max 800x800)
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                img.save(dest_path, quality=85, optimize=True)
            else:
                # Just copy if PIL not available
                shutil.copy2(source_path, dest_path)
            
            return dest_path
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
            return None
    
    def load_reptile_image(self, image_path, size=(150, 150)):
        """Load and resize image for display"""
        if not PIL_AVAILABLE or not image_path or not os.path.exists(image_path):
            return None
        
        try:
            img = Image.open(image_path)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    def create_placeholder_image(self, size=(150, 150)):
        """Create a placeholder image when no photo is available"""
        if not PIL_AVAILABLE:
            return None
        
        try:
            # Create a simple placeholder
            img = Image.new('RGB', size, color=self.colors['bg_light'])
            return ImageTk.PhotoImage(img)
        except:
            return None
        self.show_dashboard()
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import CSV", command=self.import_csv)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Reptiles menu
        reptiles_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reptiles", menu=reptiles_menu)
        reptiles_menu.add_command(label="Add New Reptile", command=self.show_add_reptile_form)
        reptiles_menu.add_command(label="View All Reptiles", command=self.show_dashboard)
        
        # Records menu
        records_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Records", menu=records_menu)
        records_menu.add_command(label="Feeding Logs", command=self.show_feeding_logs)
        records_menu.add_command(label="Shed Records", command=self.show_shed_records)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_sidebar(self):
        """Create the navigation sidebar"""
        self.sidebar = tk.Frame(self.root, bg=self.colors['bg_medium'], width=200)
        self.sidebar.pack(side='left', fill='y', padx=0, pady=0)
        self.sidebar.pack_propagate(False)
        
        # App title
        title_label = tk.Label(
            self.sidebar,
            text="🦎 Reptile\nTracker",
            font=('Arial', 18, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent'],
            pady=20
        )
        title_label.pack()
        
        # Navigation buttons
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("🦎 Add Reptile", self.show_add_reptile_form),
            ("🍖 Feeding Logs", self.show_feeding_logs),
            ("🔄 Shed Records", self.show_shed_records),
            ("📥 Import Data", self.import_csv),
            ("📤 Export Data", self.export_data),
        ]
        
        for text, command in nav_buttons:
            btn = tk.Button(
                self.sidebar,
                text=text,
                command=command,
                font=('Arial', 11),
                bg=self.colors['bg_light'],
                fg=self.colors['text'],
                activebackground=self.colors['accent'],
                activeforeground='white',
                bd=0,
                pady=12,
                cursor='hand2',
                anchor='w',
                padx=20
            )
            btn.pack(fill='x', padx=10, pady=5)
    
    def create_main_content_area(self):
        """Create the main content display area"""
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg_dark'])
        self.main_frame.pack(side='right', fill='both', expand=True)
    
    def clear_main_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    # ==================== DASHBOARD VIEW ====================
    
    def show_dashboard(self):
        """Display the main dashboard with reptile cards"""
        self.clear_main_frame()
        self.current_view = 'dashboard'
        
        # Header
        header_frame = tk.Frame(self.main_frame, bg=self.colors['bg_dark'])
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            header_frame,
            text="Dashboard",
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).pack(side='left')
        
        # Stats cards
        stats = self.db.get_dashboard_stats()
        stats_frame = tk.Frame(self.main_frame, bg=self.colors['bg_dark'])
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        stat_items = [
            ("Total Reptiles", stats['total_reptiles'], self.colors['accent']),
            ("Recent Feedings (7d)", stats['recent_feedings'], self.colors['success']),
            ("Recent Sheds (30d)", stats['recent_sheds'], self.colors['warning']),
            ("Needs Feeding", stats['needs_feeding'], self.colors['danger'])
        ]
        
        for label, value, color in stat_items:
            self.create_stat_card(stats_frame, label, value, color)
        
        # Reptiles grid
        reptiles_frame = tk.Frame(self.main_frame, bg=self.colors['bg_dark'])
        reptiles_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Scrollable canvas for reptile cards
        canvas = tk.Canvas(reptiles_frame, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(reptiles_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Get all reptiles
        reptiles = self.db.get_all_reptiles()
        
        if not reptiles:
            tk.Label(
                scrollable_frame,
                text="No reptiles added yet. Click 'Add Reptile' to get started!",
                font=('Arial', 14),
                bg=self.colors['bg_dark'],
                fg=self.colors['text_secondary'],
                pady=50
            ).pack()
        else:
            # Create reptile cards in a grid
            row = 0
            col = 0
            for reptile in reptiles:
                self.create_reptile_card(scrollable_frame, reptile, row, col)
                col += 1
                if col >= 3:  # 3 cards per row
                    col = 0
                    row += 1
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_stat_card(self, parent, label, value, color):
        """Create a statistics card"""
        card = tk.Frame(parent, bg=self.colors['bg_medium'], relief='flat', bd=0)
        card.pack(side='left', padx=10, pady=5, fill='x', expand=True)
        
        tk.Label(
            card,
            text=str(value),
            font=('Arial', 32, 'bold'),
            bg=self.colors['bg_medium'],
            fg=color
        ).pack(pady=(15, 5))
        
        tk.Label(
            card,
            text=label,
            font=('Arial', 11),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_secondary']
        ).pack(pady=(0, 15))
    
    def create_reptile_card(self, parent, reptile, row, col):
        """Create a reptile information card"""
        card = tk.Frame(
            parent,
            bg=self.colors['bg_medium'],
            relief='flat',
            bd=0,
            cursor='hand2'
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        # Configure grid weights
        parent.grid_columnconfigure(col, weight=1)
        # Reptile image
        if reptile.get('image_path') and os.path.exists(reptile['image_path']):
            photo = self.load_reptile_image(reptile['image_path'], size=(100, 100))
            if photo:
                # Keep reference to prevent garbage collection
                img_label = tk.Label(card, image=photo, bg=self.colors['bg_medium'])
                img_label.image = photo  # Keep a reference!
                img_label.pack(pady=(10, 5))
        else:
            # Show placeholder or emoji if no image
            tk.Label(
                card,
                text="🦎",
                font=('Arial', 40),
                bg=self.colors['bg_medium'],
                fg=self.colors['accent']
            ).pack(pady=(10, 5))
        
        
        # Reptile name
        name_label = tk.Label(
            card,
            text=reptile['name'],
            font=('Arial', 16, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        )
        name_label.pack(pady=(15, 5))
        
        # Species
        tk.Label(
            card,
            text=reptile['species'],
            font=('Arial', 11),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent']
        ).pack()
        
        # Age
        age = calculate_age(reptile['date_of_birth'])
        if age:
            tk.Label(
                card,
                text=f"Age: {age}",
                font=('Arial', 10),
                bg=self.colors['bg_medium'],
                fg=self.colors['text_secondary']
            ).pack(pady=5)
        
        # Stats
        stats = self.db.get_reptile_stats(reptile['id'])
        
        stats_frame = tk.Frame(card, bg=self.colors['bg_medium'])
        stats_frame.pack(pady=10)
        
        # Last feeding
        if stats['last_feeding']:
            last_feed = stats['last_feeding']['feeding_date']
            tk.Label(
                stats_frame,
                text=f"Last fed: {last_feed}",
                font=('Arial', 9),
                bg=self.colors['bg_medium'],
                fg=self.colors['text_secondary']
            ).pack()
        
        # Buttons
        btn_frame = tk.Frame(card, bg=self.colors['bg_medium'])
        btn_frame.pack(pady=(10, 15))
        
        tk.Button(
            btn_frame,
            text="View Details",
            command=lambda r=reptile: self.show_reptile_details(r['id']),
            bg=self.colors['accent'],
            fg='white',
            font=('Arial', 9, 'bold'),
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="Add Feeding",
            command=lambda r=reptile: self.show_add_feeding_form(r['id']),
            bg=self.colors['success'],
            fg='white',
            font=('Arial', 9, 'bold'),
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side='left', padx=5)
    
    # ==================== REPTILE DETAILS VIEW ====================
    
    def show_reptile_details(self, reptile_id):
        """Show detailed view of a specific reptile"""
        self.clear_main_frame()
        self.current_view = 'reptile_details'
        self.selected_reptile_id = reptile_id
        
        reptile = self.db.get_reptile(reptile_id)
        if not reptile:
            messagebox.showerror("Error", "Reptile not found")
            self.show_dashboard()
            return
        
        # Header with back button
        header_frame = tk.Frame(self.main_frame, bg=self.colors['bg_dark'])
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Button(
            header_frame,
            text="← Back",
            command=self.show_dashboard,
            bg=self.colors['bg_medium'],
            fg=self.colors['text'],
            font=('Arial', 10),
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side='left', padx=(0, 20))
        
        tk.Label(
            header_frame,
            text=reptile['name'],
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).pack(side='left')
        
        # Action buttons
        tk.Button(
            header_frame,
            text="Edit",
            command=lambda: self.show_edit_reptile_form(reptile_id),
            bg=self.colors['accent'],
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side='right', padx=5)
        
        tk.Button(
            header_frame,
            text="Delete",
            command=lambda: self.delete_reptile(reptile_id),
            bg=self.colors['danger'],
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side='right', padx=5)
        
        # Content area with scrollbar
        content_canvas = tk.Canvas(self.main_frame, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=content_canvas.yview)
        content_frame = tk.Frame(content_canvas, bg=self.colors['bg_dark'])
        
        content_frame.bind(
            "<Configure>",
            lambda e: content_canvas.configure(scrollregion=content_canvas.bbox("all"))
        )
        
        content_canvas.create_window((0, 0), window=content_frame, anchor="nw")
        content_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Reptile information section
        info_frame = tk.Frame(content_frame, bg=self.colors['bg_medium'])
        # Reptile image section
        if reptile.get('image_path') and os.path.exists(reptile['image_path']):
            image_frame = tk.Frame(content_frame, bg=self.colors['bg_medium'])
            image_frame.pack(fill='x', padx=20, pady=10)
            
            photo = self.load_reptile_image(reptile['image_path'], size=(200, 200))
            if photo:
                img_label = tk.Label(image_frame, image=photo, bg=self.colors['bg_medium'])
                img_label.image = photo  # Keep reference
                img_label.pack(pady=15)
        
        info_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            info_frame,
            text="Basic Information",
            font=('Arial', 16, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=15, pady=(15, 10))
        
        info_items = [
            ("Species", reptile['species']),
            ("Morph", reptile['morph'] or "N/A"),
            ("Sex", reptile['sex'] or "Unknown"),
            ("Date of Birth", reptile['date_of_birth'] or "Unknown"),
            ("Age", calculate_age(reptile['date_of_birth']) or "Unknown"),
            ("Acquisition Date", reptile['acquisition_date'] or "Unknown"),
            ("Weight", f"{reptile['weight_grams']}g" if reptile['weight_grams'] else "Not recorded"),
            ("Length", f"{reptile['length_cm']}cm" if reptile['length_cm'] else "Not recorded"),
        ]
        
        for label, value in info_items:
            row_frame = tk.Frame(info_frame, bg=self.colors['bg_medium'])
            row_frame.pack(fill='x', padx=15, pady=5)
            
            tk.Label(
                row_frame,
                text=f"{label}:",
                font=('Arial', 11, 'bold'),
                bg=self.colors['bg_medium'],
                fg=self.colors['text_secondary'],
                width=20,
                anchor='w'
            ).pack(side='left')
            
            tk.Label(
                row_frame,
                text=str(value),
                font=('Arial', 11),
                bg=self.colors['bg_medium'],
                fg=self.colors['text']
            ).pack(side='left')
        
        if reptile['notes']:
            tk.Label(
                info_frame,
                text="Notes:",
                font=('Arial', 11, 'bold'),
                bg=self.colors['bg_medium'],
                fg=self.colors['text_secondary'],
                anchor='w'
            ).pack(fill='x', padx=15, pady=(10, 5))
            
            tk.Label(
                info_frame,
                text=reptile['notes'],
                font=('Arial', 10),
                bg=self.colors['bg_medium'],
                fg=self.colors['text'],
                wraplength=700,
                justify='left',
                anchor='w'
            ).pack(fill='x', padx=15, pady=(0, 15))
        else:
            tk.Label(
                info_frame,
                text="",
                bg=self.colors['bg_medium']
            ).pack(pady=5)
        
        # Statistics section
        stats = self.db.get_reptile_stats(reptile_id)
        stats_frame = tk.Frame(content_frame, bg=self.colors['bg_medium'])
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            stats_frame,
            text="Statistics",
            font=('Arial', 16, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(anchor='w', padx=15, pady=(15, 10))
        
        stats_grid = tk.Frame(stats_frame, bg=self.colors['bg_medium'])
        stats_grid.pack(fill='x', padx=15, pady=(0, 15))
        
        stat_items = [
            ("Total Feedings", stats['total_feedings']),
            ("Successful Feedings", stats['successful_feedings']),
            ("Success Rate", f"{stats['feeding_success_rate']:.1f}%"),
            ("Total Sheds", stats['total_sheds']),
            ("Complete Sheds", stats['complete_sheds']),
        ]
        
        for i, (label, value) in enumerate(stat_items):
            col = i % 3
            row = i // 3
            
            stat_card = tk.Frame(stats_grid, bg=self.colors['bg_light'])
            stat_card.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            stats_grid.grid_columnconfigure(col, weight=1)
            
            tk.Label(
                stat_card,
                text=str(value),
                font=('Arial', 20, 'bold'),
                bg=self.colors['bg_light'],
                fg=self.colors['accent']
            ).pack(pady=(10, 0))
            
            tk.Label(
                stat_card,
                text=label,
                font=('Arial', 9),
                bg=self.colors['bg_light'],
                fg=self.colors['text_secondary']
            ).pack(pady=(0, 10))
        
        # Recent feeding logs
        feeding_frame = tk.Frame(content_frame, bg=self.colors['bg_medium'])
        feeding_frame.pack(fill='x', padx=20, pady=10)
        
        header_row = tk.Frame(feeding_frame, bg=self.colors['bg_medium'])
        header_row.pack(fill='x', padx=15, pady=(15, 10))
        
        tk.Label(
            header_row,
            text="Recent Feedings",
            font=('Arial', 16, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(side='left')
        
        tk.Button(
            header_row,
            text="+ Add Feeding",
            command=lambda: self.show_add_feeding_form(reptile_id),
            bg=self.colors['success'],
            fg='white',
            font=('Arial', 9, 'bold'),
            bd=0,
            padx=10,
            pady=5,
            cursor='hand2'
        ).pack(side='right')
        
        recent_feedings = self.db.get_feeding_logs(reptile_id=reptile_id, limit=5)
        
        if recent_feedings:
            for feeding in recent_feedings:
                self.create_feeding_log_row(feeding_frame, feeding)
        else:
            tk.Label(
                feeding_frame,
                text="No feeding records yet",
                font=('Arial', 10),
                bg=self.colors['bg_medium'],
                fg=self.colors['text_secondary']
            ).pack(padx=15, pady=10)
        
        # Recent shed records
        shed_frame = tk.Frame(content_frame, bg=self.colors['bg_medium'])
        shed_frame.pack(fill='x', padx=20, pady=10)
        
        header_row = tk.Frame(shed_frame, bg=self.colors['bg_medium'])
        header_row.pack(fill='x', padx=15, pady=(15, 10))
        
        tk.Label(
            header_row,
            text="Recent Sheds",
            font=('Arial', 16, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(side='left')
        
        tk.Button(
            header_row,
            text="+ Add Shed",
            command=lambda: self.show_add_shed_form(reptile_id),
            bg=self.colors['warning'],
            fg='white',
            font=('Arial', 9, 'bold'),
            bd=0,
            padx=10,
            pady=5,
            cursor='hand2'
        ).pack(side='right')
        
        recent_sheds = self.db.get_shed_records(reptile_id=reptile_id)[:5]
        
        if recent_sheds:
            for shed in recent_sheds:
                self.create_shed_record_row(shed_frame, shed)
        else:
            tk.Label(
                shed_frame,
                text="No shed records yet",
                font=('Arial', 10),
                bg=self.colors['bg_medium'],
                fg=self.colors['text_secondary']
            ).pack(padx=15, pady=(0, 15))
        
        content_canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 20))
    
    def create_feeding_log_row(self, parent, feeding):
        """Create a row displaying feeding log information"""
        row = tk.Frame(parent, bg=self.colors['bg_light'])
        row.pack(fill='x', padx=15, pady=5)
        
        # Date
        tk.Label(
            row,
            text=feeding['feeding_date'],
            font=('Arial', 10, 'bold'),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            width=12,
            anchor='w'
        ).pack(side='left', padx=5)
        
        # Food type and size
        food_text = feeding['food_type']
        if feeding['food_size']:
            food_text += f" ({feeding['food_size']})"
        if feeding['quantity'] > 1:
            food_text += f" x{feeding['quantity']}"
        
        tk.Label(
            row,
            text=food_text,
            font=('Arial', 10),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            width=25,
            anchor='w'
        ).pack(side='left', padx=5)
        
        # Ate status
        ate_color = self.colors['success'] if feeding['ate'] else self.colors['danger']
        ate_text = "✓ Ate" if feeding['ate'] else "✗ Refused"
        
        tk.Label(
            row,
            text=ate_text,
            font=('Arial', 10, 'bold'),
            bg=self.colors['bg_light'],
            fg=ate_color,
            width=10
        ).pack(side='left', padx=5)
        
        # Notes
        if feeding['notes']:
            tk.Label(
                row,
                text=feeding['notes'][:30] + "..." if len(feeding['notes']) > 30 else feeding['notes'],
                font=('Arial', 9),
                bg=self.colors['bg_light'],
                fg=self.colors['text_secondary']
            ).pack(side='left', padx=5)
    
    def create_shed_record_row(self, parent, shed):
        """Create a row displaying shed record information"""
        row = tk.Frame(parent, bg=self.colors['bg_light'])
        row.pack(fill='x', padx=15, pady=5)
        
        # Date
        tk.Label(
            row,
            text=shed['shed_date'],
            font=('Arial', 10, 'bold'),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            width=12,
            anchor='w'
        ).pack(side='left', padx=5)
        
        # Complete status
        complete_color = self.colors['success'] if shed['complete'] else self.colors['warning']
        complete_text = "✓ Complete" if shed['complete'] else "⚠ Incomplete"
        
        tk.Label(
            row,
            text=complete_text,
            font=('Arial', 10, 'bold'),
            bg=self.colors['bg_light'],
            fg=complete_color,
            width=15
        ).pack(side='left', padx=5)
        
        # Notes
        if shed['notes']:
            tk.Label(
                row,
                text=shed['notes'][:40] + "..." if len(shed['notes']) > 40 else shed['notes'],
                font=('Arial', 9),
                bg=self.colors['bg_light'],
                fg=self.colors['text_secondary']
            ).pack(side='left', padx=5)
    
    # ==================== ADD/EDIT REPTILE FORMS ====================
    
    def show_add_reptile_form(self):
        """Show form to add a new reptile"""
        self.show_reptile_form(mode='add')
    
    def show_edit_reptile_form(self, reptile_id):
        """Show form to edit an existing reptile"""
        self.show_reptile_form(mode='edit', reptile_id=reptile_id)
    
    def show_reptile_form(self, mode='add', reptile_id=None):
        """Show form for adding or editing a reptile"""
        self.clear_main_frame()
        
        reptile = None
        if mode == 'edit' and reptile_id:
            reptile = self.db.get_reptile(reptile_id)
            if not reptile:
                messagebox.showerror("Error", "Reptile not found")
                self.show_dashboard()
                return
        
        # Header
        header_frame = tk.Frame(self.main_frame, bg=self.colors['bg_dark'])
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Button(
            header_frame,
            text="← Back",
            command=self.show_dashboard if mode == 'add' else lambda: self.show_reptile_details(reptile_id),
            bg=self.colors['bg_medium'],
            fg=self.colors['text'],
            font=('Arial', 10),
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side='left', padx=(0, 20))
        
        title = "Add New Reptile" if mode == 'add' else f"Edit {reptile['name']}"
        tk.Label(
            header_frame,
            text=title,
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).pack(side='left')
        
        # Form frame
        form_frame = tk.Frame(self.main_frame, bg=self.colors['bg_medium'])
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create form fields
        fields = {}
        
        form_fields = [
            ("Name*", "name", reptile['name'] if reptile else ""),
            ("Species*", "species", reptile['species'] if reptile else ""),
            ("Morph", "morph", reptile['morph'] if reptile else ""),
            ("Sex", "sex", reptile['sex'] if reptile else ""),
            ("Date of Birth (YYYY-MM-DD)", "date_of_birth", reptile['date_of_birth'] if reptile else ""),
            ("Acquisition Date (YYYY-MM-DD)", "acquisition_date", reptile['acquisition_date'] if reptile else ""),
            ("Weight (grams)", "weight_grams", str(reptile['weight_grams']) if reptile and reptile['weight_grams'] else ""),
            ("Length (cm)", "length_cm", str(reptile['length_cm']) if reptile and reptile['length_cm'] else ""),
        ]
        
        for i, (label, field_name, default_value) in enumerate(form_fields):
            row_frame = tk.Frame(form_frame, bg=self.colors['bg_medium'])
            row_frame.pack(fill='x', padx=20, pady=10)
            
            tk.Label(
                row_frame,
                text=label,
                font=('Arial', 11),
                bg=self.colors['bg_medium'],
                fg=self.colors['text'],
                width=25,
                anchor='w'
            ).pack(side='left')
            
            entry = tk.Entry(
                row_frame,
                font=('Arial', 11),
                bg=self.colors['bg_light'],
                fg=self.colors['text'],
                insertbackground=self.colors['text'],
                bd=0,
                relief='flat'
            )
            entry.pack(side='left', fill='x', expand=True, ipady=5, padx=(10, 0))
            entry.insert(0, default_value)
            fields[field_name] = entry
        
        # Notes field (text area)
        notes_frame = tk.Frame(form_frame, bg=self.colors['bg_medium'])
        notes_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            notes_frame,
            text="Notes",
            font=('Arial', 11),
            bg=self.colors['bg_medium'],
            fg=self.colors['text'],
            anchor='w'
        ).pack(anchor='w')
        
        notes_text = tk.Text(
            notes_frame,
            font=('Arial', 10),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            bd=0,
            relief='flat',
            height=5,
            wrap='word'
        )
        notes_text.pack(fill='x', pady=(5, 0))
        if reptile and reptile['notes']:
            notes_text.insert('1.0', reptile['notes'])
        
        # Image upload button
        image_frame = tk.Frame(form_frame, bg=self.colors['bg_medium'])
        image_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            image_frame,
            text="Reptile Photo",
            font=('Arial', 11),
            bg=self.colors['bg_medium'],
            fg=self.colors['text'],
            anchor='w'
        ).pack(anchor='w')
        
        image_button = tk.Button(
            image_frame,
            text="📷 Select Image",
            command=lambda: self.select_reptile_image(fields),
            bg=self.colors['accent'],
            fg='white',
            font=('Arial', 10),
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        image_button.pack(anchor='w', pady=(5, 0))
        fields['image_button'] = image_button
        fields['selected_image_path'] = reptile.get('image_path') if reptile else None
        fields['notes'] = notes_text
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=self.colors['bg_medium'])
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Save" if mode == 'add' else "Update",
            command=lambda: self.save_reptile(fields, mode, reptile_id),
            bg=self.colors['success'],
            fg='white',
            font=('Arial', 12, 'bold'),
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(side='left', padx=10)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=self.show_dashboard if mode == 'add' else lambda: self.show_reptile_details(reptile_id),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            font=('Arial', 12),
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(side='left', padx=10)
    
    def save_reptile(self, fields, mode, reptile_id=None):
        """Save reptile data (add or update)"""
        # Get values from fields
        data = {}
        selected_image = fields.get('selected_image_path')
        for field_name, widget in fields.items():
            if isinstance(widget, tk.Text):
                value = widget.get('1.0', 'end-1c').strip()
            else:
                value = widget.get().strip()
            
            # Convert empty strings to None
            if value == "":
                value = None
            # Convert numeric fields
            elif field_name in ['weight_grams', 'length_cm'] and value:
                try:
                    value = float(value)
                except ValueError:
                    messagebox.showerror("Error", f"Invalid number for {field_name}")
                    return
            
            data[field_name] = value
        
        # Validate required fields
        if not data.get('name'):
            messagebox.showerror("Error", "Name is required")
            return
        if not data.get('species'):
            messagebox.showerror("Error", "Species is required")
            return
        
        try:
            if mode == 'add':
                reptile_id = self.db.add_reptile(**data)
            else:
                self.db.update_reptile(reptile_id, **data)
            
            # Handle image upload if a new image was selected
            if selected_image:
                image_path = self.save_reptile_image(selected_image, reptile_id)
                if image_path:
                    self.db.update_reptile(reptile_id, image_path=image_path)
            
            # Show success message and navigate to details
            messagebox.showinfo("Success", f"{data['name']} has been saved!")
            self.show_reptile_details(reptile_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save reptile: {str(e)}")
    
    def delete_reptile(self, reptile_id):
        """Delete a reptile after confirmation"""
        reptile = self.db.get_reptile(reptile_id)
        if not reptile:
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete {reptile['name']}?\n\n"
                              "This will also delete all feeding logs and shed records."):
            self.db.delete_reptile(reptile_id)
            messagebox.showinfo("Success", f"{reptile['name']} has been deleted")
            self.show_dashboard()
    
    # ==================== FEEDING LOG FORMS ====================
    
    def show_add_feeding_form(self, reptile_id):
        """Show form to add a feeding log"""
        reptile = self.db.get_reptile(reptile_id)
        if not reptile:
            messagebox.showerror("Error", "Reptile not found")
            return
        
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title(f"Add Feeding Log - {reptile['name']}")
        popup.geometry("500x550")
        popup.configure(bg=self.colors['bg_dark'])
        popup.transient(self.root)
        popup.grab_set()
        
        # Title
        tk.Label(
            popup,
            text=f"Add Feeding Log for {reptile['name']}",
            font=('Arial', 16, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        # Form frame
        form_frame = tk.Frame(popup, bg=self.colors['bg_dark'])
        form_frame.pack(fill='both', expand=True, padx=20)
        
        fields = {}
        
        # Date
        row = tk.Frame(form_frame, bg=self.colors['bg_dark'])
        row.pack(fill='x', pady=10)
        tk.Label(row, text="Date (YYYY-MM-DD)*", font=('Arial', 11), 
                bg=self.colors['bg_dark'], fg=self.colors['text'], width=20, anchor='w').pack(side='left')
        date_entry = tk.Entry(row, font=('Arial', 11), bg=self.colors['bg_light'], 
                             fg=self.colors['text'], insertbackground=self.colors['text'], bd=0)
        date_entry.pack(side='left', fill='x', expand=True, ipady=5)
        date_entry.insert(0, get_current_date())
        fields['feeding_date'] = date_entry
        
        # Food type
        row = tk.Frame(form_frame, bg=self.colors['bg_dark'])
        row.pack(fill='x', pady=10)
        tk.Label(row, text="Food Type*", font=('Arial', 11), 
                bg=self.colors['bg_dark'], fg=self.colors['text'], width=20, anchor='w').pack(side='left')
        food_entry = tk.Entry(row, font=('Arial', 11), bg=self.colors['bg_light'], 
                             fg=self.colors['text'], insertbackground=self.colors['text'], bd=0)
        food_entry.pack(side='left', fill='x', expand=True, ipady=5)
        fields['food_type'] = food_entry
        
        # Food size
        row = tk.Frame(form_frame, bg=self.colors['bg_dark'])
        row.pack(fill='x', pady=10)
        tk.Label(row, text="Food Size", font=('Arial', 11), 
                bg=self.colors['bg_dark'], fg=self.colors['text'], width=20, anchor='w').pack(side='left')
        size_entry = tk.Entry(row, font=('Arial', 11), bg=self.colors['bg_light'], 
                             fg=self.colors['text'], insertbackground=self.colors['text'], bd=0)
        size_entry.pack(side='left', fill='x', expand=True, ipady=5)
        fields['food_size'] = size_entry
        
        # Quantity
        row = tk.Frame(form_frame, bg=self.colors['bg_dark'])
        row.pack(fill='x', pady=10)
        tk.Label(row, text="Quantity", font=('Arial', 11), 
                bg=self.colors['bg_dark'], fg=self.colors['text'], width=20, anchor='w').pack(side='left')
        qty_entry = tk.Entry(row, font=('Arial', 11), bg=self.colors['bg_light'], 
                            fg=self.colors['text'], insertbackground=self.colors['text'], bd=0)
        qty_entry.pack(side='left', fill='x', expand=True, ipady=5)
        qty_entry.insert(0, "1")
        fields['quantity'] = qty_entry
        
        # Ate checkbox
        row = tk.Frame(form_frame, bg=self.colors['bg_dark'])
        row.pack(fill='x', pady=10)
        ate_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            row,
            text="Reptile ate the food",
            variable=ate_var,
            font=('Arial', 11),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            selectcolor=self.colors['bg_light'],
            activebackground=self.colors['bg_dark'],
            activeforeground=self.colors['text']
        ).pack(anchor='w')
        fields['ate'] = ate_var
        
        # Notes
        tk.Label(form_frame, text="Notes", font=('Arial', 11), 
                bg=self.colors['bg_dark'], fg=self.colors['text'], anchor='w').pack(anchor='w', pady=(10, 5))
        notes_text = tk.Text(form_frame, font=('Arial', 10), bg=self.colors['bg_light'], 
                            fg=self.colors['text'], insertbackground=self.colors['text'], 
                            bd=0, height=4, wrap='word')
        notes_text.pack(fill='x')
        fields['notes'] = notes_text
        
        # Buttons
        button_frame = tk.Frame(popup, bg=self.colors['bg_dark'])
        button_frame.pack(pady=20)
        
        def save_feeding():
            try:
                data = {
                    'reptile_id': reptile_id,
                    'feeding_date': fields['feeding_date'].get().strip(),
                    'food_type': fields['food_type'].get().strip(),
                    'food_size': fields['food_size'].get().strip() or None,
                    'quantity': int(fields['quantity'].get().strip() or 1),
                    'ate': fields['ate'].get(),
                    'notes': fields['notes'].get('1.0', 'end-1c').strip() or None
                }
                
                if not data['feeding_date'] or not data['food_type']:
                    messagebox.showerror("Error", "Date and Food Type are required")
                    return
                
                self.db.add_feeding_log(**data)
                messagebox.showinfo("Success", "Feeding log added!")
                popup.destroy()
                if self.current_view == 'reptile_details':
                    self.show_reptile_details(reptile_id)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
        
        tk.Button(
            button_frame,
            text="Save",
            command=save_feeding,
            bg=self.colors['success'],
            fg='white',
            font=('Arial', 11, 'bold'),
            bd=0,
            padx=30,
            pady=8,
            cursor='hand2'
        ).pack(side='left', padx=10)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            font=('Arial', 11),
            bd=0,
            padx=30,
            pady=8,
            cursor='hand2'
        ).pack(side='left', padx=10)
    
    def show_add_shed_form(self, reptile_id):
        """Show form to add a shed record"""
        reptile = self.db.get_reptile(reptile_id)
        if not reptile:
            messagebox.showerror("Error", "Reptile not found")
            return
        
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title(f"Add Shed Record - {reptile['name']}")
        popup.geometry("500x400")
        popup.configure(bg=self.colors['bg_dark'])
        popup.transient(self.root)
        popup.grab_set()
        
        # Title
        tk.Label(
            popup,
            text=f"Add Shed Record for {reptile['name']}",
            font=('Arial', 16, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        # Form frame
        form_frame = tk.Frame(popup, bg=self.colors['bg_dark'])
        form_frame.pack(fill='both', expand=True, padx=20)
        
        fields = {}
        
        # Date
        row = tk.Frame(form_frame, bg=self.colors['bg_dark'])
        row.pack(fill='x', pady=10)
        tk.Label(row, text="Date (YYYY-MM-DD)*", font=('Arial', 11), 
                bg=self.colors['bg_dark'], fg=self.colors['text'], width=20, anchor='w').pack(side='left')
        date_entry = tk.Entry(row, font=('Arial', 11), bg=self.colors['bg_light'], 
                             fg=self.colors['text'], insertbackground=self.colors['text'], bd=0)
        date_entry.pack(side='left', fill='x', expand=True, ipady=5)
        date_entry.insert(0, get_current_date())
        fields['shed_date'] = date_entry
        
        # Complete checkbox
        row = tk.Frame(form_frame, bg=self.colors['bg_dark'])
        row.pack(fill='x', pady=10)
        complete_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            row,
            text="Shed was complete (no stuck shed)",
            variable=complete_var,
            font=('Arial', 11),
            bg=self.colors['bg_dark'],
            fg=self.colors['text'],
            selectcolor=self.colors['bg_light'],
            activebackground=self.colors['bg_dark'],
            activeforeground=self.colors['text']
        ).pack(anchor='w')
        fields['complete'] = complete_var
        
        # Notes
        tk.Label(form_frame, text="Notes", font=('Arial', 11), 
                bg=self.colors['bg_dark'], fg=self.colors['text'], anchor='w').pack(anchor='w', pady=(10, 5))
        notes_text = tk.Text(form_frame, font=('Arial', 10), bg=self.colors['bg_light'], 
                            fg=self.colors['text'], insertbackground=self.colors['text'], 
                            bd=0, height=5, wrap='word')
        notes_text.pack(fill='x')
        fields['notes'] = notes_text
        
        # Buttons
        button_frame = tk.Frame(popup, bg=self.colors['bg_dark'])
        button_frame.pack(pady=20)
        
        def save_shed():
            try:
                data = {
                    'reptile_id': reptile_id,
                    'shed_date': fields['shed_date'].get().strip(),
                    'complete': fields['complete'].get(),
                    'notes': fields['notes'].get('1.0', 'end-1c').strip() or None
                }
                
                if not data['shed_date']:
                    messagebox.showerror("Error", "Date is required")
                    return
                
                self.db.add_shed_record(**data)
                messagebox.showinfo("Success", "Shed record added!")
                popup.destroy()
                if self.current_view == 'reptile_details':
                    self.show_reptile_details(reptile_id)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
        
        tk.Button(
            button_frame,
            text="Save",
            command=save_shed,
            bg=self.colors['success'],
            fg='white',
            font=('Arial', 11, 'bold'),
            bd=0,
            padx=30,
            pady=8,
            cursor='hand2'
        ).pack(side='left', padx=10)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            font=('Arial', 11),
            bd=0,
            padx=30,
            pady=8,
            cursor='hand2'
        ).pack(side='left', padx=10)
    
    # ==================== FEEDING LOGS VIEW ====================
    
    def show_feeding_logs(self):
        """Show all feeding logs"""
        self.clear_main_frame()
        self.current_view = 'feeding_logs'
        
        # Header
        header_frame = tk.Frame(self.main_frame, bg=self.colors['bg_dark'])
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            header_frame,
            text="Feeding Logs",
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).pack(side='left')
        
        # Get all feeding logs
        logs = self.db.get_feeding_logs(limit=100)
        
        if not logs:
            tk.Label(
                self.main_frame,
                text="No feeding logs yet",
                font=('Arial', 14),
                bg=self.colors['bg_dark'],
                fg=self.colors['text_secondary'],
                pady=50
            ).pack()
            return
        
        # Create scrollable list
        canvas = tk.Canvas(self.main_frame, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display logs
        for log in logs:
            log_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_medium'])
            log_frame.pack(fill='x', padx=20, pady=5)
            
            # Reptile name and date
            header_row = tk.Frame(log_frame, bg=self.colors['bg_medium'])
            header_row.pack(fill='x', padx=15, pady=(10, 5))
            
            tk.Label(
                header_row,
                text=log['reptile_name'],
                font=('Arial', 12, 'bold'),
                bg=self.colors['bg_medium'],
                fg=self.colors['accent']
            ).pack(side='left')
            
            tk.Label(
                header_row,
                text=log['feeding_date'],
                font=('Arial', 10),
                bg=self.colors['bg_medium'],
                fg=self.colors['text_secondary']
            ).pack(side='right')
            
            # Food details
            food_text = log['food_type']
            if log['food_size']:
                food_text += f" ({log['food_size']})"
            if log['quantity'] > 1:
                food_text += f" x{log['quantity']}"
            
            tk.Label(
                log_frame,
                text=food_text,
                font=('Arial', 11),
                bg=self.colors['bg_medium'],
                fg=self.colors['text']
            ).pack(anchor='w', padx=15, pady=5)
            
            # Status and notes
            bottom_row = tk.Frame(log_frame, bg=self.colors['bg_medium'])
            bottom_row.pack(fill='x', padx=15, pady=(5, 10))
            
            ate_color = self.colors['success'] if log['ate'] else self.colors['danger']
            ate_text = "✓ Ate" if log['ate'] else "✗ Refused"
            
            tk.Label(
                bottom_row,
                text=ate_text,
                font=('Arial', 10, 'bold'),
                bg=self.colors['bg_medium'],
                fg=ate_color
            ).pack(side='left')
            
            if log['notes']:
                tk.Label(
                    bottom_row,
                    text=f"  •  {log['notes']}",
                    font=('Arial', 9),
                    bg=self.colors['bg_medium'],
                    fg=self.colors['text_secondary']
                ).pack(side='left')
        
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 20))
    
    # ==================== SHED RECORDS VIEW ====================
    
    def show_shed_records(self):
        """Show all shed records"""
        self.clear_main_frame()
        self.current_view = 'shed_records'
        
        # Header
        header_frame = tk.Frame(self.main_frame, bg=self.colors['bg_dark'])
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            header_frame,
            text="Shed Records",
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).pack(side='left')
        
        # Get all shed records
        records = self.db.get_shed_records()
        
        if not records:
            tk.Label(
                self.main_frame,
                text="No shed records yet",
                font=('Arial', 14),
                bg=self.colors['bg_dark'],
                fg=self.colors['text_secondary'],
                pady=50
            ).pack()
            return
        
        # Create scrollable list
        canvas = tk.Canvas(self.main_frame, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display records
        for record in records:
            record_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_medium'])
            record_frame.pack(fill='x', padx=20, pady=5)
            
            # Reptile name and date
            header_row = tk.Frame(record_frame, bg=self.colors['bg_medium'])
            header_row.pack(fill='x', padx=15, pady=(10, 5))
            
            tk.Label(
                header_row,
                text=record['reptile_name'],
                font=('Arial', 12, 'bold'),
                bg=self.colors['bg_medium'],
                fg=self.colors['accent']
            ).pack(side='left')
            
            tk.Label(
                header_row,
                text=record['shed_date'],
                font=('Arial', 10),
                bg=self.colors['bg_medium'],
                fg=self.colors['text_secondary']
            ).pack(side='right')
            
            # Status and notes
            bottom_row = tk.Frame(record_frame, bg=self.colors['bg_medium'])
            bottom_row.pack(fill='x', padx=15, pady=(5, 10))
            
            complete_color = self.colors['success'] if record['complete'] else self.colors['warning']
            complete_text = "✓ Complete Shed" if record['complete'] else "⚠ Incomplete Shed"
            
            tk.Label(
                bottom_row,
                text=complete_text,
                font=('Arial', 10, 'bold'),
                bg=self.colors['bg_medium'],
                fg=complete_color
            ).pack(side='left')
            
            if record['notes']:
                tk.Label(
                    bottom_row,
                    text=f"  •  {record['notes']}",
                    font=('Arial', 9),
                    bg=self.colors['bg_medium'],
                    fg=self.colors['text_secondary']
                ).pack(side='left')
        
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 20))
    
    # ==================== IMPORT/EXPORT ====================
    
    def import_csv(self):
        """Import data from CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV file to import",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                
                if not rows:
                    messagebox.showwarning("Warning", "CSV file is empty")
                    return
                
                # Determine import type based on columns
                columns = set(rows[0].keys())
                
                if 'name' in columns and 'species' in columns:
                    # Import reptiles
                    count = self.import_reptiles_from_csv(rows)
                    messagebox.showinfo("Success", f"Imported {count} reptile(s)")
                    self.show_dashboard()
                elif 'reptile_name' in columns and 'feeding_date' in columns:
                    # Import feeding logs
                    count = self.import_feeding_logs_from_csv(rows)
                    messagebox.showinfo("Success", f"Imported {count} feeding log(s)")
                    self.show_feeding_logs()
                else:
                    messagebox.showerror("Error", "Unrecognized CSV format")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV: {str(e)}")
    
    def import_reptiles_from_csv(self, rows):
        """Import reptiles from CSV rows"""
        count = 0
        for row in rows:
            try:
                data = {
                    'name': row.get('name', '').strip(),
                    'species': row.get('species', '').strip(),
                    'morph': row.get('morph', '').strip() or None,
                    'sex': row.get('sex', '').strip() or None,
                    'date_of_birth': row.get('date_of_birth', '').strip() or None,
                    'acquisition_date': row.get('acquisition_date', '').strip() or None,
                    'weight_grams': float(row.get('weight_grams', 0)) if row.get('weight_grams') else None,
                    'length_cm': float(row.get('length_cm', 0)) if row.get('length_cm') else None,
                    'notes': row.get('notes', '').strip() or None
                }
                
                if data['name'] and data['species']:
                    self.db.add_reptile(**data)
                    count += 1
            except Exception as e:
                print(f"Error importing row: {e}")
                continue
        
        return count
    
    def import_feeding_logs_from_csv(self, rows):
        """Import feeding logs from CSV rows"""
        count = 0
        for row in rows:
            try:
                # Find reptile by name
                reptile_name = row.get('reptile_name', '').strip()
                reptiles = self.db.get_all_reptiles()
                reptile = next((r for r in reptiles if r['name'] == reptile_name), None)
                
                if not reptile:
                    continue
                
                data = {
                    'reptile_id': reptile['id'],
                    'feeding_date': row.get('feeding_date', '').strip(),
                    'food_type': row.get('food_type', '').strip(),
                    'food_size': row.get('food_size', '').strip() or None,
                    'quantity': int(row.get('quantity', 1)),
                    'ate': row.get('ate', 'true').lower() in ['true', '1', 'yes'],
                    'notes': row.get('notes', '').strip() or None
                }
                
                if data['feeding_date'] and data['food_type']:
                    self.db.add_feeding_log(**data)
                    count += 1
            except Exception as e:
                print(f"Error importing row: {e}")
                continue
        
        return count
    
    def export_data(self):
        """Export data to CSV file"""
        # Ask user what to export
        export_window = tk.Toplevel(self.root)
        export_window.title("Export Data")
        export_window.geometry("400x250")
        export_window.configure(bg=self.colors['bg_dark'])
        export_window.transient(self.root)
        export_window.grab_set()
        
        tk.Label(
            export_window,
            text="Select data to export:",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        def export_reptiles():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile="reptiles_export.csv"
            )
            if file_path:
                self.export_reptiles_to_csv(file_path)
                export_window.destroy()
        
        def export_feeding():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile="feeding_logs_export.csv"
            )
            if file_path:
                self.export_feeding_logs_to_csv(file_path)
                export_window.destroy()
        
        def export_sheds():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile="shed_records_export.csv"
            )
            if file_path:
                self.export_shed_records_to_csv(file_path)
                export_window.destroy()
        
        tk.Button(
            export_window,
            text="Export Reptiles",
            command=export_reptiles,
            bg=self.colors['accent'],
            fg='white',
            font=('Arial', 11, 'bold'),
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(pady=10)
        
        tk.Button(
            export_window,
            text="Export Feeding Logs",
            command=export_feeding,
            bg=self.colors['success'],
            fg='white',
            font=('Arial', 11, 'bold'),
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(pady=10)
        
        tk.Button(
            export_window,
            text="Export Shed Records",
            command=export_sheds,
            bg=self.colors['warning'],
            fg='white',
            font=('Arial', 11, 'bold'),
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(pady=10)
    
    def export_reptiles_to_csv(self, file_path):
        """Export reptiles to CSV"""
        try:
            reptiles = self.db.get_all_reptiles()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['name', 'species', 'morph', 'sex', 'date_of_birth', 
                            'acquisition_date', 'weight_grams', 'length_cm', 'notes']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                for reptile in reptiles:
                    row = {k: reptile.get(k, '') for k in fieldnames}
                    writer.writerow(row)
            
            messagebox.showinfo("Success", f"Exported {len(reptiles)} reptile(s) to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def export_feeding_logs_to_csv(self, file_path):
        """Export feeding logs to CSV"""
        try:
            logs = self.db.get_feeding_logs()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['reptile_name', 'feeding_date', 'food_type', 'food_size', 
                            'quantity', 'ate', 'notes']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                for log in logs:
                    row = {k: log.get(k, '') for k in fieldnames}
                    writer.writerow(row)
            
            messagebox.showinfo("Success", f"Exported {len(logs)} feeding log(s) to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def export_shed_records_to_csv(self, file_path):
        """Export shed records to CSV"""
        try:
            records = self.db.get_shed_records()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['reptile_name', 'shed_date', 'complete', 'notes']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                for record in records:
                    row = {k: record.get(k, '') for k in fieldnames}
                    writer.writerow(row)
            
            messagebox.showinfo("Success", f"Exported {len(records)} shed record(s) to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    # ==================== ABOUT ====================
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About Reptile Tracker",
            "Reptile Tracker v1.0\n\n"
            "A comprehensive desktop application for tracking\n"
            "reptile care, feeding schedules, and shed records.\n\n"
            "Features:\n"
            "• Track multiple reptiles\n"
            "• Log feeding records\n"
            "• Track shed cycles\n"
            "• Import/Export CSV data\n"
            "• Detailed statistics and analytics\n\n"
            "Built with Python and tkinter"
        )
    
    def run(self):
        """Start the application"""
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Start main loop
        self.root.mainloop()
        
        # Close database connection when app closes
        self.db.close()


if __name__ == "__main__":
    app = ReptileTrackerApp()
    app.run()

# Made with Bob
