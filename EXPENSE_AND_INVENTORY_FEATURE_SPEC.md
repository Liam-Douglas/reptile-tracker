# Expense Tracking & Food Inventory Feature Specification

## Overview
This document outlines the new Expense Tracking and Food Inventory Management features for the Reptile Tracker application.

## Features Implemented

### 1. Database Schema ✅

#### Expenses Table
Tracks all expenses related to reptile care with the following fields:
- `id` - Primary key
- `reptile_id` - Optional link to specific reptile (NULL for general expenses)
- `expense_date` - Date of expense
- `category` - Expense category (Food, Supplies, Vet, Equipment, etc.)
- `amount` - Cost amount
- `currency` - Currency code (default: USD)
- `vendor` - Where purchased
- `description` - Expense description
- `receipt_path` - Path to uploaded receipt image/PDF
- `payment_method` - How paid (Cash, Card, etc.)
- `is_recurring` - Boolean for recurring expenses
- `tags` - Comma-separated tags for filtering
- `notes` - Additional notes
- `created_at` / `updated_at` - Timestamps

#### Food Inventory Table
Tracks food stock levels with automatic deduction on feeding:
- `id` - Primary key
- `food_type` - Type of food (Rat, Mouse, Cricket, etc.)
- `food_size` - Size (Small, Medium, Large, Pinkie, etc.)
- `quantity` - Current stock quantity
- `unit` - Unit of measurement (items, grams, etc.)
- `cost_per_unit` - Cost per item
- `supplier` - Where purchased
- `purchase_date` - When purchased
- `expiry_date` - Expiration date
- `notes` - Additional notes
- `created_at` / `updated_at` - Timestamps
- **UNIQUE constraint** on (food_type, food_size) to prevent duplicates

#### Inventory Transactions Table
Logs all inventory changes for audit trail:
- `id` - Primary key
- `inventory_id` - Link to food_inventory
- `transaction_type` - Type (purchase, feeding, adjustment, waste)
- `quantity` - Quantity changed (positive or negative)
- `transaction_date` - When transaction occurred
- `reference_id` - Link to related record (e.g., feeding_log_id)
- `reference_type` - Type of reference (feeding_log, etc.)
- `notes` - Transaction notes
- `created_at` - Timestamp

### 2. Database Methods ✅

#### Expense Operations
- `add_expense()` - Create new expense record
- `get_expense(expense_id)` - Get single expense with reptile name
- `get_expenses()` - Get expenses with filtering (reptile, category, date range, pagination)
- `update_expense()` - Update expense details
- `delete_expense()` - Remove expense
- `get_expense_categories()` - Get unique categories
- `get_expense_summary()` - Get statistics (count, total, average)
- `get_expenses_by_category()` - Group expenses by category
- `get_monthly_expenses()` - Get monthly totals for charts

#### Food Inventory Operations
- `add_food_item()` - Add or update inventory (auto-increments if exists)
- `get_food_inventory()` - Get all items (optional: include zero stock)
- `get_food_item(inventory_id)` - Get single item
- `get_food_item_by_type()` - Find by food type and size
- `update_food_quantity()` - Adjust quantity with transaction logging
- `deduct_food_from_feeding()` - Auto-deduct when feeding logged
- `get_inventory_transactions()` - Get transaction history
- `get_low_stock_items()` - Get items below threshold
- `get_out_of_stock_items()` - Get items with zero stock
- `delete_food_item()` - Remove inventory item

## Features To Implement

### 3. Flask Routes (app.py)

#### Expense Routes
```python
@app.route('/expenses')
def expenses_list()
    # Display all expenses with filtering options
    # Filters: reptile, category, date range
    # Show summary statistics

@app.route('/expense/add', methods=['GET', 'POST'])
def add_expense()
    # Form to add new expense
    # Support receipt upload (images and PDFs)
    # Auto-populate reptile dropdown

@app.route('/expense/<int:expense_id>')
def expense_details(expense_id)
    # View single expense with receipt
    # Edit and delete options

@app.route('/expense/<int:expense_id>/edit', methods=['GET', 'POST'])
def edit_expense(expense_id)
    # Edit expense form

@app.route('/expense/<int:expense_id>/delete', methods=['POST'])
def delete_expense(expense_id)
    # Delete expense with confirmation

@app.route('/expenses/reports')
def expense_reports()
    # Analytics dashboard
    # Charts: by category, monthly trends, per-reptile costs
    # Export to CSV
```

#### Food Inventory Routes
```python
@app.route('/inventory')
def food_inventory()
    # Display all food items
    # Show current stock, low stock alerts
    # Quick add/adjust buttons

@app.route('/inventory/add', methods=['GET', 'POST'])
def add_inventory_item()
    # Form to add new food type
    # Or add quantity to existing

@app.route('/inventory/<int:inventory_id>')
def inventory_item_details(inventory_id)
    # View item details
    # Transaction history
    # Edit/delete options

@app.route('/inventory/<int:inventory_id>/adjust', methods=['POST'])
def adjust_inventory(inventory_id)
    # Quick quantity adjustment
    # AJAX endpoint for instant updates

@app.route('/inventory/transactions')
def inventory_transactions()
    # Full transaction log
    # Filter by item, date, type

@app.route('/inventory/low-stock')
def low_stock_alert()
    # Show items needing restock
    # Generate shopping list
```

#### Integration with Feeding Logs
```python
# Modify existing add_feeding route to:
# 1. Check if food type/size exists in inventory
# 2. Show current stock quantity
# 3. Auto-deduct from inventory when feeding logged
# 4. Warn if stock is low or out
```

### 4. Templates

#### expenses.html
- List view with filters (category, reptile, date range)
- Summary cards (total spent, average, count)
- Table with: date, category, amount, reptile, vendor, receipt icon
- Add expense button
- Export to CSV button

#### add_expense.html / edit_expense.html
- Form fields for all expense data
- Reptile dropdown (optional)
- Category dropdown with common categories
- Receipt upload (drag-and-drop)
- Preview uploaded receipt
- Save and cancel buttons

#### expense_reports.html
- Summary statistics cards
- Chart: Expenses by category (pie chart)
- Chart: Monthly expenses (line/bar chart)
- Chart: Per-reptile costs (bar chart)
- Date range selector
- Export options

#### food_inventory.html
- Grid/table view of all food items
- Color-coded stock levels (green: good, yellow: low, red: out)
- Quick add quantity buttons
- Low stock alerts banner
- Add new item button
- Filter by food type

#### add_inventory_item.html
- Form for new food item
- Auto-suggest existing types/sizes
- Quantity, cost, supplier fields
- Purchase and expiry dates
- Save button

#### inventory_transactions.html
- Transaction log table
- Filters: item, date range, transaction type
- Shows: date, item, type, quantity change, reference
- Export to CSV

### 5. Receipt Upload Functionality

#### File Handling
- Accept: JPG, PNG, PDF
- Max size: 10MB
- Store in: `/uploads/receipts/`
- Filename format: `receipt_{expense_id}_{timestamp}.{ext}`

#### Optional: OCR Integration
- Use Tesseract or cloud OCR API
- Extract: date, amount, vendor
- Pre-fill form fields
- User can review/edit

### 6. UI/UX Enhancements

#### Navigation
Add to base.html navigation:
- "💰 Expenses" link
- "📦 Inventory" link with low stock badge

#### Dashboard Integration
Add to main dashboard:
- "Recent Expenses" widget (last 5)
- "Low Stock Alert" widget
- "Monthly Spending" summary card

#### Feeding Log Integration
When adding feeding:
- Show current stock for selected food
- Warning if stock is low
- Auto-deduct option (checkbox, default: checked)
- Link to add more stock if needed

### 7. Suggested Expense Categories

**Pre-defined categories:**
- Food & Feeders
- Supplements & Vitamins
- Veterinary Care
- Medications
- Enclosure & Habitat
- Heating & Lighting
- Substrate & Bedding
- Décor & Enrichment
- Cleaning Supplies
- Equipment & Tools
- Breeding Supplies
- Other

### 8. Food Inventory Features

#### Stock Management
- **Add Stock**: Purchase new items or restock existing
- **Adjust Stock**: Manual corrections (waste, loss, etc.)
- **Auto-Deduct**: Automatic deduction when feeding logged
- **Transaction Log**: Complete audit trail

#### Alerts & Notifications
- Low stock warnings (configurable threshold)
- Out of stock alerts
- Expiring food notifications
- Shopping list generation

#### Reporting
- Stock value calculation (quantity × cost_per_unit)
- Usage patterns (most fed items)
- Waste tracking
- Cost per feeding analysis

## Implementation Priority

### Phase 1: Core Functionality (High Priority)
1. ✅ Database schema and methods
2. Expense list and add/edit routes
3. Basic expense templates
4. Food inventory list and add routes
5. Basic inventory templates
6. Navigation links

### Phase 2: Integration (Medium Priority)
7. Receipt upload functionality
8. Feeding log integration (auto-deduct)
9. Low stock alerts
10. Dashboard widgets

### Phase 3: Analytics (Lower Priority)
11. Expense reports and charts
12. Inventory transaction history
13. Export to CSV
14. Advanced filtering

### Phase 4: Enhancements (Future)
15. OCR for receipts
16. Recurring expense automation
17. Budget tracking
18. Mobile-optimized views
19. Barcode scanning for inventory

## Technical Notes

### Database Migrations
- Tables will be created automatically on first run
- Existing data is preserved
- No manual migration needed

### File Storage
- Receipts stored in `/uploads/receipts/`
- Ensure directory has write permissions
- Consider cloud storage for production (S3, etc.)

### Performance Considerations
- Add indexes on frequently queried fields:
  - `expenses.expense_date`
  - `expenses.category`
  - `expenses.reptile_id`
  - `food_inventory.food_type`
  - `inventory_transactions.transaction_date`

### Security
- Validate file uploads (type, size)
- Sanitize user inputs
- Use parameterized queries (already implemented)
- Restrict file access to authenticated users

## Testing Checklist

- [ ] Add expense with receipt upload
- [ ] Edit expense and update receipt
- [ ] Delete expense (verify receipt file deleted)
- [ ] Filter expenses by category, reptile, date
- [ ] View expense reports and charts
- [ ] Add new food item to inventory
- [ ] Add quantity to existing item
- [ ] Log feeding and verify auto-deduction
- [ ] Adjust inventory manually
- [ ] View transaction history
- [ ] Check low stock alerts
- [ ] Export data to CSV
- [ ] Test with multiple reptiles
- [ ] Test with large datasets (100+ expenses)

## Future Enhancements

1. **Budget Management**
   - Set monthly/yearly budgets
   - Track spending vs budget
   - Alerts when approaching limit

2. **Supplier Management**
   - Track preferred suppliers
   - Compare prices
   - Reorder reminders

3. **Inventory Forecasting**
   - Predict when stock will run out
   - Suggest reorder quantities
   - Seasonal usage patterns

4. **Mobile App**
   - Quick expense entry
   - Barcode scanning
   - Receipt photo capture

5. **Multi-User Support**
   - Shared expenses
   - User-specific budgets
   - Permission levels

## Documentation Updates Needed

- [ ] Update README.md with new features
- [ ] Create EXPENSE_TRACKING_GUIDE.md
- [ ] Create INVENTORY_MANAGEMENT_GUIDE.md
- [ ] Update CHANGELOG.md
- [ ] Add screenshots to documentation
- [ ] Create video tutorial

---

**Status**: Database layer complete ✅  
**Next Step**: Implement Flask routes and templates  
**Estimated Completion**: Phase 1 - 4-6 hours of development