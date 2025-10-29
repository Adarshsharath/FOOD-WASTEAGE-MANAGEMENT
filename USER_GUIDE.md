# Food Rescue Platform - User Guide

## Quick Start

### Running the Application
```bash
streamlit run src/app/main_sqlite.py
```

The app will open in your browser at `http://localhost:8501`

---

## Page Navigation

### 1. Home / Dashboard 🏠
**What it does:**
- Shows key metrics (providers, receivers, listings, claims)
- Displays charts for claims status distribution
- Shows weekly claims trends
- Lists all food items with filtering options

**How to use:**
- View overall statistics at the top
- Use filters to find specific food items by city, food type, or meal type
- Items near expiry (≤3 days) are highlighted in red

---

### 2. Manage Listings 📝
**What it does:**
- Add new food listings
- Edit existing listings
- Delete listings

**How to use:**

#### Adding a Listing:
1. Expand "Add Listing"
2. Use the suggested Food ID or enter your own
3. Fill in all required fields:
   - Food Name
   - Quantity
   - Expiry Date
   - Provider (select from dropdown)
   - Provider Type
   - Location
   - Food Type
   - Meal Type
4. Click "Create"

#### Editing a Listing:
1. Expand "Edit Listing"
2. Select the Food ID from dropdown
3. Modify the fields you want to change
4. Click "Update"

#### Deleting a Listing:
1. Expand "Delete Listing"
2. Select the Food ID from dropdown
3. Read the warning
4. Click "Confirm Delete"

---

### 3. Manage Claims 🎯
**What it does:**
- Create new claims (receivers claiming food items)
- Update claim status
- View all claims

**How to use:**

#### Adding a Claim:
1. Expand "Add Claim"
2. Use the suggested Claim ID or enter your own
3. Select the food item from dropdown
4. Select the receiver from dropdown
5. Choose status (Pending/Completed/Cancelled)
6. Click "Create Claim"

#### Updating Claim Status:
1. Expand "Update Claim Status"
2. Select the claim from dropdown
3. Choose new status
4. Click "Update Status"

---

### 4. Providers & Receivers 👥
**What it does:**
- Manage food providers (restaurants, groceries, etc.)
- Manage food receivers (food banks, shelters, etc.)
- Export contact lists

**How to use:**

#### Providers Tab:
- View all providers in a table
- Export provider contacts as CSV
- Add/Edit/Delete providers using the form

#### Receivers Tab:
- View all receivers in a table
- Add/Edit/Delete receivers using the form

#### Adding a Provider/Receiver:
1. Select "Add" from Action dropdown
2. Use the suggested ID or enter your own
3. Fill in required fields:
   - Name (required)
   - Contact (required)
   - Type (optional)
   - City (optional)
   - Address (optional for providers)
4. Click "Submit"

#### Editing a Provider/Receiver:
1. Select "Edit" from Action dropdown
2. Enter the ID you want to edit
3. Fill in the new values
4. Click "Submit"

#### Deleting a Provider/Receiver:
1. Select "Delete" from Action dropdown
2. Enter the ID you want to delete
3. Click "Submit"

---

### 5. SQL Queries & Analysis 📊
**What it does:**
- Run predefined SQL queries
- Analyze data patterns
- Export query results

**Available Queries:**
1. Providers and receivers per city
2. Top provider type
3. Provider contacts in city
4. Top receivers by claims
5. Total quantity available
6. City with most listings
7. Most common food types
8. Claims per food item
9. Claims status distribution
10. Food listings near expiry (≤3 days)
11. Claims per week (time-series)

**How to use:**
1. Scroll to the query you want to run
2. Click "SQL" expander to view the SQL code
3. For queries with parameters (like city), select the parameter
4. Click "Run: [Query Name]"
5. View results in the table
6. Click "Export result CSV" to download

---

### 6. EDA / Insights 📈
**What it does:**
- Visualize data trends
- Identify patterns
- Monitor expiry risks

**Charts Available:**
- Listings by City (bar chart)
- Listings by Meal Type (bar chart)
- Listings near expiry (table)

**How to use:**
- Simply navigate to this page
- All charts load automatically
- Scroll to view different insights

---

### 7. Admin / Deploy ⚙️
**What it does:**
- Re-import CSV data
- View database statistics
- Backup database to CSV
- Export SQL schema

**How to use:**

#### Re-import CSV Data:
1. Click "🔄 Re-import CSV Data"
2. Wait for import to complete
3. Check row counts to verify

#### View Statistics:
- Row counts are displayed automatically

#### Backup Database:
1. Click "💾 Backup DB to CSV (tables)"
2. Download buttons will appear for each table
3. Click to download individual tables

#### Export Schema:
1. Click "📄 Export SQL dump"
2. Click "📥 Download schema.sql"

---

## Tips & Best Practices

### 1. **Use Auto-Generated IDs**
- The system suggests the next available ID
- This prevents duplicate ID errors
- You can still use custom IDs if needed

### 2. **Fill Required Fields**
- Fields marked as required must be filled
- The system will show validation errors if you miss any

### 3. **Check Dependencies**
- Add providers before adding listings
- Add receivers before creating claims
- Add listings before creating claims

### 4. **Monitor Expiry Dates**
- Items near expiry are highlighted in red on the dashboard
- Check the "Food listings near expiry" query regularly

### 5. **Export Data Regularly**
- Use the Admin page to backup your data
- Export important contact lists from Providers & Receivers page

### 6. **Use Filters**
- On the dashboard, use filters to find specific items
- Filter by city, food type, or meal type

---

## Common Error Messages

### ❌ "Food ID already exists!"
**Cause:** Trying to add a listing with an ID that's already in use
**Solution:** Use the suggested next ID or choose a different ID

### ❌ "Provider name is required!"
**Cause:** Trying to submit a form without filling required fields
**Solution:** Fill in all required fields before submitting

### ❌ "No providers found. Please add providers first"
**Cause:** Trying to add a listing when no providers exist
**Solution:** Go to "Providers & Receivers" page and add a provider first

### ❌ "Invalid Food ID or Receiver ID"
**Cause:** Trying to create a claim with non-existent Food or Receiver
**Solution:** Verify the Food and Receiver exist in the database

---

## Data Flow

```
1. Add Providers → 2. Add Food Listings → 3. Add Receivers → 4. Create Claims
```

**Recommended Order:**
1. Start by adding providers (restaurants, groceries, etc.)
2. Add food listings from those providers
3. Add receivers (food banks, shelters, etc.)
4. Create claims when receivers claim food items
5. Update claim status as they progress

---

## Database Location

The SQLite database is stored at:
```
FOOD MANAGEMENT SYSTEM/food_rescue.db
```

To reset the database:
1. Stop the Streamlit app
2. Delete `food_rescue.db`
3. Restart the app
4. Data will be re-imported from CSV files in the `data/` directory

---

## CSV Data Files

Located in `data/` directory:
- `providers_data.csv` - Provider information
- `receivers_data.csv` - Receiver information
- `food_listings_data.csv` - Food listings
- `claims_data.csv` - Claims data

**CSV Format:**
- Column names can be in any case (Food_ID or food_id)
- Dates should be in format: `M/D/YYYY` (e.g., `3/17/2025`)
- Timestamps should be in format: `M/D/YYYY H:MM` (e.g., `3/5/2025 5:26`)

---

## Support

If you encounter any issues:
1. Check the error message for specific guidance
2. Verify you've followed the data flow (providers → listings → receivers → claims)
3. Check that all required fields are filled
4. Try using the suggested auto-generated IDs
5. Review the FIXES_SUMMARY.md for technical details

---

## Features Summary

✅ Full CRUD operations for all entities
✅ Auto-generated IDs to prevent duplicates
✅ Input validation and error handling
✅ CSV import/export functionality
✅ Interactive charts and visualizations
✅ SQL query interface
✅ Audit logging
✅ Contact list exports
✅ Expiry date monitoring
✅ Status tracking for claims

---

**Enjoy using the Food Rescue Platform! 🍽️**
