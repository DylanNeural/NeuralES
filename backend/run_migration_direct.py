#!/usr/bin/env python
"""Execute migration using SQLAlchemy engine.begin()"""
import sys
sys.path.insert(0, '.')

from sqlalchemy import text
from app.data.db import engine

# Read migration SQL
with open('migrations/001_add_reference_tables.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

log_file = 'migration_direct.log'

# Clear log
with open(log_file, 'w', encoding='utf-8') as f:
    f.write('=== Direct Migration Execution ===\n\n')

def log_msg(msg):
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
    print(msg, flush=True)

try:
    log_msg('Reading migration SQL...')
    log_msg(f'SQL size: {len(sql)} characters')
    
    # Use engine.begin() for guaranteed transaction commit
    with engine.begin() as conn:
        log_msg('[1] Executing all migration SQL using engine.begin()...')
        try:
            # Execute SQL as a single text block
            conn.execute(text(sql))
            # Transaction will auto-commit when exiting the context manager
            log_msg('[OK] All SQL executed successfully')
            log_msg('[OK] Transaction committed')
        except Exception as sql_err:
            log_msg(f'[ERROR] {str(sql_err)}')
            # Transaction will rollback when exiting the context manager on error
            raise
    
    log_msg('\n=== Migration Complete ===')
    log_msg('[OK] Tables created successfully')
    log_msg('[OK] Columns added successfully')
    log_msg('[OK] Indexes created successfully')
    
except Exception as e:
    import traceback
    log_msg(f'\n[FAILED] {str(e)}')
    log_msg(traceback.format_exc())
    sys.exit(1)
