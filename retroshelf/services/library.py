from pathlib import Path
import re

GENERIC_EXTENSION_WARNINGS = {
    ".bin": "La extensión '.bin' es genérica y puede coincidir con archivos auxiliares o pistas secundarias de disco (por ejemplo en pistas CUE/BIN).",
    ".dat": "La extensión '.dat' suele utilizarse para archivos de datos auxiliares o metadatos, no necesariamente ejecutables.",
}

def normalize_extensions(raw_text: str) -> tuple[str, list[str]]:
    """
    Normaliza y valida una cadena de extensiones separadas exclusivamente por punto y coma (;).

    Retorna:
        tuple[str, list[str]]: (extensiones_normalizadas_separadas_por_punto_y_coma, advertencias)

    Lanza:
        ValueError: Si el campo está vacío, contiene comas, o alguna extensión tiene formato inválido.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("El campo de extensiones no puede estar vacío. Indicá al menos una extensión (ej: .sfc;.smc;.zip).")

    # Regla estricta: No permitir comas como separador
    if "," in raw_text:
        raise ValueError(
            "Las extensiones deben separarse exclusivamente mediante punto y coma (;).\n"
            "Se detectaron comas (,). Reemplazá las comas por punto y coma (ej: .cue;.bin;.iso)."
        )

    tokens = raw_text.split(";")
    normalized_list: list[str] = []
    seen = set()
    warnings: list[str] = []

    for raw_token in tokens:
        token = raw_token.strip()
        if not token:
            continue

        # Aceptar con o sin punto inicial
        if not token.startswith("."):
            token = f".{token}"

        # Convertir a minúsculas
        token = token.lower()

        # Validar formato: debe comenzar con un punto seguido de caracteres alfanuméricos válidos
        if not re.match(r"^\.[a-z0-9_\-\.]{1,20}$", token) or token == ".":
            raise ValueError(
                f"La extensión '{raw_token.strip()}' tiene un formato inválido.\n"
                "Solo debe contener letras, números y el punto inicial (ej: .gba, .sfc, .iso)."
            )

        # Evitar duplicados manteniendo orden
        if token not in seen:
            seen.add(token)
            normalized_list.append(token)

            # Advertir sobre extensiones genéricas
            if token in GENERIC_EXTENSION_WARNINGS:
                warnings.append(GENERIC_EXTENSION_WARNINGS[token])

    if not normalized_list:
        raise ValueError("No se encontraron extensiones válidas en el texto ingresado.")

    return ";".join(normalized_list), warnings


def parse_extensions_list(extensions_str: str) -> list[str]:
    """
    Convierte la cadena almacenada en la base de datos (separada por ;) en una lista de extensiones en minúsculas.
    """
    if not extensions_str:
        return []
    result = []
    for ext in extensions_str.split(";"):
        clean = ext.strip().lower()
        if clean:
            if not clean.startswith("."):
                clean = f".{clean}"
            if clean not in result:
                result.append(clean)
    return result


def scan_rom_folder(folder: str | Path, allowed_extensions: list[str] | str) -> list[Path]:
    """
    Escanea recursivamente una carpeta en busca de archivos cuyas extensiones
    coincidan con la lista permitida para la lista seleccionada.
    """
    root = Path(folder)
    if not root.is_dir():
        raise ValueError("La ruta seleccionada no es una carpeta válida o accesible.")

    if isinstance(allowed_extensions, str):
        allowed_list = parse_extensions_list(allowed_extensions)
    else:
        allowed_list = [
            (e.lower() if e.startswith(".") else f".{e.lower()}").strip()
            for e in allowed_extensions if e.strip()
        ]

    allowed_set = set(allowed_list)
    if not allowed_set:
        raise ValueError(
            "Esta lista no tiene extensiones configuradas.\n"
            "Editá la lista y configurá las extensiones permitidas separadas por ';' antes de escanear."
        )

    matched: list[Path] = []
    for item in root.rglob("*"):
        try:
            if item.is_file() and item.suffix.lower() in allowed_set:
                matched.append(item)
        except (PermissionError, OSError):
            continue

    return sorted(matched, key=lambda p: str(p).lower())


def import_scanned_games(db, list_id: int, paths: list[Path]) -> dict:
    """
    Importa una lista de rutas de juegos a una lista determinada en SQLite,
    evitando duplicar archivos ya importados previamente.
    Retorna un diccionario con el resumen de la importación.
    """
    rows = db.all("SELECT rom_path FROM games WHERE list_id=?", (list_id,))
    existing_paths = {str(Path(r["rom_path"]).resolve()).lower() for r in rows}

    added = 0
    skipped = 0

    for path in paths:
        try:
            resolved = str(path.resolve())
            if resolved.lower() in existing_paths:
                skipped += 1
                continue

            title = path.stem
            db.execute(
                "INSERT INTO games(list_id, title, rom_path) VALUES(?,?,?)",
                (list_id, title, resolved)
            )
            existing_paths.add(resolved.lower())
            added += 1
        except Exception:
            skipped += 1

    return {
        "total_found": len(paths),
        "added": added,
        "skipped": skipped
    }


def add_game(db, list_id: int, path: str | Path, title: str | None = None) -> int | None:
    """Agrega un juego individual a una lista dada evitando duplicados."""
    p = Path(path)
    resolved = str(p.resolve())
    existing = db.one("SELECT id FROM games WHERE list_id=? AND rom_path=?", (list_id, resolved))
    if existing:
        return existing["id"]

    return db.execute(
        "INSERT INTO games(list_id, title, rom_path) VALUES(?,?,?)",
        (list_id, title or p.stem, resolved)
    )
