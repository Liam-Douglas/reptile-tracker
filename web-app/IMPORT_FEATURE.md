# 📥 Data Import Feature

## Overview

The Reptile Tracker now supports bulk data import from Excel and CSV files. This feature allows you to:
- Import multiple reptiles at once
- Bulk import feeding logs
- Bulk import shed records
- Download pre-formatted templates
- Validate data before import

## How to Use

### 1. Access the Import Page

Navigate to **Import Data** from the main menu or visit `/import`

### 2. Download a Template

Choose the type of data you want to import:
- **Reptiles** - Import your reptile collection
- **Feeding Logs** - Import feeding history
- **Shed Records** - Import shed tracking data

Click the "Download Template" button for your chosen data type.

### 3. Fill in Your Data

Open the downloaded Excel file and fill in your data:
- Keep the column headers exactly as shown
- You can delete the example row
- Leave optional fields empty if not needed
- Follow the format guidelines below

### 4. Upload and Import

1. Select the data type from the dropdown
2. Choose your filled-in file
3. Click "Upload and Import"
4. Review the results - any errors will be displayed

## Data Formats

### Reptiles Template

| Column | Required | Format | Example |
|--------|----------|--------|---------|
| name | ✅ Yes | Text | "Monty" |
| species | ✅ Yes | Text | "Ball Python" |
| morph | No | Text | "Banana" |
| sex | No | Text | "Male" or "Female" |
| date_of_birth | No | YYYY-MM-DD | "2023-01-15" |
| acquisition_date | No | YYYY-MM-DD | "2023-06-20" |
| weight_grams | No | Number | 250.5 |
| length_cm | No | Number | 90.0 |
| notes | No | Text | "Healthy and active" |

### Feeding Logs Template

| Column | Required | Format | Example |
|--------|----------|--------|---------|
| reptile_name | ✅ Yes | Text (must exist) | "Monty" |
| feeding_date | ✅ Yes | YYYY-MM-DD | "2024-01-15" |
| food_type | ✅ Yes | Text | "Mouse" |
| food_size | No | Text | "Medium" |
| quantity | No | Number | 1 |
| ate | No | yes/no | "yes" |
| notes | No | Text | "Ate well" |

**Important**: The reptile must already exist in your database before importing feeding logs.

### Shed Records Template

| Column | Required | Format | Example |
|--------|----------|--------|---------|
| reptile_name | ✅ Yes | Text (must exist) | "Monty" |
| shed_date | ✅ Yes | YYYY-MM-DD | "2024-01-20" |
| complete | No | yes/no | "yes" |
| shed_length_cm | No | Number | 95.0 |
| notes | No | Text | "Complete shed" |

**Important**: The reptile must already exist in your database before importing shed records.

## Tips for Successful Import

### ✅ Do's

- **Use the templates** - They have the correct column headers
- **Check dates** - Use YYYY-MM-DD format (e.g., 2024-01-15)
- **Import reptiles first** - Before importing feeding logs or shed records
- **Use consistent names** - Reptile names must match exactly
- **Test with small batches** - Try importing a few rows first
- **Keep backups** - Save your original data before importing

### ❌ Don'ts

- **Don't change column headers** - Keep them exactly as in the template
- **Don't use different date formats** - Stick to YYYY-MM-DD
- **Don't import logs for non-existent reptiles** - Add reptiles first
- **Don't leave required fields empty** - They're marked with *
- **Don't use special characters in names** - Keep it simple

## Error Handling

If errors occur during import:
- **Partial Import**: Successfully imported rows are saved
- **Error Messages**: Specific errors are shown for each failed row
- **Row Numbers**: Errors reference the row number in your file
- **Fix and Retry**: Correct the errors and re-upload

Common errors:
- "Missing required fields" - Fill in all required columns
- "Reptile not found" - Add the reptile first or check spelling
- "Invalid date format" - Use YYYY-MM-DD format
- "Invalid number" - Check numeric fields for text

## File Format Support

### Supported Formats

- **Excel (.xlsx)** - Recommended, best compatibility
- **Excel 97-2003 (.xls)** - Older Excel format
- **CSV (.csv)** - Comma-separated values

### File Size Limits

- Maximum file size: 16MB
- Recommended: Under 1000 rows per import
- For larger datasets: Split into multiple files

## Examples

### Example 1: Importing 3 Reptiles

```
name,species,morph,sex,date_of_birth,acquisition_date,weight_grams,length_cm,notes
Monty,Ball Python,Banana,Male,2023-01-15,2023-06-20,250.5,90.0,Healthy
Slinky,Corn Snake,Amelanistic,Female,2022-05-10,2023-01-15,180.0,75.5,Very active
Rex,Bearded Dragon,,Male,2023-03-20,2023-08-01,350.0,40.0,Loves greens
```

### Example 2: Importing Feeding Logs

```
reptile_name,feeding_date,food_type,food_size,quantity,ate,notes
Monty,2024-01-15,Mouse,Medium,1,yes,Ate immediately
Monty,2024-01-22,Mouse,Medium,1,yes,Good appetite
Slinky,2024-01-16,Pinkie Mouse,Small,2,yes,Ate both
```

### Example 3: Importing Shed Records

```
reptile_name,shed_date,complete,shed_length_cm,notes
Monty,2024-01-20,yes,95.0,Perfect shed
Slinky,2024-01-18,yes,80.5,Complete in one piece
Rex,2024-01-25,no,,Stuck shed on toes
```

## Google Sheets Integration

You can also use Google Sheets:

1. Create a new Google Sheet
2. Copy the template format
3. Fill in your data
4. Download as Excel (.xlsx) or CSV
5. Upload to Reptile Tracker

## Troubleshooting

### Import button doesn't work
- Check file format (.xlsx, .xls, or .csv)
- Ensure file size is under 16MB
- Try a different browser

### All rows show errors
- Verify column headers match template exactly
- Check for hidden characters or extra spaces
- Re-download the template and try again

### Some rows imported, others failed
- Review error messages for specific issues
- Fix the failed rows in your file
- Re-upload (already imported rows will be duplicated)

### Reptile names not matching
- Check for extra spaces
- Verify exact spelling
- Names are case-sensitive

## Best Practices

1. **Start Small**: Test with 5-10 rows first
2. **Backup First**: Export existing data before large imports
3. **Clean Data**: Remove duplicates and fix formatting before import
4. **Validate Dates**: Ensure all dates are in YYYY-MM-DD format
5. **Check Names**: Verify reptile names match exactly
6. **Review Results**: Check imported data after upload
7. **Keep Templates**: Save filled templates for future reference

## Technical Details

### Supported by
- **pandas** - Data processing library
- **openpyxl** - Excel file handling
- **Flask** - Web framework

### Database Operations
- Bulk insert with transaction support
- Row-by-row validation
- Automatic error collection
- Partial import on errors

### Security
- File type validation
- Size limit enforcement
- SQL injection prevention
- Input sanitization

---

**Need Help?** Check the Field Reference section on the Import Data page for detailed column descriptions.