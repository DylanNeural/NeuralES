from sqlalchemy import create_engine, inspect, text
from app.config.settings import Settings

settings = Settings()
engine = create_engine(settings.database_url)
inspector = inspect(engine)
tables = inspector.get_table_names()
print('All tables in DB:', tables)
print('\nt_dispositif exists:', 't_dispositif' in tables)

if 't_dispositif' in tables:
    cols = inspector.get_columns('t_dispositif')
    print('\nColumns in t_dispositif:')
    for col in cols:
        print(f"  {col['name']}: {col['type']}")
else:
    print("\n❌ t_dispositif table NOT FOUND - migration not applied!")
    print("\nTrying to check if schema migrations are applied...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM t_organisation LIMIT 1"))
        print("t_organisation exists: True")
