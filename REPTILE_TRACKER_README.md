# 🦎 Reptile Tracker

A comprehensive desktop application for tracking reptile care, feeding schedules, shed records, and health information.

## Features

### Core Functionality
- **Multi-Reptile Management**: Track unlimited number of reptiles
- **Feeding Logs**: Record what you feed, when, and whether they ate
- **Shed Tracking**: Monitor shed cycles and completeness
- **Detailed Profiles**: Store comprehensive information for each reptile
- **Statistics & Analytics**: View feeding success rates, shed history, and more
- **Data Import/Export**: CSV support for bulk data management

### User Interface
- **Dashboard View**: Overview of all reptiles with quick stats
- **Detailed Reptile Profiles**: Complete information and history for each animal
- **Feeding Log View**: Chronological list of all feeding records
- **Shed Records View**: Timeline of all shed events
- **Intuitive Forms**: Easy-to-use forms for adding and editing data

## Installation

### Prerequisites
- Python 3.6 or higher
- tkinter (usually comes with Python)
- SQLite3 (included with Python)

### Setup
1. Ensure all files are in the same directory:
   - `reptile_tracker.py` (main application)
   - `reptile_tracker_db.py` (database module)

2. Run the application:
   ```bash
   python3 reptile_tracker.py
   ```

### For macOS Users
If you encounter tkinter issues:
```bash
# Install tkinter support
brew install python-tk

# Or use system Python
/usr/bin/python3 reptile_tracker.py
```

## Quick Start Guide

### Adding Your First Reptile

1. Click **"🦎 Add Reptile"** in the sidebar or menu
2. Fill in the required fields:
   - **Name*** (required): Your reptile's name
   - **Species*** (required): e.g., Ball Python, Bearded Dragon
   - **Morph**: Color/pattern morph (optional)
   - **Sex**: Male, Female, or Unknown
   - **Date of Birth**: YYYY-MM-DD format
   - **Acquisition Date**: When you got them
   - **Weight**: In grams
   - **Length**: In centimeters
   - **Notes**: Any additional information
3. Click **Save**

### Recording a Feeding

1. From the dashboard, click **"Add Feeding"** on a reptile card
2. Or navigate to the reptile's detail page and click **"+ Add Feeding"**
3. Fill in the feeding information:
   - **Date**: When you fed them (defaults to today)
   - **Food Type**: e.g., Mouse, Rat, Cricket, Dubia Roach
   - **Food Size**: e.g., Small, Medium, Large, Adult
   - **Quantity**: Number of food items
   - **Ate**: Check if they ate, uncheck if refused
   - **Notes**: Any observations
4. Click **Save**

### Recording a Shed

1. Navigate to the reptile's detail page
2. Click **"+ Add Shed"** in the shed records section
3. Fill in:
   - **Date**: When they shed
   - **Complete**: Check if shed was complete (no stuck shed)
   - **Notes**: Any issues or observations
4. Click **Save**

## Data Import/Export

### Importing Data

The application supports CSV import for bulk data entry.

#### Import Reptiles

Create a CSV file with these columns:
```csv
name,species,morph,sex,date_of_birth,acquisition_date,weight_grams,length_cm,notes
Monty,Ball Python,Pastel,Male,2020-05-15,2021-01-10,1200,120,Very docile
Spike,Bearded Dragon,,Male,2019-08-20,2020-03-15,450,45,Loves greens
```

**Required columns**: `name`, `species`  
**Optional columns**: All others

#### Import Feeding Logs

Create a CSV file with these columns:
```csv
reptile_name,feeding_date,food_type,food_size,quantity,ate,notes
Monty,2024-12-01,Mouse,Medium,1,true,Ate immediately
Monty,2024-12-08,Mouse,Medium,1,false,Refused - in shed
Spike,2024-12-05,Dubia Roach,Adult,10,true,Very hungry
```

**Required columns**: `reptile_name`, `feeding_date`, `food_type`  
**Optional columns**: `food_size`, `quantity`, `ate`, `notes`

**Note**: The reptile must already exist in the database (import reptiles first)

#### How to Import

1. Click **"📥 Import Data"** in the sidebar
2. Or use menu: **File → Import CSV**
3. Select your CSV file
4. The app will automatically detect the data type and import

### Exporting Data

Export your data to CSV for backup or analysis:

1. Click **"📤 Export Data"** in the sidebar
2. Or use menu: **File → Export Data**
3. Choose what to export:
   - **Reptiles**: All reptile information
   - **Feeding Logs**: All feeding records
   - **Shed Records**: All shed events
4. Choose save location
5. Open in Excel, Google Sheets, or any spreadsheet application

## Database Information

### Storage Location
Data is stored in `reptile_tracker.db` in the same directory as the application.

### Database Schema

**reptiles** table:
- id, name, species, morph, sex
- date_of_birth, acquisition_date
- weight_grams, length_cm
- notes, image_path
- created_at, updated_at

**feeding_logs** table:
- id, reptile_id, feeding_date
- food_type, food_size, quantity
- ate (boolean), notes
- created_at

**shed_records** table:
- id, reptile_id, shed_date
- complete (boolean), notes
- created_at

**weight_history** table:
- id, reptile_id, measurement_date
- weight_grams, notes
- created_at

### Backup Your Data

**Important**: Regularly backup your `reptile_tracker.db` file!

```bash
# Create a backup
cp reptile_tracker.db reptile_tracker_backup_$(date +%Y%m%d).db
```

## Usage Tips

### Best Practices

1. **Consistent Naming**: Use consistent food type names (e.g., always "Mouse" not "mouse" or "Mice")
2. **Regular Updates**: Log feedings immediately after they occur
3. **Detailed Notes**: Add notes about behavior, appetite changes, or health concerns
4. **Date Format**: Always use YYYY-MM-DD format for dates
5. **Regular Backups**: Export your data regularly as backup

### Feeding Schedule Tracking

The dashboard shows reptiles that haven't been fed in 7 days under "Needs Feeding". Use this to:
- Identify which reptiles need to be fed
- Maintain consistent feeding schedules
- Avoid overfeeding or underfeeding

### Shed Cycle Monitoring

Track shed patterns to:
- Predict upcoming sheds
- Identify shed problems early
- Adjust humidity if needed
- Monitor growth rates

### Statistics Usage

Use the statistics on reptile detail pages to:
- Monitor feeding success rates
- Identify feeding problems
- Track growth over time
- Make informed care decisions

## Keyboard Shortcuts

Currently, the application is mouse-driven. Future versions may include:
- Ctrl+N: New reptile
- Ctrl+F: Add feeding
- Ctrl+S: Add shed
- Ctrl+I: Import data
- Ctrl+E: Export data

## Troubleshooting

### Application Won't Start

**Problem**: "ModuleNotFoundError: No module named 'tkinter'"
**Solution**: Install tkinter support (see Installation section)

**Problem**: "ModuleNotFoundError: No module named 'reptile_tracker_db'"
**Solution**: Ensure both .py files are in the same directory

### Database Issues

**Problem**: "Database is locked"
**Solution**: Close any other instances of the application

**Problem**: Data not saving
**Solution**: Check file permissions in the application directory

### Import Issues

**Problem**: CSV import fails
**Solution**: 
- Verify CSV format matches examples
- Check for special characters in data
- Ensure reptile names match exactly for feeding logs
- Use UTF-8 encoding for CSV files

### Display Issues

**Problem**: Window too small or text cut off
**Solution**: The window is resizable - drag corners to adjust size

**Problem**: Colors look wrong
**Solution**: This is a dark-themed application. If you prefer light themes, the colors can be customized in the code.

## Customization

### Changing Colors

Edit the `colors` dictionary in `reptile_tracker.py`:

```python
self.colors = {
    'bg_dark': '#2C2C2C',      # Main background
    'bg_medium': '#3A3A3A',    # Card backgrounds
    'bg_light': '#4A4A4A',     # Input fields
    'accent': '#4ECDC4',       # Teal accent
    'success': '#96CEB4',      # Green for success
    'warning': '#FFD93D',      # Yellow for warnings
    'danger': '#FF6B6B',       # Red for errors
    'text': 'white',           # Main text
    'text_secondary': '#CCCCCC' # Secondary text
}
```

### Adding Custom Fields

To add custom fields to reptiles:
1. Modify the database schema in `reptile_tracker_db.py`
2. Update the form in `reptile_tracker.py`
3. Add the field to import/export functions

## Advanced Features

### Bulk Operations

Import multiple reptiles at once using CSV import:
1. Create a spreadsheet with all your reptiles
2. Export as CSV
3. Import into the application

### Data Analysis

Export data to CSV and use spreadsheet software for:
- Feeding cost analysis
- Growth rate calculations
- Shed cycle predictions
- Feeding success trends

### Multiple Databases

To maintain separate databases (e.g., for different collections):
1. Create copies of the application in different folders
2. Each will have its own `reptile_tracker.db` file

## System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.6 or higher
- **RAM**: 256 MB minimum
- **Storage**: 10 MB for application, varies with data
- **Display**: 1200x800 minimum resolution recommended

## Data Privacy

- All data is stored locally on your computer
- No internet connection required
- No data is sent to external servers
- Your reptile data remains completely private

## Future Enhancements

Potential features for future versions:
- Weight tracking graphs
- Feeding schedule reminders
- Photo gallery for each reptile
- Veterinary visit tracking
- Breeding records
- Temperature/humidity logging
- Mobile app companion
- Cloud backup option
- Multi-user support

## Support & Feedback

For issues, suggestions, or questions:
- Check the Troubleshooting section
- Review the Quick Start Guide
- Ensure you're using the latest version

## Version History

### Version 1.0 (Current)
- Initial release
- Core reptile tracking functionality
- Feeding and shed logging
- CSV import/export
- Statistics and analytics
- Dashboard and detail views

## License

This application is provided as-is for personal use in tracking reptile care.

## Credits

Built with:
- Python 3
- tkinter (GUI framework)
- SQLite3 (database)

---

**Happy Reptile Keeping! 🦎🐍🦴**

Remember: Proper record-keeping is essential for responsible reptile ownership. This tool helps you provide the best care for your scaly friends!