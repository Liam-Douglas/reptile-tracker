# 📝 Changelog

All notable changes to the Reptile Tracker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2024-12-10

### 🎉 Added - Data Import Feature

#### New Features
- **Excel/CSV Import System** - Bulk import data from spreadsheets
  - Import reptiles, feeding logs, and shed records
  - Support for Excel (.xlsx, .xls) and CSV formats
  - Downloadable pre-formatted templates for each data type
  - Row-by-row validation with detailed error reporting
  - Partial import support (saves successful rows even if some fail)

#### New Pages
- **Import Data Page** (`/import`)
  - User-friendly interface with step-by-step instructions
  - Template download buttons for all data types
  - File upload form with data type selection
  - Comprehensive field reference guide
  - Examples and tips for successful imports

#### New Database Methods
- `bulk_import_reptiles()` - Import multiple reptiles at once
- `bulk_import_feeding_logs()` - Bulk import feeding history
- `bulk_import_shed_records()` - Bulk import shed tracking data

#### New Routes
- `GET /import` - Display import page
- `GET /import/template/<data_type>` - Download Excel templates
- `POST /import/upload` - Process uploaded import files

#### Documentation
- `IMPORT_FEATURE.md` - Complete import feature documentation
  - How-to guide with examples
  - Field format reference
  - Troubleshooting tips
  - Best practices

#### Dependencies
- Added `pandas>=2.0.0` for data processing
- Added `openpyxl>=3.1.0` for Excel file handling

#### UI Updates
- Added "Import Data" link to navigation menu
- Import page with modern, mobile-responsive design
- Collapsible field reference sections

---

## [1.0.1] - 2024-12-10

### 🐛 Fixed - Critical Bug Fixes

#### Data Persistence
- **Fixed**: Data loss on Render deployments
  - Added persistent disk storage configuration
  - Created `render.yaml` with 1GB disk mount
  - Updated `app.py` to use `DATA_DIR` environment variable
  - Database and uploads now stored in persistent location

#### Database Methods
- **Fixed**: `AttributeError: 'ReptileDatabase' object has no attribute 'get_all_shed_records'`
  - Added missing `get_all_feeding_logs()` method
  - Added missing `get_all_shed_records()` method

#### Dashboard Statistics
- **Fixed**: Dashboard template errors due to missing stats
  - Updated `get_dashboard_stats()` to return `total_feedings`
  - Updated `get_dashboard_stats()` to return `total_sheds`
  - Updated `get_dashboard_stats()` to return `feeding_success_rate`

#### Feeding Logs
- **Fixed**: Parameter mismatch in feeding log creation
  - Changed `date` parameter to `feeding_date`
  - Changed `amount` parameter to `food_size`
  - Added `quantity` parameter support

#### Documentation
- `DEPLOYMENT_GUIDE.md` - Comprehensive deployment instructions
- `BUGFIXES.md` - Detailed bug fix documentation

---

## [1.0.0] - 2024-12-09

### 🎉 Initial Release

#### Core Features
- **Reptile Management**
  - Add, edit, and delete reptiles
  - Track species, morph, sex, and measurements
  - Photo upload support
  - Detailed reptile profiles

- **Feeding Logs**
  - Record feeding schedules
  - Track food type, size, and quantity
  - Monitor feeding success rates
  - View feeding history

- **Shed Records**
  - Track shed cycles
  - Record shed completeness
  - Measure shed length
  - Monitor shed patterns

- **Dashboard**
  - Overview statistics
  - Quick access to all reptiles
  - Recent activity summary
  - Reptile cards with photos

#### Technical Features
- SQLite database with full CRUD operations
- Mobile-responsive design
- Flask web framework
- Image upload and storage
- Flash message system
- Navigation menu

#### Deployment Support
- Railway configuration (`nixpacks.toml`)
- Procfile for deployment
- Requirements.txt with dependencies
- README with deployment instructions

---

## Version History

- **v1.1.0** (2024-12-10) - Data Import Feature
- **v1.0.1** (2024-12-10) - Critical Bug Fixes
- **v1.0.0** (2024-12-09) - Initial Release

---

## Upcoming Features

### Planned for v1.2.0
- [ ] Data export (Excel/CSV)
- [ ] Weight tracking charts
- [ ] Feeding schedule reminders
- [ ] Multi-user support with authentication
- [ ] Dark mode theme
- [ ] Mobile app (PWA)

### Under Consideration
- [ ] Veterinary records tracking
- [ ] Breeding records
- [ ] Expense tracking
- [ ] Photo gallery
- [ ] Print reports
- [ ] API for third-party integrations

---

## Contributing

Found a bug or have a feature request? Please open an issue on GitHub!

## Support

For questions or issues:
1. Check the documentation files (README.md, DEPLOYMENT_GUIDE.md, etc.)
2. Review the BUGFIXES.md for known issues
3. Open an issue on GitHub

---

**Made with ❤️ by Bob** 🦎