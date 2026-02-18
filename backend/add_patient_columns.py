"""
Migration script pour ajouter les colonnes manquantes à t_patient
Lance-le une seule fois depuis le backend:
    python add_patient_columns.py
"""
from sqlalchemy import text
from app.data.db import SessionLocal

def add_patient_columns():
    db = SessionLocal()
    try:
        # Vérifier si les colonnes existent avant de les ajouter
        columns_to_add = [
            ("nom", "VARCHAR(100) NOT NULL DEFAULT ''"),
            ("prenom", "VARCHAR(100) NOT NULL DEFAULT ''"),
            ("numero_securite_sociale", "VARCHAR(13) UNIQUE"),
            ("service", "VARCHAR(100)"),
            ("medecin_referent", "VARCHAR(100)"),
            ("remarque", "VARCHAR(500)"),
        ]
        
        for col_name, col_def in columns_to_add:
            try:
                db.execute(text(f"ALTER TABLE t_patient ADD COLUMN {col_name} {col_def}"))
                print(f"✓ Colonne '{col_name}' ajoutée")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e):
                    print(f"⊘ Colonne '{col_name}' existe déjà")
                else:
                    print(f"✗ Erreur pour '{col_name}': {e}")
        
        db.commit()
        print("\n✓ Migration terminée")
    except Exception as e:
        print(f"✗ Erreur générale: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_patient_columns()
