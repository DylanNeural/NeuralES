#!/usr/bin/env python
"""Complete setup v2: Using direct migration"""
import sys
import subprocess

sys.path.insert(0, '.')

setup_log = 'setup_v2.log'

with open(setup_log, 'w', encoding='utf-8') as f:
    f.write('=== Setup V2 - Direct Migration + Seed ===\n\n')

def log_msg(msg):
    with open(setup_log, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
    print(msg, flush=True)

try:
    log_msg('Step 1: Running Direct Migration...')
    log_msg('-' * 50)
    
    # Run migration directly
    result = subprocess.run([sys.executable, 'run_migration_direct.py'], 
                          capture_output=True, text=True)
    
    # Append migration output to log if it exists
    if __import__('os').path.exists('migration_direct.log'):
        with open('migration_direct.log', 'r', encoding='utf-8') as f:
            migration_log = f.read()
        with open(setup_log, 'a', encoding='utf-8') as f:
            f.write(migration_log + '\n\n')
        print(migration_log)
    else:
        # Migration might have failed to create log
        log_msg('Migration Direct Log not found.')
        if result.stdout:
            log_msg('STDOUT: ' + result.stdout)
        if result.stderr:
            log_msg('STDERR: ' + result.stderr)
    
    if result.returncode != 0:
        log_msg(f'\n[ERROR] Migration failed with code {result.returncode}')
        log_msg(result.stderr)
        sys.exit(1)
    
    log_msg('\nStep 2: Seeding Database...')
    log_msg('-' * 50)
    
    from seed_db import main as seed_main
    seed_main()
    
    log_msg('\n[OK] Setup complete!')
    log_msg('Next: Restart backend')
    
except Exception as e:
    import traceback
    log_msg(f'\n[ERROR] {str(e)}')
    log_msg(traceback.format_exc())
    sys.exit(1)
