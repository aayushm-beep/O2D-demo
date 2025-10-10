#!/usr/bin/env python3
"""
Database Migration Script - Old Schema to New Enhanced Schema (150+ columns)
Migrates data from old order_dispatch_db to new enhanced schema
"""

import pymysql
from datetime import datetime
import sys
import os

# Database Configuration
OLD_DB = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',  # Change this to your password
    'database': 'order_dispatch_db',
    'charset': 'utf8mb4'
}

NEW_DB = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',  # Change this to your password
    'database': 'order_dispatch_db_new',
    'charset': 'utf8mb4'
}

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70)

def print_step(text):
    """Print step information"""
    print(f"\n{text}")

def create_new_database():
    """Create new database with enhanced schema"""
    print_step("Step 1: Creating new database...")
    
    try:
        # Connect without database selection
        conn = pymysql.connect(
            host=NEW_DB['host'],
            port=NEW_DB['port'],
            user=NEW_DB['user'],
            password=NEW_DB['password'],
            charset=NEW_DB['charset']
        )
        cursor = conn.cursor()
        
        # Drop if exists and create new
        cursor.execute(f"DROP DATABASE IF EXISTS {NEW_DB['database']}")
        cursor.execute(f"CREATE DATABASE {NEW_DB['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        print(f"  ✓ Database '{NEW_DB['database']}' created successfully")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Now execute schema
        if os.path.exists('create_database.sql'):
            print_step("Step 2: Creating tables from SQL file...")
            conn = pymysql.connect(**NEW_DB)
            cursor = conn.cursor()
            
            with open('create_database.sql', 'r', encoding='utf8') as f:
                sql_content = f.read()
                # Split by semicolon but handle complex statements
                statements = sql_content.split(';')
                
                for statement in statements:
                    statement = statement.strip()
                    if statement and not statement.startswith('--'):
                        try:
                            cursor.execute(statement)
                        except Exception as e:
                            if 'CREATE DATABASE' not in statement and 'USE ' not in statement:
                                print(f"  Warning: {str(e)[:100]}")
            
            conn.commit()
            cursor.close()
            conn.close()
            print("  ✓ Tables created successfully")
        else:
            print("  ✗ create_database.sql not found. Please ensure it exists in the current directory.")
            sys.exit(1)
            
    except Exception as e:
        print(f"  ✗ Error creating database: {e}")
        sys.exit(1)

def migrate_users():
    """Migrate users table"""
    print_step("Step 3: Migrating users...")
    
    try:
        old_conn = pymysql.connect(**OLD_DB)
        new_conn = pymysql.connect(**NEW_DB)
        
        old_cursor = old_conn.cursor(pymysql.cursors.DictCursor)
        new_cursor = new_conn.cursor()
        
        # Get all users
        old_cursor.execute("SELECT * FROM users")
        users = old_cursor.fetchall()
        
        if not users:
            print("  ℹ No users to migrate")
            old_cursor.close()
            new_cursor.close()
            old_conn.close()
            new_conn.close()
            return
        
        # Insert into new database
        for user in users:
            new_cursor.execute("""
                INSERT INTO users (id, username, password, email, role, full_name, phone, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user.get('id'),
                user.get('username'),
                user.get('password'),
                user.get('email'),
                user.get('role', 'user'),
                user.get('full_name'),
                user.get('phone'),
                user.get('is_active', True),
                user.get('created_at', datetime.now())
            ))
        
        new_conn.commit()
        old_cursor.close()
        new_cursor.close()
        old_conn.close()
        new_conn.close()
        
        print(f"  ✓ Migrated {len(users)} users")
        
    except Exception as e:
        print(f"  ✗ Error migrating users: {e}")

def migrate_customers():
    """Migrate customers table"""
    print_step("Step 4: Migrating customers...")
    
    try:
        old_conn = pymysql.connect(**OLD_DB)
        new_conn = pymysql.connect(**NEW_DB)
        
        old_cursor = old_conn.cursor(pymysql.cursors.DictCursor)
        new_cursor = new_conn.cursor()
        
        old_cursor.execute("SELECT * FROM customers")
        customers = old_cursor.fetchall()
        
        if not customers:
            print("  ℹ No customers to migrate")
            old_cursor.close()
            new_cursor.close()
            old_conn.close()
            new_conn.close()
            return
        
        for customer in customers:
            new_cursor.execute("""
                INSERT INTO customers (
                    id, customer_id, name, email, phone, company, 
                    address_line1, address_line2, city, state, zipcode, country,
                    customer_type, credit_limit, outstanding_balance, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                customer.get('id'),
                customer.get('customer_id'),
                customer.get('name'),
                customer.get('email'),
                customer.get('phone'),
                customer.get('company'),
                customer.get('address_line1'),
                customer.get('address_line2'),
                customer.get('city'),
                customer.get('state'),
                customer.get('zipcode'),
                customer.get('country', 'USA'),
                customer.get('customer_type', 'retail'),
                customer.get('credit_limit', 0),
                customer.get('outstanding_balance', 0),
                customer.get('created_at', datetime.now())
            ))
        
        new_conn.commit()
        old_cursor.close()
        new_cursor.close()
        old_conn.close()
        new_conn.close()
        
        print(f"  ✓ Migrated {len(customers)} customers")
        
    except Exception as e:
        print(f"  ✗ Error migrating customers: {e}")

def migrate_products():
    """Migrate products table"""
    print_step("Step 5: Migrating products...")
    
    try:
        old_conn = pymysql.connect(**OLD_DB)
        new_conn = pymysql.connect(**NEW_DB)
        
        old_cursor = old_conn.cursor(pymysql.cursors.DictCursor)
        new_cursor = new_conn.cursor()
        
        old_cursor.execute("SELECT * FROM products")
        products = old_cursor.fetchall()
        
        if not products:
            print("  ℹ No products to migrate")
            old_cursor.close()
            new_cursor.close()
            old_conn.close()
            new_conn.close()
            return
        
        for product in products:
            new_cursor.execute("""
                INSERT INTO products (
                    id, product_id, name, category, brand, sku, description,
                    unit_price, cost_price, stock_quantity, reorder_level,
                    supplier_id, warehouse_location, is_active, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                product.get('id'),
                product.get('product_id'),
                product.get('name'),
                product.get('category'),
                product.get('brand'),
                product.get('sku'),
                product.get('description'),
                product.get('unit_price', 0),
                product.get('cost_price', 0),
                product.get('stock_quantity', 0),
                product.get('reorder_level', 10),
                product.get('supplier_id'),
                product.get('warehouse_location'),
                product.get('is_active', True),
                product.get('created_at', datetime.now())
            ))
        
        new_conn.commit()
        old_cursor.close()
        new_cursor.close()
        old_conn.close()
        new_conn.close()
        
        print(f"  ✓ Migrated {len(products)} products")
        
    except Exception as e:
        print(f"  ✗ Error migrating products: {e}")

def migrate_warehouses():
    """Migrate warehouses table"""
    print_step("Step 6: Migrating warehouses...")
    
    try:
        old_conn = pymysql.connect(**OLD_DB)
        new_conn = pymysql.connect(**NEW_DB)
        
        old_cursor = old_conn.cursor(pymysql.cursors.DictCursor)
        new_cursor = new_conn.cursor()
        
        old_cursor.execute("SELECT * FROM warehouses")
        warehouses = old_cursor.fetchall()
        
        if not warehouses:
            print("  ℹ No warehouses to migrate")
            old_cursor.close()
            new_cursor.close()
            old_conn.close()
            new_conn.close()
            return
        
        for warehouse in warehouses:
            new_cursor.execute("""
                INSERT INTO warehouses (
                    id, warehouse_id, name, location, city, state,
                    manager_name, capacity, current_stock, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                warehouse.get('id'),
                warehouse.get('warehouse_id'),
                warehouse.get('name'),
                warehouse.get('location'),
                warehouse.get('city'),
                warehouse.get('state'),
                warehouse.get('manager_name'),
                warehouse.get('capacity', 0),
                warehouse.get('current_stock', 0),
                warehouse.get('is_active', True)
            ))
        
        new_conn.commit()
        old_cursor.close()
        new_cursor.close()
        old_conn.close()
        new_conn.close()
        
        print(f"  ✓ Migrated {len(warehouses)} warehouses")
        
    except Exception as e:
        print(f"  ✗ Error migrating warehouses: {e}")

def migrate_orders():
    """Migrate orders table - Map old columns to new 150+ columns"""
    print_step("Step 7: Migrating orders (this may take a while)...")
    
    try:
        old_conn = pymysql.connect(**OLD_DB)
        new_conn = pymysql.connect(**NEW_DB)
        
        old_cursor = old_conn.cursor(pymysql.cursors.DictCursor)
        new_cursor = new_conn.cursor()
        
        # Get total count
        old_cursor.execute("SELECT COUNT(*) as count FROM orders")
        total = old_cursor.fetchone()['count']
        
        if total == 0:
            print("  ℹ No orders to migrate")
            old_cursor.close()
            new_cursor.close()
            old_conn.close()
            new_conn.close()
            return
            
        print(f"  Total orders to migrate: {total:,}")
        
        # Migrate in batches
        batch_size = 500
        offset = 0
        
        while offset < total:
            old_cursor.execute(f"SELECT * FROM orders LIMIT {batch_size} OFFSET {offset}")
            orders = old_cursor.fetchall()
            
            for order in orders:
                # Map old columns to new columns (existing columns + NULL for new ones)
                new_cursor.execute("""
                    INSERT INTO orders (
                        order_id, customer_id, customer_name, customer_email, customer_phone,
                        order_date, order_time, order_status, priority_level, order_type,
                        sales_channel, product_id, product_name, product_category, brand,
                        quantity, unit_price, subtotal, discount_percent, discount_amount,
                        tax_rate, tax_amount, shipping_cost, total_amount, currency,
                        payment_method, payment_status, 
                        shipping_address_line1, shipping_city, shipping_state, 
                        shipping_zipcode, shipping_country,
                        carrier, tracking_number, shipping_method, delivery_date,
                        warehouse_id, dispatch_date, dispatch_status,
                        driver_name, vehicle_id,
                        created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s
                    )
                """, (
                    order.get('order_id'),
                    order.get('customer_id'),
                    order.get('customer_name'),
                    order.get('customer_email'),
                    order.get('customer_phone'),
                    order.get('order_date'),
                    order.get('order_time'),
                    order.get('order_status', 'Pending'),
                    order.get('priority_level', 'Medium'),
                    order.get('order_type'),
                    order.get('sales_channel'),
                    order.get('product_id'),
                    order.get('product_name'),
                    order.get('product_category'),
                    order.get('brand'),
                    order.get('quantity', 1),
                    order.get('unit_price', 0),
                    order.get('total_price', 0),
                    order.get('discount_percent', 0),
                    order.get('discount_amount', 0),
                    order.get('tax_rate', 0),
                    order.get('tax_amount', 0),
                    order.get('shipping_cost', 0),
                    order.get('total_amount', 0),
                    order.get('currency', 'USD'),
                    order.get('payment_method'),
                    order.get('payment_status'),
                    order.get('shipping_address_line1'),
                    order.get('shipping_city'),
                    order.get('shipping_state'),
                    order.get('shipping_zipcode'),
                    order.get('shipping_country', 'USA'),
                    order.get('carrier'),
                    order.get('tracking_number'),
                    order.get('shipping_method'),
                    order.get('delivery_date'),
                    order.get('warehouse_id'),
                    order.get('dispatch_date'),
                    order.get('dispatch_status'),
                    order.get('driver_name'),
                    order.get('vehicle_id'),
                    order.get('created_at', datetime.now()),
                    order.get('updated_at', datetime.now())
                ))
            
            new_conn.commit()
            offset += batch_size
            progress = min(offset, total)
            percentage = (progress / total) * 100
            print(f"  Progress: {progress:,}/{total:,} ({percentage:.1f}%)")
        
        old_cursor.close()
        new_cursor.close()
        old_conn.close()
        new_conn.close()
        
        print(f"  ✓ Migrated {total:,} orders successfully")
        
    except Exception as e:
        print(f"  ✗ Error migrating orders: {e}")
        import traceback
        traceback.print_exc()

def verify_migration():
    """Verify migration was successful"""
    print_step("Step 8: Verifying migration...")
    
    try:
        new_conn = pymysql.connect(**NEW_DB)
        cursor = new_conn.cursor()
        
        tables = ['users', 'customers', 'products', 'warehouses', 'orders']
        
        print("\n  Migration Summary:")
        print("  " + "-"*50)
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table.capitalize():15} : {count:,} records")
        
        print("  " + "-"*50)
        
        cursor.close()
        new_conn.close()
        
    except Exception as e:
        print(f"  ✗ Error during verification: {e}")

def main():
    """Main migration process"""
    print_header("DATABASE MIGRATION TOOL")
    print("  Old Database: " + OLD_DB['database'])
    print("  New Database: " + NEW_DB['database'])
    print("\n  This will migrate all data to the new enhanced schema (150+ columns)")
    
    response = input("\n  Continue? (yes/no): ").lower()
    if response != 'yes':
        print("\n  Migration cancelled.")
        sys.exit(0)
    
    try:
        # Execute migration steps
        create_new_database()
        migrate_users()
        migrate_customers()
        migrate_products()
        migrate_warehouses()
        migrate_orders()
        verify_migration()
        
        print_header("MIGRATION COMPLETED SUCCESSFULLY!")
        print("\n  Next Steps:")
        print("  1. Update config.py:")
        print(f"     DB_NAME = '{NEW_DB['database']}'")
        print("\n  2. Test the application:")
        print("     python app.py")
        print("\n  3. After verification, you can rename databases:")
        print(f"     mv {OLD_DB['database']} -> {OLD_DB['database']}_backup")
        print(f"     mv {NEW_DB['database']} -> {OLD_DB['database']}")
        print("\n  4. Or keep both databases for safety")
        
    except Exception as e:
        print_header("MIGRATION FAILED")
        print(f"\n  Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()