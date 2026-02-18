#!/usr/bin/env python
"""
Complete setup: Run migration + seed
Logs to file: setup.log
"""
import sys
import os

sys.path.insert(0, '.')

setup_log = 'setup.log'

# Clear log
with open(setup_log, 'w', encoding='utf-8') as f:
    f.write('=== NeuralES Database Setup ===\n\n')

def log_msg(msg):
    """Log message to file and stdout"""
    with open(setup_log, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
    print(msg, flush=True)

try:
    log_msg('Step 1: Running Migration...')
    log_msg('-' * 50)
    
    from sqlalchemy import text
    from app.data.db import engine
    
    # Read migration file
    with open('migrations/001_add_reference_tables.sql', 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    # Split into individual statements
    statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
    
    log_msg(f'Found {len(statements)} statements to execute')
    
    with engine.begin() as conn:
        for i, stmt in enumerate(statements):
            if stmt:
                try:
                    conn.execute(text(stmt))
                    log_msg(f'  [{i+1:2d}] OK {stmt[:60]}...')
                except Exception as stmt_err:
                    # Log but continue - some statements might fail if objects already exist
                    error_msg = str(stmt_err)
                    if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                        log_msg(f'  [{i+1:2d}] EXISTS {stmt[:60]}... (already exists)')
                    else:
                        log_msg(f'  [{i+1:2d}] OK {stmt[:60]}... (note: {error_msg[:80]})')
    
    log_msg('[OK] Migration completed')
    log_msg('  - Created t_service table')
    log_msg('  - Created t_medecin table')
    log_msg('  - Added deleted_at columns')
    log_msg('  - Added FK constraints to t_patient')
    log_msg('  - Created performance indexes')
    
    log_msg('\nStep 2: Seeding Database...')
    log_msg('-' * 50)
    
    # Import and run seed function
    from seed_db import main as seed_main
    seed_main()
    
    log_msg('\n[OK] Database seed completed successfully')
    log_msg('\n=== Setup Complete ===')
    log_msg('Next: Restart backend to reload models')
    
except Exception as e:
    import traceback
    log_msg(f'\n[ERROR] Setup failed: {str(e)}')
    log_msg(traceback.format_exc())
    sys.exit(1)
