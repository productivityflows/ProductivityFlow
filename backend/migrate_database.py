#!/usr/bin/env python3
"""
Database migration script to fix schema issues
"""
import os
import sys
import psycopg2
from urllib.parse import urlparse

def migrate_database():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable is not set!")
        return False
    
    # Handle Render's postgres:// vs postgresql:// format
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    try:
        # Parse the database URL
        parsed = urlparse(DATABASE_URL)
        
        # Connect to the database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password
        )
        
        cursor = conn.cursor()
        
        print("🔍 Checking current database schema...")
        
        # Check if teams table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'teams'
            );
        """)
        
        teams_exists = cursor.fetchone()[0]
        
        if not teams_exists:
            print("❌ Teams table doesn't exist. Need to create all tables first.")
            return False
        
        # Check teams table structure
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'teams'
            ORDER BY ordinal_position;
        """)
        
        columns = [row[0] for row in cursor.fetchall()]
        print(f"📋 Current teams table columns: {columns}")
        
        migrations_performed = []
        
        # Migration 1: Add employee_code column if it doesn't exist
        if 'employee_code' not in columns:
            print("🔧 Adding employee_code column to teams table...")
            
            if 'code' in columns:
                # Rename existing 'code' column to 'employee_code'
                print("  └─ Renaming 'code' column to 'employee_code'...")
                cursor.execute("ALTER TABLE teams RENAME COLUMN code TO employee_code;")
                migrations_performed.append("Renamed 'code' to 'employee_code'")
            else:
                # Add new employee_code column
                print("  └─ Adding new employee_code column...")
                cursor.execute("ALTER TABLE teams ADD COLUMN employee_code VARCHAR(10);")
                
                # Update existing rows with generated codes
                cursor.execute("SELECT id FROM teams WHERE employee_code IS NULL;")
                teams_without_codes = cursor.fetchall()
                
                if teams_without_codes:
                    print(f"  └─ Generating employee codes for {len(teams_without_codes)} existing teams...")
                    import random
                    import string
                    
                    for (team_id,) in teams_without_codes:
                        # Generate a unique code
                        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
                        code = ''.join(random.choices(chars, k=6))
                        cursor.execute("UPDATE teams SET employee_code = %s WHERE id = %s;", (code, team_id))
                
                # Make employee_code NOT NULL and UNIQUE
                cursor.execute("ALTER TABLE teams ALTER COLUMN employee_code SET NOT NULL;")
                cursor.execute("ALTER TABLE teams ADD CONSTRAINT teams_employee_code_unique UNIQUE (employee_code);")
                migrations_performed.append("Added employee_code column with constraints")
        
        # Migration 2: Ensure all required indexes exist
        print("🔧 Checking and adding required indexes...")
        
        # Check if employee_code index exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE tablename = 'teams' 
                AND indexname LIKE '%employee_code%'
            );
        """)
        
        if not cursor.fetchone()[0]:
            print("  └─ Adding index on employee_code...")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_teams_employee_code ON teams (employee_code);")
            migrations_performed.append("Added employee_code index")
        
        # Migration 3: Verify constraints
        print("🔧 Verifying table constraints...")
        
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'teams' 
            AND constraint_type = 'UNIQUE'
            AND constraint_name LIKE '%employee_code%';
        """)
        
        unique_constraints = cursor.fetchall()
        if not unique_constraints:
            print("  └─ Adding unique constraint on employee_code...")
            try:
                cursor.execute("ALTER TABLE teams ADD CONSTRAINT teams_employee_code_unique UNIQUE (employee_code);")
                migrations_performed.append("Added employee_code unique constraint")
            except psycopg2.errors.DuplicateTable:
                print("  └─ Unique constraint already exists")
        
        # Commit all changes
        conn.commit()
        
        print("✅ Database migration completed successfully!")
        if migrations_performed:
            print("📝 Migrations performed:")
            for migration in migrations_performed:
                print(f"  - {migration}")
        else:
            print("📝 No migrations needed - database is up to date")
        
        # Verify the final schema
        print("\n🔍 Final teams table structure:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'teams'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)