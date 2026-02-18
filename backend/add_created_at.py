from sqlalchemy import create_engine, text
from app.config.settings import Settings

settings = Settings()
engine = create_engine(settings.database_url)

with engine.connect() as conn:
    sql = "ALTER TABLE t_dispositif ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL;"
    try:
        conn.execute(text(sql))
        conn.commit()
        print("✓ Colonne created_at ajoutée à t_dispositif")
    except Exception as e:
        error_str = str(e)
        if "already exists" in error_str or "duplicate" in error_str.lower():
            print("✓ Colonne created_at existe déjà")
        else:
            print(f"Erreur: {e}")
