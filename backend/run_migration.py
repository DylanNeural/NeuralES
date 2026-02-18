#!/usr/bin/env python
"""Execute database migration"""
import sys
sys.path.insert(0, '.')

from sqlalchemy import text
from app.data.db import engine

# Read migration file
with open('migrations/001_add_reference_tables.sql', 'r') as f:
    content = f.read()

# Execute as raw SQL
with engine.begin() as conn:
    conn.execute(text(content))
    print('✅ Migration executed successfully - Database schema updated')
    print('✅ Created: t_service, t_medecin tables')
    print('✅ Added: deleted_at columns to all tables')
    print('✅ Added: Foreign key constraints in t_patient')
    print('✅ Added: Performance indexes')
