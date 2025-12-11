# 📝 Changelog

All notable changes to the Reptile Tracker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---
## [3.0.0] - 2025-12-10

### 🎉 Major Release - Expense Tracking & Food Inventory Management

#### 🆕 New Features

**💰 Expense Tracking System**
- Complete expense management with digital receipt uploads
- Track expenses by category (12 pre-defined categories)
- Link expenses to specific reptiles or mark as general
- Upload receipts (PNG, JPG, PDF) with drag-and-drop interface
- Filter expenses by reptile, category, and date range
- Summary statistics (total spent, count, average)
- Vendor and payment method tracking
- Tags and notes support for organization
- Recurring expense flagging
- Edit and delete expenses with receipt management
- Detailed expense view with receipt preview
- Export expenses to CSV

**📦 Food Inventory Management**
- Track food stock levels with automatic deduction
- Visual stock indicators (green: good, yellow: low, red: out)
- Low stock alerts (configurable threshold)
- Out of stock warnings
- Auto-increment existing items when adding stock
- Quick "+1" and "-1" adjustment buttons
- Cost per unit tracking for expense analysis
- Supplier and purchase date tracking
- Expiry date monitoring for perishable items
- Complete transaction audit trail
- Transaction types: purchase, feeding, adjustment, waste
- Auto-suggestions for food types and sizes
- Manual quantity adjustments with notes
- Stock value calculations
- Transaction history with filtering

**📊 Expense Reports & Analytics**
- Interactive expense reports dashboard
- Expenses by category with visual bar charts
- Monthly expense trends with bar graphs
- Summary statistics cards
- Filter reports by reptile, date range, or year
- Highest/lowest month identification
- Monthly average calculations
- Print-friendly report layouts
- Export capabilities

**🔗 System Integration**
- Navigation menu updated with Expenses and Inventory links
- Active state highlighting for new sections
- Seamless integration with existing features
- Ready for feeding log integration (auto-deduct inventory)

#### 🗄️ Database Changes

**New Tables**
- `expenses` - Complete expense tracking with receipts
- `food_inventory` - Food stock management
- `inventory_transactions` - Complete audit trail

**New Database Methods (20 total)**
- Expense operations: add, get, update, delete, categories, summary, by_category, monthly
- Inventory operations: add, get, update, deduct, transactions, low_stock, out_of_stock, delete

#### 🎨 User Interface

**New Templates (9 total)**
- `expenses.html` - List view with filtering and summary stats
- `add_expense.html` - Form with drag-and-drop receipt upload
- `edit_expense.html` - Edit form with current receipt display
- `expense_details.html` - Detailed view with receipt preview
- `expense_reports.html` - Analytics dashboard with charts
- `food_inventory.html` - Grid view with stock alerts
- `add_inventory_item.html` - Stock addition form
- `inventory_item_details.html` - Item details with transaction history
- `inventory_transactions.html` - Complete transaction log

**UI Enhancements**
- Color-coded stock level indicators
- Drag-and-drop file upload interface
- Interactive charts and graphs
- Responsive grid layouts
- Mobile-optimized views
- Print-friendly report layouts

#### 🛠️ Technical Improvements

**Backend**
- 13 new Flask routes for expenses and inventory
- Receipt file handling (images and PDFs)
- File upload validation and security
- Automatic file cleanup on deletion
- Transaction logging for audit trails
- Advanced filtering and search capabilities

**Frontend**
- Modern card-based layouts
- Interactive JavaScript for file uploads
- Real-time form validation
- Responsive design patterns
- Accessibility improvements

#### 📚 Documentation

**New Documentation Files**
- `EXPENSE_AND_INVENTORY_FEATURE_SPEC.md` - Complete 398-line specification
- Comprehensive feature documentation
- Implementation roadmap
- Testing checklist
- Future enhancement ideas

#### 🔄 Migration Notes

- All new tables created automatically on first run
- No manual migration required
- Existing data preserved
- Backward compatible with v2.0.0

#### 💡 Usage Examples

**Expense Tracking**
```
1. Navigate to "💰 Expenses" in menu
2. Click "Add Expense"
3. Fill in details and drag-drop receipt
4. View in list with filters
5. Generate reports for analysis
```

**Food Inventory**
```
1. Navigate to "📦 Food Inventory" in menu
2. Click "Add Stock"
3. Enter food type, size, and quantity
4. System tracks usage and alerts on low stock
5. View transaction history for audit
```

#### 🎯 Key Benefits

- **Cost Tracking**: Know exactly how much you spend on reptile care
- **Stock Management**: Never run out of food with automatic alerts
- **Receipt Organization**: Digital receipts always accessible
- **Audit Trail**: Complete history of all inventory changes
- **Analytics**: Understand spending patterns and trends
- **Integration Ready**: Prepared for automatic inventory deduction on feeding

#### 📊 Statistics

- **Lines of Code Added**: ~3,800+
- **New Routes**: 13
- **New Templates**: 9
- **New Database Methods**: 20
- **New Tables**: 3
- **Documentation Pages**: 1 (398 lines)

#### 🐛 Deployment Fixes

**Syntax Error Resolution (4 commits)**
1. **Fix #1** (Commit `7e31f5f`): Added missing closing `''')` for `notification_settings` table
   - Issue: Unclosed SQL statement in table creation
   - Impact: Python syntax error preventing deployment

2. **Fix #2** (Commit `6f398d5`): Properly closed `expenses` table SQL statement
   - Issue: Missing closing parenthesis and `FOREIGN KEY` constraint
   - Removed orphaned closing statements from previous edits
   - Impact: IndentationError at line 155

3. **Fix #3** (Commit `6112042`): Completed `get_expenses_by_category` function
   - Issue: Incomplete function with unclosed SQL query
   - Added parameter handling, query execution, and return statement
   - Impact: IndentationError at line 1063

4. **Fix #4** (Commit `7b08ef9`): Removed orphaned triple-quote and duplicate code
   - Issue: Orphaned `'''` at line 1242 with 20 lines of duplicate code inside
   - Duplicate code from `get_expenses_by_category` trapped in string literal
   - Impact: IndentationError at line 1268, preventing Python from parsing file

**Lessons Learned**
- Always close multi-line SQL statements properly
- Verify function completeness before committing
- Watch for orphaned string literals that can trap code
- Test Python syntax locally before deploying

---


## [2.0.0] - 2025-12-10

### 🎉 Major Release - Complete Feature Overhaul

#### 🆕 New Features

**Weight & Length Tracking**
- Weight history tracking with measurements over time
- Length history tracking with growth monitoring
- Interactive charts and graphs for visualizing growth
- Add measurements with dates and notes
- View complete measurement history

**Photo Gallery System**
- Upload multiple photos per reptile
- Set primary photo for reptile profile
- Photo captions and metadata
- Delete photos with file cleanup
- Gallery view with all reptile photos

**Email & SMS Notifications**
- Email notifications via SMTP (Gmail, Outlook, etc.)
- SMS notifications via Twilio
- Customizable notification settings page
- Test notification functionality
- Daily reminder time configuration
- Advance notice settings (0-7 days)
- Overdue-only notification mode

**Data Backup & Restore**
- Complete data export to JSON format
- Backup includes all reptiles, logs, photos, and settings
- Restore from backup with merge or replace options
- Timestamped backup files
- Comprehensive data preservation

#### 🐛 Critical Bug Fixes

**Database Structure**
- Fixed: Database methods were outside class scope
- Fixed: `get_overdue_feedings()` method not accessible
- Fixed: Missing `length_history` table in schema
- Fixed: Indentation issues causing AttributeErrors

**Data Persistence**
- Fixed: Data loss on Render deployments
- Configured persistent disk storage at `/opt/render/project/data`
- Added `DATA_DIR` environment variable support
- Database and uploads now persist between deployments

**Template Errors**
- Fixed: `now()` function undefined in feeding_reminders.html
- Fixed: Duplicate closing `</a>` tag in navigation
- Fixed: Missing `db = get_db()` in photo gallery routes

**Application Stability**
- Fixed: Internal Server Error on length tracking page
- Fixed: Internal Server Error on feeding reminders page
- Fixed: Missing return statement in length tracking route

#### 📚 Documentation

**New Documentation Files**
- `DATA_PERSISTENCE.md` - Data persistence configuration guide
- `NOTIFICATION_SETUP.md` - Complete notification setup guide
- `RENDER_FIX_DATA_PERSISTENCE.md` - Troubleshooting guide
- `TEST_RESULTS.md` - Comprehensive test results
- Updated `CONTRIBUTING.md` with new feature ideas

#### 🔧 Technical Improvements

**Database Schema Updates**
- Added `weight_history` table
- Added `length_history` table
- Added `photos` table with primary photo support
- Added `notification_settings` table
- Added `feeding_reminders` table

**New Dependencies**
- `twilio>=8.0.0` - SMS notification support
- `APScheduler>=3.10.0` - Scheduled task support

**New Routes**
- `/reptile/<id>/weight` - Weight tracking page
- `/reptile/<id>/length` - Length tracking page
- `/reptile/<id>/photos` - Photo gallery
- `/notification-settings` - Notification configuration
- `/backup` - Data backup download
- `/restore` - Data restore upload

#### 🎨 UI/UX Improvements
- Mobile-responsive navigation menu
- Flash message auto-dismiss
- Improved card layouts
- Better form styling
- Consistent color scheme
- Loading states and feedback

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

- **v2.0.0** (2025-12-10) - Major Release: Weight/Length Tracking, Photo Gallery, Notifications, Backup/Restore
- **v1.1.0** (2024-12-10) - Data Import Feature
- **v1.0.1** (2024-12-10) - Critical Bug Fixes
- **v1.0.0** (2024-12-09) - Initial Release

---

## Upcoming Features

### Planned for v2.1.0
- [ ] Automated notification scheduler (APScheduler/cron)
- [ ] Health records & veterinary visit tracking
- [ ] Temperature & humidity logging with graphs
- [ ] Breeding records and genetics tracking

### Planned for v2.2.0
- [ ] Expense tracking for food, supplies, vet visits
- [ ] Multiple enclosure management
- [ ] Feeding calculator (prey size recommendations)
- [ ] Growth rate analysis with ML predictions
- [ ] Medication reminders and tracking
- [ ] QR code labels for enclosures

### Under Consideration
- [ ] Mobile-responsive PWA
- [ ] Multi-user support with permissions
- [ ] Smart device integration (thermostats, cameras)
- [ ] Social features (share profiles, connect with keepers)
- [ ] Dark/light theme toggle
- [ ] Multi-language support
- [ ] Voice commands integration
- [ ] AI-powered health insights

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