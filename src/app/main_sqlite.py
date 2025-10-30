import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Food Rescue Platform",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #FF6B6B;
        --secondary-color: #4ECDC4;
        --success-color: #95E1D3;
        --warning-color: #FFE66D;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        color: white;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Headers */
    h1 {
        color: #667eea;
        font-weight: 700;
        padding-bottom: 1rem;
        border-bottom: 3px solid #667eea;
    }
    
    h2 {
        color: #764ba2;
        font-weight: 600;
        margin-top: 1.5rem;
    }
    
    h3 {
        color: #4ECDC4;
        font-weight: 600;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 600;
        color: #666;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    /* Form inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        padding: 0.5rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 8px;
        font-weight: 600;
        color: #667eea;
    }
    
    /* Success/Error/Warning messages */
    .stSuccess {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 4px;
        padding: 1rem;
    }
    
    .stError {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 4px;
        padding: 1rem;
    }
    
    .stWarning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 4px;
        padding: 1rem;
    }
    
    .stInfo {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 4px;
        padding: 1rem;
    }
    
    /* Cards */
    .css-1r6slb0 {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Radio buttons */
    .stRadio > label {
        font-weight: 600;
        color: #667eea;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
        color: white;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / 'food_rescue.db'

def get_db_connection():
    """Create SQLite database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def migrate_database():
    """Migrate existing database to add new columns if needed"""
    if DB_PATH.exists():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if claimed_quantity column exists in claims table
            cursor.execute("PRAGMA table_info(claims)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'claimed_quantity' not in columns:
                # Add the claimed_quantity column with default value 0
                cursor.execute("ALTER TABLE claims ADD COLUMN claimed_quantity INTEGER DEFAULT 0")
                conn.commit()
                st.info("✅ Database migrated: Added 'claimed_quantity' column to claims table")
        except Exception as e:
            st.warning(f"Migration check: {str(e)}")
        finally:
            conn.close()

def import_csv_data():
    """Import CSV files from data/ directory"""
    DATA_DIR = ROOT / 'data'
    
    if not DATA_DIR.exists():
        st.error(f"Data directory {DATA_DIR} not found! Please create it and put your CSV files there.")
        return False
    
    csv_files = list(DATA_DIR.glob('*.csv'))
    if not csv_files:
        st.error(f"No CSV files found in {DATA_DIR}. Please add your CSV files there.")
        return False
    
    st.info(f"Found CSV files: {[f.name for f in csv_files]}")
    
    # Create tables
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.execute("DROP TABLE IF EXISTS claims")
    cursor.execute("DROP TABLE IF EXISTS food_listings")
    cursor.execute("DROP TABLE IF EXISTS receivers")
    cursor.execute("DROP TABLE IF EXISTS providers")
    cursor.execute("DROP TABLE IF EXISTS audit_log")
    
    # Create tables
    cursor.execute('''
        CREATE TABLE providers (
            provider_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT,
            address TEXT,
            city TEXT,
            contact TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE receivers (
            receiver_id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT,
            city TEXT,
            contact TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE food_listings (
            food_id INTEGER PRIMARY KEY,
            food_name TEXT,
            quantity INTEGER,
            expiry_date DATE,
            provider_id INTEGER,
            provider_type TEXT,
            location TEXT,
            food_type TEXT,
            meal_type TEXT,
            FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE claims (
            claim_id INTEGER PRIMARY KEY,
            food_id INTEGER,
            receiver_id INTEGER,
            status TEXT CHECK (status IN ('Pending','Completed','Cancelled')),
            timestamp DATETIME,
            FOREIGN KEY (food_id) REFERENCES food_listings(food_id),
            FOREIGN KEY (receiver_id) REFERENCES receivers(receiver_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation TEXT NOT NULL,
            user TEXT DEFAULT 'streamlit',
            details TEXT,
            ts_utc DATETIME NOT NULL
        )
    ''')
    
    # Import data from CSV files
    import_order = ['providers', 'receivers', 'food_listings', 'claims']
    
    for table in import_order:
        csv_file = DATA_DIR / f"{table}_data.csv"
        if csv_file.exists():
            try:
                df = pd.read_csv(csv_file)
                st.write(f"Importing {table}: {len(df)} rows")
                
                # Clean the data
                df = df.copy()
                
                # Normalize column names to lowercase with underscores
                df.columns = df.columns.str.lower().str.replace(' ', '_')
                
                # Handle expiry_date - convert to ISO format, drop invalid
                if 'expiry_date' in df.columns:
                    # Try multiple date formats
                    df['expiry_date'] = pd.to_datetime(df['expiry_date'], format='%m/%d/%Y', errors='coerce')
                    if df['expiry_date'].isna().all():
                        df['expiry_date'] = pd.to_datetime(df['expiry_date'], errors='coerce')
                    df = df.dropna(subset=['expiry_date'])
                    df['expiry_date'] = df['expiry_date'].dt.strftime('%Y-%m-%d')
                
                # Handle timestamp - convert to ISO format
                if 'timestamp' in df.columns:
                    # Try multiple timestamp formats
                    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%m/%d/%Y %H:%M', errors='coerce')
                    if df['timestamp'].isna().all():
                        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                    df = df.dropna(subset=['timestamp'])
                    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
                
                # Handle quantity - convert to integer, NULL for negative/missing
                if 'quantity' in df.columns:
                    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
                    df.loc[df['quantity'] < 0, 'quantity'] = None
                
                # Handle contact - normalize phone numbers
                if 'contact' in df.columns:
                    df['contact'] = df['contact'].astype(str).str.strip()
                
                # Deduplicate by contact for providers and receivers
                if table in ['providers', 'receivers'] and 'contact' in df.columns:
                    df = df.drop_duplicates(subset=['contact'], keep='first')
                
                st.write(f"After cleaning: {len(df)} rows")
                
                # Insert data
                if not df.empty:
                    placeholders = ', '.join(['?' for _ in df.columns])
                    columns = ', '.join(df.columns)
                    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                    
                    for _, row in df.iterrows():
                        cursor.execute(query, tuple(row))
                    
                    st.success(f"✅ {table}: {len(df)} rows imported")
                else:
                    st.warning(f"⚠️ {table}: No data after cleaning")
                    
            except Exception as e:
                st.error(f"❌ Error importing {table}: {str(e)}")
                return False
        else:
            st.warning(f"⚠️ {csv_file} not found, skipping {table}")
    
    conn.commit()
    conn.close()
    st.success("🎉 CSV import completed!")
    return True

def init_database():
    """Initialize the database - either with CSV import or sample data"""
    if not DB_PATH.exists():
        st.info("🔄 First time setup - initializing database...")
        
        # Check if CSV files exist
        DATA_DIR = ROOT / 'data'
        if DATA_DIR.exists() and list(DATA_DIR.glob('*.csv')):
            st.write("📁 Found CSV files - importing real data...")
            if import_csv_data():
                return
            else:
                st.warning("⚠️ CSV import failed, using sample data instead")
        
        # Fallback to sample data
        st.write("📊 Using sample data...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS providers (
                provider_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                address TEXT,
                city TEXT,
                contact TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS receivers (
                receiver_id INTEGER PRIMARY KEY,
                name TEXT,
                type TEXT,
                city TEXT,
                contact TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS food_listings (
                food_id INTEGER PRIMARY KEY,
                food_name TEXT,
                quantity INTEGER,
                expiry_date DATE,
                provider_id INTEGER,
                provider_type TEXT,
                location TEXT,
                food_type TEXT,
                meal_type TEXT,
                FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS claims (
                claim_id INTEGER PRIMARY KEY,
                food_id INTEGER,
                receiver_id INTEGER,
                claimed_quantity INTEGER DEFAULT 0,
                status TEXT CHECK (status IN ('Pending','Completed','Cancelled')),
                timestamp DATETIME,
                FOREIGN KEY (food_id) REFERENCES food_listings(food_id),
                FOREIGN KEY (receiver_id) REFERENCES receivers(receiver_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation TEXT NOT NULL,
                user TEXT DEFAULT 'streamlit',
                details TEXT,
                ts_utc DATETIME NOT NULL
            )
        ''')
        
        # Insert sample data
        cursor.execute('''
            INSERT INTO providers (provider_id, name, type, city, contact) VALUES 
            (1, 'Restaurant A', 'Restaurant', 'New York', '+1-555-0101'),
            (2, 'Cafe B', 'Cafe', 'Los Angeles', '+1-555-0102'),
            (3, 'Grocery C', 'Grocery', 'Chicago', '+1-555-0103'),
            (4, 'Bakery D', 'Bakery', 'Houston', '+1-555-0104'),
            (5, 'Hotel E', 'Hotel', 'Phoenix', '+1-555-0105')
        ''')
        
        cursor.execute('''
            INSERT INTO receivers (receiver_id, name, type, city, contact) VALUES 
            (1, 'Food Bank A', 'Food Bank', 'New York', '+1-555-0201'),
            (2, 'Shelter B', 'Shelter', 'Los Angeles', '+1-555-0202'),
            (3, 'Community C', 'Community', 'Chicago', '+1-555-0203'),
            (4, 'Church D', 'Church', 'Houston', '+1-555-0204'),
            (5, 'School E', 'School', 'Phoenix', '+1-555-0205')
        ''')
        
        cursor.execute('''
            INSERT INTO food_listings (food_id, food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type) VALUES 
            (1, 'Bread', 50, '2025-01-15', 1, 'Restaurant', 'Kitchen A', 'Bread', 'Breakfast'),
            (2, 'Rice', 100, '2025-02-01', 2, 'Cafe', 'Storage B', 'Grain', 'Lunch'),
            (3, 'Vegetables', 75, '2025-01-20', 3, 'Grocery', 'Warehouse C', 'Vegetables', 'Dinner'),
            (4, 'Fruits', 60, '2025-01-25', 4, 'Bakery', 'Bakery D', 'Fruits', 'Snack'),
            (5, 'Milk', 30, '2025-01-18', 5, 'Hotel', 'Kitchen E', 'Dairy', 'Breakfast'),
            (6, 'Cheese', 25, '2025-01-30', 1, 'Restaurant', 'Kitchen A', 'Dairy', 'Lunch'),
            (7, 'Pasta', 80, '2025-02-05', 2, 'Cafe', 'Storage B', 'Grain', 'Dinner'),
            (8, 'Meat', 40, '2025-01-22', 3, 'Grocery', 'Warehouse C', 'Protein', 'Dinner')
        ''')
        
        cursor.execute('''
            INSERT INTO claims (claim_id, food_id, receiver_id, status, timestamp) VALUES 
            (1, 1, 1, 'Completed', '2025-01-10 10:00:00'),
            (2, 2, 2, 'Pending', '2025-01-11 14:30:00'),
            (3, 3, 3, 'Completed', '2025-01-12 09:15:00'),
            (4, 4, 4, 'Cancelled', '2025-01-13 16:45:00'),
            (5, 5, 5, 'Pending', '2025-01-14 11:20:00')
        ''')
        
        conn.commit()
        conn.close()
        st.success('✅ Database initialized with sample data!')

def run_query(query, params=None):
    """Run a SQL query and return results as DataFrame"""
    conn = get_db_connection()
    try:
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()

def execute_query(query, params=None):
    """Execute a SQL query (INSERT, UPDATE, DELETE)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()

def log_audit(operation, details=''):
    """Log an operation to audit log"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    execute_query(
        "INSERT INTO audit_log(operation, user, details, ts_utc) VALUES (?, 'streamlit', ?, ?)",
        (operation, details, now)
    )

def get_next_id(table, id_column):
    """Get the next available ID for a table"""
    result = run_query(f"SELECT MAX({id_column}) as max_id FROM {table}")
    max_id = result.iloc[0]['max_id']
    return 1 if max_id is None or pd.isna(max_id) else int(max_id) + 1

def append_to_csv(table_name, data_dict):
    """Append data to CSV file"""
    DATA_DIR = ROOT / 'data'
    csv_file = DATA_DIR / f"{table_name}_data.csv"
    
    try:
        # Read existing CSV
        if csv_file.exists():
            df = pd.read_csv(csv_file)
        else:
            # Create new DataFrame with columns from data_dict
            df = pd.DataFrame(columns=data_dict.keys())
        
        # Append new row
        new_row = pd.DataFrame([data_dict])
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Save back to CSV
        df.to_csv(csv_file, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving to CSV: {str(e)}")
        return False

def page_home():
    # Hero section
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 12px; margin-bottom: 2rem; color: white;'>
            <h1 style='color: white; border: none; font-size: 3rem; margin: 0;'>🍽️ Food Rescue Platform</h1>
            <p style='font-size: 1.2rem; margin-top: 1rem; opacity: 0.9;'>
                Connect surplus-food providers to receivers • Reduce waste • Fight hunger
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get KPIs from database
    providers_count = run_query("SELECT COUNT(*) as count FROM providers").iloc[0]['count']
    receivers_count = run_query("SELECT COUNT(*) as count FROM receivers").iloc[0]['count']
    listings_count = run_query("SELECT COUNT(*) as count FROM food_listings").iloc[0]['count']
    claims_count = run_query("SELECT COUNT(*) as count FROM claims").iloc[0]['count']
    completed_count = run_query("SELECT COUNT(*) as count FROM claims WHERE status='Completed'").iloc[0]['count']
    
    pct_completed = (completed_count / claims_count * 100) if claims_count > 0 else 0
    
    # KPI Cards with icons
    st.markdown("### 📊 Platform Statistics")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric('🏪 Providers', providers_count)
    k2.metric('🏥 Receivers', receivers_count)
    k3.metric('🍕 Listings', listings_count)
    k4.metric('📋 Claims', claims_count)
    k5.metric('✅ Completed', f"{pct_completed:.1f}%")
    
    st.markdown("---")
    
    # Charts in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Claims Status Distribution")
        claims_data = run_query("SELECT status, COUNT(*) as count FROM claims GROUP BY status")
        if not claims_data.empty:
            fig1 = px.pie(claims_data, names='status', values='count', 
                         color_discrete_sequence=['#667eea', '#4ECDC4', '#FF6B6B'],
                         hole=0.4)
            fig1.update_layout(
                showlegend=True,
                height=350,
                margin=dict(t=30, b=0, l=0, r=0)
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No claims data available yet")
    
    with col2:
        st.markdown("### 📊 Weekly Claims Trend")
        weekly_data = run_query("""
            SELECT strftime('%Y-W%W', timestamp) as week, COUNT(*) as claims 
            FROM claims 
            GROUP BY week 
            ORDER BY week
        """)
        if not weekly_data.empty:
            fig2 = px.area(weekly_data, x='week', y='claims',
                          color_discrete_sequence=['#667eea'])
            fig2.update_layout(
                showlegend=False,
                height=350,
                margin=dict(t=30, b=0, l=0, r=0),
                xaxis_title="Week",
                yaxis_title="Claims"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No weekly data available yet")
    
    # Listings table with filters
    st.markdown("---")
    st.markdown("### 🍕 Available Food Listings")
    
    listings_query = """
        SELECT f.*, p.city, p.name AS provider_name, p.contact AS provider_contact,
               COALESCE(SUM(c.claimed_quantity), 0) as total_claimed,
               (f.quantity - COALESCE(SUM(c.claimed_quantity), 0)) as available_quantity
        FROM food_listings f 
        JOIN providers p ON p.provider_id = f.provider_id
        LEFT JOIN claims c ON f.food_id = c.food_id AND c.status != 'Cancelled'
        GROUP BY f.food_id
        HAVING available_quantity > 0
    """
    listings = run_query(listings_query)
    
    if not listings.empty:
        cities = sorted(listings['city'].dropna().unique())
        food_types = sorted(listings['food_type'].dropna().unique())
        meal_types = sorted(listings['meal_type'].dropna().unique())
        
        st.markdown("**🔍 Filter Options:**")
        c1, c2, c3 = st.columns(3)
        with c1:
            f_city = st.multiselect('🌆 City', cities, key='home_city')
        with c2:
            f_food = st.multiselect('🥗 Food Type', food_types, key='home_food')
        with c3:
            f_meal = st.multiselect('🍽️ Meal Type', meal_types, key='home_meal')
        
        # Filter data
        df = listings.copy()
        if f_city:
            df = df[df['city'].isin(f_city)]
        if f_food:
            df = df[df['food_type'].isin(f_food)]
        if f_meal:
            df = df[df['meal_type'].isin(f_meal)]
        
        # Replace the original quantity column with available quantity for display
        df['Original_Quantity'] = df['quantity']
        df['quantity'] = df['available_quantity'].astype(int)
        
        # Select and reorder columns for better display
        display_columns = ['food_id', 'food_name', 'quantity', 'expiry_date', 
                          'provider_name', 'city', 'food_type', 'meal_type', 
                          'location', 'provider_contact']
        
        # Only include columns that exist
        display_columns = [col for col in display_columns if col in df.columns]
        df_display = df[display_columns].copy()
        
        # Highlight near expiry
        df_display['expiry_date'] = pd.to_datetime(df_display['expiry_date'])
        today = pd.Timestamp.now().normalize()
        
        def highlight(row):
            if row['expiry_date'] <= today + pd.Timedelta(days=3):
                return 'background-color: #ffd6d6'
            return ''
        
        st.info("ℹ️ **Quantity shown is the AVAILABLE quantity** (Original quantity - Claimed quantity)")
        st.dataframe(df_display.style.apply(lambda r: [highlight(r)] * len(r), axis=1), use_container_width=True)
    else:
        st.info('No food listings found')

def page_manage_listings():
    st.header('Manage Listings (CRUD)')
    
    providers = run_query("SELECT provider_id, name FROM providers ORDER BY name")
    listings = run_query("SELECT * FROM food_listings")
    
    with st.expander('Add Listing', expanded=False):
        if providers.empty:
            st.warning('⚠️ No providers found. Please add providers first in the "Providers & Receivers" page.')
        else:
            next_id = get_next_id('food_listings', 'food_id')
            with st.form('add_listing_form'):
                col1, col2 = st.columns([3, 1])
                with col1:
                    food_id = st.number_input('Food_ID', step=1, min_value=1, value=next_id)
                with col2:
                    st.info(f'Next: {next_id}')
                food_name = st.text_input('Food_Name')
                quantity = st.number_input('Quantity', step=1, min_value=0)
                expiry_date = st.date_input('Expiry_Date')
                provider_choice = st.selectbox('Provider', providers['name'].tolist())
                provider_id = int(providers.loc[providers['name'] == provider_choice, 'provider_id'].iloc[0])
                provider_type = st.text_input('Provider_Type')
                location = st.text_input('Location')
                food_type = st.text_input('Food_Type')
                meal_type = st.text_input('Meal_Type')
                submitted = st.form_submit_button('Create')
                if submitted:
                    # Validation
                    if not food_name or not food_name.strip():
                        st.error('❌ Food name is required!')
                    elif not provider_type or not provider_type.strip():
                        st.error('❌ Provider type is required!')
                    elif not location or not location.strip():
                        st.error('❌ Location is required!')
                    elif not food_type or not food_type.strip():
                        st.error('❌ Food type is required!')
                    elif not meal_type or not meal_type.strip():
                        st.error('❌ Meal type is required!')
                    else:
                        try:
                            execute_query('''
                                INSERT INTO food_listings(food_id, food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (food_id, food_name.strip(), quantity, str(expiry_date), provider_id, provider_type.strip(), location.strip(), food_type.strip(), meal_type.strip()))
                            log_audit('create_listing', f'food_id={food_id}')
                            st.success('✅ Listing created successfully!')
                            st.rerun()
                        except Exception as e:
                            if 'UNIQUE constraint failed' in str(e):
                                st.error(f'❌ Food ID {food_id} already exists! Please use a different ID.')
                            else:
                                st.error(f'❌ Error creating listing: {str(e)}')
    
    with st.expander('Edit Listing'):
        if not listings.empty:
            picked_id = st.selectbox('Select Food_ID', listings['food_id'].tolist())
            row = listings[listings['food_id'] == picked_id].iloc[0]
            with st.form('edit_listing_form'):
                food_name = st.text_input('Food_Name', row['food_name'])
                quantity = st.number_input('Quantity', step=1, min_value=0, value=int(row['quantity']) if not pd.isna(row['quantity']) else 0)
                expiry_date = st.date_input('Expiry_Date', pd.to_datetime(row['expiry_date']).date())
                provider_id = st.number_input('Provider_ID', step=1, value=int(row['provider_id']))
                provider_type = st.text_input('Provider_Type', row['provider_type'] or '')
                location = st.text_input('Location', row['location'] or '')
                food_type = st.text_input('Food_Type', row['food_type'] or '')
                meal_type = st.text_input('Meal_Type', row['meal_type'] or '')
                submitted = st.form_submit_button('Update')
                if submitted:
                    # Validation
                    if not food_name or not food_name.strip():
                        st.error('❌ Food name is required!')
                    elif not provider_type or not provider_type.strip():
                        st.error('❌ Provider type is required!')
                    elif not location or not location.strip():
                        st.error('❌ Location is required!')
                    elif not food_type or not food_type.strip():
                        st.error('❌ Food type is required!')
                    elif not meal_type or not meal_type.strip():
                        st.error('❌ Meal type is required!')
                    else:
                        try:
                            execute_query('''
                                UPDATE food_listings SET food_name=?, quantity=?, expiry_date=?, provider_id=?, provider_type=?, location=?, food_type=?, meal_type=? 
                                WHERE food_id=?
                            ''', (food_name.strip(), quantity, str(expiry_date), provider_id, provider_type.strip(), location.strip(), food_type.strip(), meal_type.strip(), picked_id))
                            log_audit('update_listing', f'food_id={picked_id}')
                            st.success('✅ Listing updated successfully!')
                            st.rerun()
                        except Exception as e:
                            st.error(f'❌ Error updating listing: {str(e)}')
        else:
            st.info('No listings to edit')
    
    with st.expander('Delete Listing'):
        if not listings.empty:
            del_id = st.selectbox('Select Food_ID to delete', listings['food_id'].tolist(), key='delete_listing_select')
            st.warning('⚠️ This action cannot be undone!')
            if st.button('Confirm Delete', type='primary'):
                try:
                    execute_query('DELETE FROM food_listings WHERE food_id=?', (del_id,))
                    log_audit('delete_listing', f'food_id={del_id}')
                    st.success('✅ Listing deleted successfully!')
                    st.rerun()
                except Exception as e:
                    st.error(f'❌ Error deleting listing: {str(e)}')
        else:
            st.info('No listings to delete')

def page_manage_claims():
    st.header('Manage Claims (CRUD)')
    
    # Get food listings with available quantities
    foods = run_query("""
        SELECT f.food_id, f.food_name, f.quantity, f.provider_id,
               COALESCE(SUM(c.claimed_quantity), 0) as total_claimed,
               (f.quantity - COALESCE(SUM(c.claimed_quantity), 0)) as available_quantity
        FROM food_listings f
        LEFT JOIN claims c ON f.food_id = c.food_id AND c.status != 'Cancelled'
        GROUP BY f.food_id
        HAVING available_quantity > 0
    """)
    receivers = run_query("SELECT receiver_id, name FROM receivers")
    claims = run_query("SELECT * FROM claims")
    
    with st.expander('Add Claim'):
        if foods.empty:
            st.warning('⚠️ No food listings found. Please add food listings first in the "Manage Listings" page.')
        elif receivers.empty:
            st.warning('⚠️ No receivers found. Please add receivers first in the "Providers & Receivers" page.')
        else:
            next_id = get_next_id('claims', 'claim_id')
            with st.form('add_claim_form'):
                col1, col2 = st.columns([3, 1])
                with col1:
                    claim_id = st.number_input('Claim_ID', step=1, min_value=1, value=next_id)
                with col2:
                    st.info(f'Next: {next_id}')
                
                # Create food options with IDs and available quantities
                food_options = {f"{row['food_id']} - {row['food_name']} (Available: {int(row['available_quantity'])})": row['food_id'] for _, row in foods.iterrows()}
                food_choice = st.selectbox('Food ID - Food Name (Available Quantity)', list(food_options.keys()))
                selected_food_id = food_options[food_choice]
                
                # Get available quantity for selected food
                selected_food = foods[foods['food_id'] == selected_food_id].iloc[0]
                max_quantity = int(selected_food['available_quantity'])
                
                # Quantity selector
                claimed_quantity = st.number_input(
                    f'Quantity to Claim (Max: {max_quantity})', 
                    min_value=1, 
                    max_value=max_quantity, 
                    value=min(1, max_quantity),
                    step=1
                )
                
                # Create receiver options with IDs
                receiver_options = {f"{row['receiver_id']} - {row['name']}": row['receiver_id'] for _, row in receivers.iterrows()}
                recv_choice = st.selectbox('Receiver', list(receiver_options.keys()))
                selected_receiver_id = receiver_options[recv_choice]
                
                status = st.selectbox('Status', ['Pending', 'Completed', 'Cancelled'], index=0)
                submitted = st.form_submit_button('Create Claim')
                
                if submitted:
                    try:
                        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        execute_query('''
                            INSERT INTO claims(claim_id, food_id, receiver_id, claimed_quantity, status, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (claim_id, selected_food_id, selected_receiver_id, claimed_quantity, status, ts))
                        log_audit('create_claim', f'claim_id={claim_id}, food_id={selected_food_id}, receiver_id={selected_receiver_id}, quantity={claimed_quantity}')
                        st.success(f'✅ Claim created successfully! Food ID: {selected_food_id}, Receiver ID: {selected_receiver_id}, Quantity: {claimed_quantity}')
                        st.rerun()
                    except Exception as e:
                        if 'UNIQUE constraint failed' in str(e):
                            st.error(f'❌ Claim ID {claim_id} already exists! Please use a different ID.')
                        elif 'FOREIGN KEY constraint failed' in str(e):
                            st.error(f'❌ Invalid Food ID ({selected_food_id}) or Receiver ID ({selected_receiver_id}). Please check your selection.')
                        else:
                            st.error(f'❌ Error creating claim: {str(e)}')
    
    with st.expander('Update Claim Status'):
        if not claims.empty:
            pick = st.selectbox('Select Claim', claims.apply(lambda r: f"{r['claim_id']} - {r['status']}", axis=1).tolist())
            claim_id = int(pick.split(' - ')[0])
            new_status = st.selectbox('New Status', ['Pending', 'Completed', 'Cancelled'])
            if st.button('Update Status'):
                try:
                    execute_query('UPDATE claims SET status=? WHERE claim_id=?', (new_status, claim_id))
                    log_audit('update_claim', f'claim_id={claim_id}, status={new_status}')
                    st.success('✅ Status updated successfully!')
                    st.rerun()
                except Exception as e:
                    st.error(f'❌ Error updating claim status: {str(e)}')
        else:
            st.info('No claims to update')
    
    st.subheader('View Claims')
    st.dataframe(claims, use_container_width=True)

def page_providers_receivers():
    st.header('Providers & Receivers')
    tab1, tab2 = st.tabs(['Providers', 'Receivers'])
    
    providers = run_query("SELECT * FROM providers")
    receivers = run_query("SELECT * FROM receivers")
    
    with tab1:
        st.dataframe(providers, use_container_width=True)
        
        if not providers.empty:
            st.download_button('Export provider contact CSV', data=providers[['name','city','contact']].to_csv(index=False), file_name='providers_contacts.csv', mime='text/csv')
        
        with st.expander('Add / Edit / Delete Provider'):
            next_provider_id = get_next_id('providers', 'provider_id')
            with st.form('provider_form'):
                mode = st.selectbox('Action', ['Add','Edit','Delete'])
                col1, col2 = st.columns([3, 1])
                with col1:
                    provider_id = st.number_input('Provider_ID', step=1, value=next_provider_id if mode == 'Add' else 1)
                with col2:
                    if mode == 'Add':
                        st.info(f'Next: {next_provider_id}')
                name = st.text_input('Name')
                type_ = st.text_input('Type')
                address = st.text_input('Address')
                city = st.text_input('City')
                contact = st.text_input('Contact')
                submitted = st.form_submit_button('Submit')
                if submitted:
                    try:
                        if mode == 'Add':
                            if not name or not name.strip():
                                st.error('❌ Provider name is required!')
                            elif not contact or not contact.strip():
                                st.error('❌ Contact is required!')
                            else:
                                try:
                                    execute_query('''
                                        INSERT INTO providers(provider_id,name,type,address,city,contact)
                                        VALUES (?, ?, ?, ?, ?, ?)
                                    ''', (provider_id, name.strip(), type_.strip() if type_ else '', address.strip() if address else '', city.strip() if city else '', contact.strip()))
                                    log_audit('create_provider', f'provider_id={provider_id}')
                                    st.success('✅ Provider added successfully!')
                                    st.rerun()
                                except Exception as add_error:
                                    if 'UNIQUE constraint failed' in str(add_error):
                                        st.error(f'❌ Provider ID {provider_id} already exists! Please use a different ID.')
                                    else:
                                        raise add_error
                        elif mode == 'Edit':
                            if not name or not name.strip():
                                st.error('❌ Provider name is required!')
                            elif not contact or not contact.strip():
                                st.error('❌ Contact is required!')
                            else:
                                execute_query('''
                                    UPDATE providers SET name=?, type=?, address=?, city=?, contact=?
                                    WHERE provider_id=?
                                ''', (name.strip(), type_.strip() if type_ else '', address.strip() if address else '', city.strip() if city else '', contact.strip(), provider_id))
                                log_audit('update_provider', f'provider_id={provider_id}')
                                st.success('✅ Provider updated successfully!')
                                st.rerun()
                        else:
                            execute_query('DELETE FROM providers WHERE provider_id=?', (provider_id,))
                            log_audit('delete_provider', f'provider_id={provider_id}')
                            st.success('✅ Provider deleted successfully!')
                            st.rerun()
                    except Exception as e:
                        st.error(f'❌ Error: {str(e)}')
    
    with tab2:
        st.dataframe(receivers, use_container_width=True)
        with st.expander('Add / Edit / Delete Receiver'):
            next_receiver_id = get_next_id('receivers', 'receiver_id')
            with st.form('receiver_form'):
                mode = st.selectbox('Action', ['Add','Edit','Delete'])
                col1, col2 = st.columns([3, 1])
                with col1:
                    receiver_id = st.number_input('Receiver_ID', step=1, value=next_receiver_id if mode == 'Add' else 1)
                with col2:
                    if mode == 'Add':
                        st.info(f'Next: {next_receiver_id}')
                name = st.text_input('Name', key='r_name')
                type_ = st.text_input('Type', key='r_type')
                city = st.text_input('City', key='r_city')
                contact = st.text_input('Contact', key='r_contact')
                submitted = st.form_submit_button('Submit', type='primary')
                if submitted:
                    try:
                        if mode == 'Add':
                            if not name or not name.strip():
                                st.error('❌ Receiver name is required!')
                            elif not contact or not contact.strip():
                                st.error('❌ Contact is required!')
                            else:
                                try:
                                    execute_query('''
                                        INSERT INTO receivers(receiver_id,name,type,city,contact)
                                        VALUES (?, ?, ?, ?, ?)
                                    ''', (receiver_id, name.strip(), type_.strip() if type_ else '', city.strip() if city else '', contact.strip()))
                                    log_audit('create_receiver', f'receiver_id={receiver_id}')
                                    st.success('✅ Receiver added successfully!')
                                    st.rerun()
                                except Exception as add_error:
                                    if 'UNIQUE constraint failed' in str(add_error):
                                        st.error(f'❌ Receiver ID {receiver_id} already exists! Please use a different ID.')
                                    else:
                                        raise add_error
                        elif mode == 'Edit':
                            if not name or not name.strip():
                                st.error('❌ Receiver name is required!')
                            elif not contact or not contact.strip():
                                st.error('❌ Contact is required!')
                            else:
                                execute_query('''
                                    UPDATE receivers SET name=?, type=?, city=?, contact=?
                                    WHERE receiver_id=?
                                ''', (name.strip(), type_.strip() if type_ else '', city.strip() if city else '', contact.strip(), receiver_id))
                                log_audit('update_receiver', f'receiver_id={receiver_id}')
                                st.success('✅ Receiver updated successfully!')
                                st.rerun()
                        else:
                            execute_query('DELETE FROM receivers WHERE receiver_id=?', (receiver_id,))
                            log_audit('delete_receiver', f'receiver_id={receiver_id}')
                            st.success('✅ Receiver deleted successfully!')
                            st.rerun()
                    except Exception as e:
                        st.error(f'❌ Error: {str(e)}')

def page_sql_queries():
    st.header('SQL Queries & Analysis (Required)')
    
    queries = {
        'Providers and receivers per city': '''
            SELECT city, 
                   SUM(CASE WHEN src='provider' THEN cnt ELSE 0 END) AS providers,
                   SUM(CASE WHEN src='receiver' THEN cnt ELSE 0 END) AS receivers
            FROM (
                SELECT city, COUNT(*) AS cnt, 'provider' AS src FROM providers GROUP BY city
                UNION ALL
                SELECT city, COUNT(*) AS cnt, 'receiver' AS src FROM receivers GROUP BY city
            ) t
            GROUP BY city
            ORDER BY city
        ''',
        'Top provider type': '''
            SELECT provider_type, COUNT(*) AS listings_count
            FROM food_listings
            GROUP BY provider_type
            ORDER BY listings_count DESC
            LIMIT 1
        ''',
        'Provider contacts in city': '''
            SELECT name, contact FROM providers WHERE city = ?
            ORDER BY name
        ''',
        'Top receivers by claims': '''
            SELECT r.receiver_id, r.name, COUNT(*) AS claims_count
            FROM claims c
            JOIN receivers r ON r.receiver_id = c.receiver_id
            GROUP BY r.receiver_id, r.name
            ORDER BY claims_count DESC
        ''',
        'Total quantity available': '''
            SELECT SUM(quantity) AS total_quantity FROM food_listings
        ''',
        'City with most listings': '''
            SELECT p.city, COUNT(*) AS listings_count
            FROM food_listings f
            JOIN providers p ON p.provider_id = f.provider_id
            GROUP BY p.city
            ORDER BY listings_count DESC
            LIMIT 1
        ''',
        'Most common food types': '''
            SELECT food_type, COUNT(*) AS cnt
            FROM food_listings
            GROUP BY food_type
            ORDER BY cnt DESC
            LIMIT 5
        ''',
        'Claims per food item': '''
            SELECT f.food_id, f.food_name, COUNT(c.claim_id) AS claims_count
            FROM food_listings f
            LEFT JOIN claims c ON c.food_id = f.food_id
            GROUP BY f.food_id, f.food_name
            ORDER BY claims_count DESC
        ''',
        'Claims status distribution': '''
            SELECT status, COUNT(*) AS cnt,
                   ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM claims), 2) AS pct
            FROM claims
            GROUP BY status
        ''',
        'Food listings near expiry (<=3 days)': '''
            SELECT *
            FROM food_listings
            WHERE expiry_date <= date('now','+3 day')
            ORDER BY expiry_date ASC
        ''',
        'Claims per week (time-series)': '''
            SELECT strftime('%Y-W%W', timestamp) AS iso_week, COUNT(*) AS claims
            FROM claims
            GROUP BY iso_week
            ORDER BY iso_week
        '''
    }
    
    for label, sql in queries.items():
        st.subheader(label)
        with st.expander('SQL', expanded=False):
            st.code(sql, language='sql')
        
        params = {}
        if label == 'Provider contacts in city':
            cities = run_query("SELECT DISTINCT city FROM providers WHERE city IS NOT NULL")['city'].dropna().tolist()
            if cities:
                city = st.selectbox('City', cities, key=f'city_{label}')
                params = (city,)
        
        if st.button(f'Run: {label}'):
            try:
                df = run_query(sql, params)
                st.dataframe(df, use_container_width=True)
                st.download_button('Export result CSV', data=df.to_csv(index=False), file_name=f'{label.replace(" ","_")}.csv', mime='text/csv')
            except Exception as e:
                st.error(f'Error running query: {str(e)}')

def page_eda():
    st.header('EDA / Insights')
    
    # City trends
    city_counts = run_query('''
        SELECT p.city, COUNT(*) as listings
        FROM food_listings f 
        JOIN providers p ON p.provider_id = f.provider_id
        GROUP BY p.city
    ''')
    if not city_counts.empty:
        st.plotly_chart(px.bar(city_counts, x='city', y='listings', title='Listings by City'), use_container_width=True)
    
    # Meal type demand
    meal_counts = run_query('''
        SELECT meal_type, COUNT(*) as count
        FROM food_listings 
        GROUP BY meal_type 
        ORDER BY count DESC
    ''')
    if not meal_counts.empty:
        st.plotly_chart(px.bar(meal_counts, x='meal_type', y='count', title='Listings by Meal Type'), use_container_width=True)
    
    # Expiry risk
    near = run_query('''
        SELECT *
        FROM food_listings
        WHERE expiry_date <= date('now','+3 day')
        ORDER BY expiry_date ASC
    ''')
    st.write('Listings near expiry (<=3 days):')
    if not near.empty:
        st.dataframe(near, use_container_width=True)
    else:
        st.info('No listings near expiry')

def page_user_registration():
    # Hero section
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%); 
                    border-radius: 12px; margin-bottom: 2rem; color: white;'>
            <h1 style='color: white; border: none; font-size: 2.5rem; margin: 0;'>🆕 Join Our Platform</h1>
            <p style='font-size: 1.1rem; margin-top: 1rem; opacity: 0.9;'>
                Register as a Provider or Receiver to start making a difference
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Role selection with better styling
    st.markdown("### 👤 Select Your Role")
    role = st.radio('', ['🏪 Provider (Donate Food)', '🏥 Receiver (Receive Food)'], horizontal=True, label_visibility='collapsed')
    
    # Extract role
    role = 'Provider' if 'Provider' in role else 'Receiver'
    
    st.markdown('---')
    
    if role == 'Provider':
        st.subheader('📦 Provider Registration')
        st.write('Register your business to donate surplus food')
        
        next_id = get_next_id('providers', 'provider_id')
        
        with st.form('provider_registration_form'):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f'Your Provider ID will be: **{next_id}**')
            
            name = st.text_input('Business Name *', placeholder='e.g., ABC Restaurant')
            type_ = st.selectbox('Business Type *', [
                'Restaurant', 
                'Cafe', 
                'Grocery Store', 
                'Supermarket', 
                'Bakery', 
                'Hotel', 
                'Catering Service',
                'Other'
            ])
            address = st.text_area('Full Address *', placeholder='Street, Building, Floor')
            city = st.text_input('City *', placeholder='e.g., New York')
            contact = st.text_input('Contact Number *', placeholder='e.g., +1-555-1234')
            
            st.markdown('**Required fields are marked with** *')
            submitted = st.form_submit_button('✅ Register as Provider', type='primary')
            
            if submitted:
                # Validation
                if not name or not name.strip():
                    st.error('❌ Business name is required!')
                elif not address or not address.strip():
                    st.error('❌ Address is required!')
                elif not city or not city.strip():
                    st.error('❌ City is required!')
                elif not contact or not contact.strip():
                    st.error('❌ Contact number is required!')
                else:
                    try:
                        # Prepare data
                        provider_data = {
                            'Provider_ID': next_id,
                            'Name': name.strip(),
                            'Type': type_,
                            'Address': address.strip(),
                            'City': city.strip(),
                            'Contact': contact.strip()
                        }
                        
                        # Add to database
                        execute_query('''
                            INSERT INTO providers(provider_id, name, type, address, city, contact)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (next_id, name.strip(), type_, address.strip(), city.strip(), contact.strip()))
                        
                        # Append to CSV
                        if append_to_csv('providers', provider_data):
                            log_audit('register_provider', f'provider_id={next_id}, name={name}')
                            st.success(f'✅ Registration successful! Your Provider ID is: **{next_id}**')
                            st.balloons()
                            st.info('You can now add food listings in the "Manage Listings" page.')
                        else:
                            st.warning('⚠️ Registered in database but failed to save to CSV.')
                        
                    except Exception as e:
                        if 'UNIQUE constraint failed' in str(e):
                            st.error(f'❌ Provider ID {next_id} already exists! Please refresh and try again.')
                        else:
                            st.error(f'❌ Registration failed: {str(e)}')
    
    else:  # Receiver
        st.subheader('🏥 Receiver Registration')
        st.write('Register your organization to receive surplus food')
        
        next_id = get_next_id('receivers', 'receiver_id')
        
        with st.form('receiver_registration_form'):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f'Your Receiver ID will be: **{next_id}**')
            
            name = st.text_input('Name *', placeholder='e.g., Community Food Bank or John Doe')
            type_ = st.selectbox('Type *', [
                'Individual',
                'Food Bank',
                'Shelter',
                'Community Center',
                'Church',
                'School',
                'NGO',
                'Charity',
                'Other'
            ])
            city = st.text_input('City *', placeholder='e.g., New York')
            contact = st.text_input('Contact Number *', placeholder='e.g., +1-555-1234')
            
            st.markdown('**Required fields are marked with** *')
            submitted = st.form_submit_button('✅ Register as Receiver', type='primary')
            
            if submitted:
                # Validation
                if not name or not name.strip():
                    st.error('❌ Organization name is required!')
                elif not city or not city.strip():
                    st.error('❌ City is required!')
                elif not contact or not contact.strip():
                    st.error('❌ Contact number is required!')
                else:
                    try:
                        # Prepare data
                        receiver_data = {
                            'Receiver_ID': next_id,
                            'Name': name.strip(),
                            'Type': type_,
                            'City': city.strip(),
                            'Contact': contact.strip()
                        }
                        
                        # Add to database
                        execute_query('''
                            INSERT INTO receivers(receiver_id, name, type, city, contact)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (next_id, name.strip(), type_, city.strip(), contact.strip()))
                        
                        # Append to CSV
                        if append_to_csv('receivers', receiver_data):
                            log_audit('register_receiver', f'receiver_id={next_id}, name={name}')
                            st.success(f'✅ Registration successful! Your Receiver ID is: **{next_id}**')
                            st.balloons()
                            st.info('You can now claim food items in the "Manage Claims" page.')
                        else:
                            st.warning('⚠️ Registered in database but failed to save to CSV.')
                        
                    except Exception as e:
                        if 'UNIQUE constraint failed' in str(e):
                            st.error(f'❌ Receiver ID {next_id} already exists! Please refresh and try again.')
                        else:
                            st.error(f'❌ Registration failed: {str(e)}')

def page_admin():
    st.header('Admin / Deploy')
    
    # CSV Import Section
    st.subheader('📁 CSV Data Import')
    if st.button('🔄 Re-import CSV Data'):
        if import_csv_data():
            st.success('✅ CSV data re-imported successfully!')
            st.rerun()
    
    # Get counts
    counts = {}
    for table in ['providers', 'receivers', 'food_listings', 'claims', 'audit_log']:
        count = run_query(f"SELECT COUNT(*) as count FROM {table}").iloc[0]['count']
        counts[table] = count
    
    st.write('📊 Row counts:', counts)
    
    if st.button('💾 Backup DB to CSV (tables)'):
        for table in ['providers', 'receivers', 'food_listings', 'claims']:
            df = run_query(f"SELECT * FROM {table}")
            if not df.empty:
                st.download_button(f'📥 Download {table}.csv', data=df.to_csv(index=False), file_name=f'{table}.csv', mime='text/csv')
    
    if st.button('📄 Export SQL dump'):
        # Get schema
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        schema = cursor.fetchall()
        conn.close()
        
        schema_text = '\n'.join([row[0] for row in schema if row[0]])
        st.download_button('📥 Download schema.sql', data=schema_text, file_name='schema.sql', mime='text/plain')
    
    st.success('✅ SQLite database is working! All operations are real and persistent.')

def main():
    # Initialize database on first run
    init_database()
    
    # Migrate database if needed (add new columns to existing database)
    migrate_database()
    
    # Sidebar with logo and navigation
    st.sidebar.markdown("""
        <div style='text-align: center; padding: 1rem 0; margin-bottom: 1rem;'>
            <h1 style='color: white; font-size: 2rem; margin: 0;'>🍽️</h1>
            <h3 style='color: white; margin: 0.5rem 0 0 0;'>Food Rescue</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio('📍 Navigation', [
        '🆕 User Registration',
        '🏠 Home / Dashboard',
        '📝 Manage Listings',
        '📋 Manage Claims',
        '👥 Providers & Receivers',
        '📊 SQL Queries & Analysis',
        '📈 EDA / Insights',
        '⚙️ Admin / Deploy'
    ], label_visibility='visible')
    
    if '🆕' in page or 'User Registration' in page:
        page_user_registration()
    elif '🏠' in page or 'Home' in page or 'Dashboard' in page:
        page_home()
    elif '📝' in page or 'Manage Listings' in page:
        page_manage_listings()
    elif '📋' in page or 'Manage Claims' in page:
        page_manage_claims()
    elif '👥' in page or 'Providers' in page or 'Receivers' in page:
        page_providers_receivers()
    elif '📊' in page or 'SQL Queries' in page:
        page_sql_queries()
    elif '📈' in page or 'EDA' in page or 'Insights' in page:
        page_eda()
    else:
        page_admin()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
        <div style='text-align: center; color: white; opacity: 0.7; font-size: 0.8rem;'>
            <p>Made with ❤️ for reducing food waste</p>
            <p>© 2025 Food Rescue Platform</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()