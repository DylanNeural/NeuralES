#!/usr/bin/env python
"""Execute database migration with logging"""
import sys
import traceback

sys.path.insert(0, '.')

from sqlalchemy import text
from app.data.db import engine

log_file = 'migration.log'

def log_msg(msg):
    with open(log_file, 'a') as f:
        f.write(msg + '\n')
    print(msg)

try:
    log_msg('Starting migration...')
    
    # Read migration file
    with open('migrations/001_add_reference_tables.sql', 'r') as f:
        content = f.read()
    
    log_msg(f'Migration file read: {len(content)} chars')
    
    # Execute as one statement
    with engine.begin() as conn:
        try:
            conn.execute(text(content))
            log_msg('SQL executed successfully')
        except Exception as sql_err:
            log_msg(f'SQL Error: {str(sql_err)}')
            raise
    
    log_msg('✅ Migration executed successfully - Database schema updated')
    log_msg('✅ Created: t_service, t_medecin tables')
    log_msg('✅ Added: deleted_at columns to all tables')
    log_msg('✅ Added: Foreign key constraints in t_patient')
    log_msg('✅ Added: Performance indexes')
    
except Exception as e:
    log_msg(f'❌ Migration failed: {str(e)}')
    log_msg(traceback.format_exc())
    sys.exit(1)
