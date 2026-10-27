from pathlib import Path
import sqlite3
import os

APP_DIR = Path(os.environ.get("APPDATA", Path.home())) / "RetroShelf"
DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "retroshelf.db"

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS emulators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    executable TEXT NOT NULL,
    arguments TEXT NOT NULL DEFAULT '"{rom}"',
    platform TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS game_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    platform TEXT NOT NULL DEFAULT '',
    default_emulator_id INTEGER REFERENCES emulators(id) ON DELETE SET NULL,
    layout TEXT NOT NULL DEFAULT 'Wheel',
    allowed_extensions TEXT NOT NULL DEFAULT '',
    roms_path TEXT NOT NULL DEFAULT '',
    media_path TEXT NOT NULL DEFAULT '',
    boxart_path TEXT NOT NULL DEFAULT '',
    wheel_path TEXT NOT NULL DEFAULT '',
    video_path TEXT NOT NULL DEFAULT '',
    cartart_path TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL REFERENCES game_lists(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    rom_path TEXT NOT NULL,
    emulator_override_id INTEGER REFERENCES emulators(id) ON DELETE SET NULL,
    launch_arguments TEXT NOT NULL DEFAULT '',
    cover_path TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(list_id, rom_path)
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_games_list ON games(list_id);
"""

class Database:
    def __init__(self, path=DB_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as con:
            con.executescript(SCHEMA)
        self._migrate()

    def _migrate(self):
        """Asegura la compatibilidad con esquemas anteriores agregando columnas faltantes."""
        with self.connect() as con:
            con.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            con.commit()
            cols = [r[1] for r in con.execute("PRAGMA table_info(game_lists)").fetchall()]
            for col in ("allowed_extensions", "roms_path", "media_path", "boxart_path", "wheel_path", "video_path", "cartart_path"):
                if col not in cols:
                    con.execute(f"ALTER TABLE game_lists ADD COLUMN {col} TEXT NOT NULL DEFAULT ''")
                    con.commit()


    def connect(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        return con

    def all(self, sql, params=()):
        with self.connect() as con:
            return con.execute(sql, params).fetchall()

    def one(self, sql, params=()):
        with self.connect() as con:
            return con.execute(sql, params).fetchone()

    def execute(self, sql, params=()):
        with self.connect() as con:
            cur = con.execute(sql, params)
            con.commit()
            return cur.lastrowid

    def get_setting(self, key: str, default: str = None) -> str | None:
        row = self.one("SELECT value FROM settings WHERE key=?", (key,))
        return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        with self.connect() as con:
            con.execute(
                "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, str(value))
            )
            con.commit()

    def get_media_path(self, game_id: int, media_type: str) -> str | None:
        """Resuelve la ruta a un archivo de medio (wheel, boxart, video, cartart) para un juego."""
        from retroshelf.services.media import resolve_game_media
        row = self.one(
            """SELECT g.*, l.boxart_path, l.wheel_path, l.video_path, l.cartart_path
               FROM games g JOIN game_lists l ON l.id = g.list_id WHERE g.id = ?""",
            (game_id,)
        )
        if not row:
            return None
        media = resolve_game_media(dict(row))
        return media.get(media_type)


