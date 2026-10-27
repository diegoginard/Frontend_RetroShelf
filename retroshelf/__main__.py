import sys
from pathlib import Path

# Asegurar que el directorio raíz de RetroShelf esté en sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

def main():
    import os
    try:
        from retroshelf.db import Database
        db = Database()
        driver = db.get_setting("video_driver", "d3d11")
        if driver:
            os.environ["QSG_RHI_BACKEND"] = driver
            os.environ["QT_RHI_BACKEND"] = driver
    except Exception:
        pass

    if "--player" in sys.argv or "--play" in sys.argv:
        from retroshelf.ui.player_window import run_player
        run_player()
    else:
        from retroshelf.ui.main_window import run
        run()

if __name__ == "__main__":
    main()
