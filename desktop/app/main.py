import sys
from PySide6.QtWidgets import QApplication
from app.pages.login import LoginWindow

def main():
    app = QApplication(sys.argv)

    # Charger le thème global QSS
    from pathlib import Path

    base_dir = Path(__file__).resolve().parent          # .../desktop/app
    qss_path = base_dir / "ressources" / "theme.qss"

    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
    else:
        print(f"[WARN] QSS introuvable: {qss_path}")


    w = LoginWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
