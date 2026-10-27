import os
from pathlib import Path

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
VIDEO_EXTS = (".mp4", ".mkv", ".avi", ".webm", ".m4v")

def detect_media_folders(base_path: str | Path | None, media_root: str | Path | None = None, media_spec: list[dict] | None = None) -> dict[str, str]:
    """
    Escanea la carpeta de medios seleccionada buscando las subcarpetas requeridas
    estrictamente según la especificación del layout (media_spec).
    No asume alias ni carpetas fuera de la ruta indicada.
    """
    detected = {
        "media_path": "",
        "boxart_path": "",
        "wheel_path": "",
        "video_path": "",
        "cartart_path": ""
    }

    target_dir = None
    if media_root:
        mr_path = Path(media_root)
        if mr_path.is_dir():
            target_dir = mr_path
            detected["media_path"] = str(mr_path)
    elif base_path:
        bp = Path(base_path)
        if bp.is_dir():
            m_sub = bp / "media"
            if m_sub.is_dir():
                target_dir = m_sub
                detected["media_path"] = str(m_sub)
            else:
                target_dir = bp

    if not target_dir or not target_dir.is_dir() or not media_spec:
        return detected

    try:
        subdirs = {entry.name.lower(): entry.path for entry in os.scandir(target_dir) if entry.is_dir()}
    except Exception:
        return detected

    for item in media_spec:
        key = item.get("key", "")
        target_field = f"{key}_path"
        if target_field not in detected or detected[target_field]:
            continue

        folder_name = (item.get("folder") or key).lower()
        cand_names = [folder_name]
        if folder_name.endswith("s"):
            cand_names.append(folder_name[:-1])
        else:
            cand_names.append(folder_name + "s")
        if key.lower() not in cand_names:
            cand_names.append(key.lower())

        for name in cand_names:
            if name in subdirs:
                sub_path = subdirs[name]
                exts = item.get("extensions")
                if exts:
                    has_files = False
                    try:
                        for file_entry in os.scandir(sub_path):
                            if file_entry.is_file() and any(file_entry.name.lower().endswith(e.lower()) for e in exts):
                                has_files = True
                                break
                    except Exception:
                        has_files = True
                    if has_files:
                        detected[target_field] = sub_path
                        break
                else:
                    detected[target_field] = sub_path
                    break

    return detected


def find_media_file(folder: str | Path | None, base_name: str, extensions: tuple[str, ...]) -> str | None:
    """Busca un archivo con base_name y alguna de las extensiones dentro de folder."""
    if not folder:
        return None
    f_path = Path(folder)
    if not f_path.is_dir():
        return None

    # Búsqueda exacta
    for ext in extensions:
        candidate = f_path / f"{base_name}{ext}"
        if candidate.is_file():
            return str(candidate)

    # Búsqueda con comparación insensible a mayúsculas
    try:
        lower_candidates = {f"{base_name.lower()}{ext.lower()}": ext for ext in extensions}
        for entry in os.scandir(folder):
            if entry.is_file() and entry.name.lower() in lower_candidates:
                return entry.path
    except Exception:
        pass

    return None


def resolve_game_media(*args, **kwargs) -> dict[str, str | None]:
    """
    Resuelve las rutas completas a los archivos multimedia (boxart, wheel, video/snap, cartart)
    para un juego según el archivo de ROM y la configuración de su lista o datos del juego.
    Soporta múltiples formas de llamada:
      - resolve_game_media(rom_path, list_row)
      - resolve_game_media(db, gid, game)
      - resolve_game_media(game)
    """
    media = {
        "boxart": None,
        "wheel": None,
        "video": None,
        "snap": None,
        "cartart": None
    }

    rom_path = ""
    list_row = None

    if len(args) == 3:
        # resolve_game_media(db, gid, game)
        _db, _gid, list_row = args
    elif len(args) == 2:
        a0, a1 = args
        if isinstance(a0, str):
            rom_path = a0
            list_row = a1
        else:
            list_row = a1
    elif len(args) == 1:
        a0 = args[0]
        if isinstance(a0, str):
            rom_path = a0
        else:
            list_row = a0
    else:
        rom_path = kwargs.get("rom_path", "")
        list_row = kwargs.get("list_row", kwargs.get("game"))

    row_dict = {}
    if list_row is not None:
        if isinstance(list_row, dict):
            row_dict = list_row
        elif hasattr(list_row, "keys"):
            row_dict = dict(list_row)

    if not rom_path and row_dict:
        rom_path = row_dict.get("rom_path") or ""

    stem = Path(rom_path).stem if rom_path else ""

    if stem and row_dict:
        root_m = row_dict.get("media_path")
        m_root_path = Path(root_m) if root_m and os.path.isdir(root_m) else None

        # 1. Box Art
        box_folder = row_dict.get("boxart_path")
        if box_folder and os.path.isdir(box_folder):
            media["boxart"] = find_media_file(box_folder, stem, IMAGE_EXTS)

        # 2. Wheel Logos
        wheel_folder = row_dict.get("wheel_path")
        if wheel_folder and os.path.isdir(wheel_folder):
            media["wheel"] = find_media_file(wheel_folder, stem, IMAGE_EXTS)

        # 3. Video Snaps
        video_folder = row_dict.get("video_path")
        if video_folder and os.path.isdir(video_folder):
            v_found = find_media_file(video_folder, stem, VIDEO_EXTS)
            media["video"] = v_found
            media["snap"] = v_found

        # 4. Cart Art
        cart_folder = row_dict.get("cartart_path")
        if cart_folder and os.path.isdir(cart_folder):
            media["cartart"] = find_media_file(cart_folder, stem, IMAGE_EXTS)

    # Resolución de medios para Menú de Sistemas (cuando el item representa una lista/consola)
    if (not stem or row_dict.get("is_menu_target")) and row_dict:
        import re
        sys_name = (row_dict.get("title") or "").strip()
        plat_name = (row_dict.get("platform") or "").strip()

        # Generar variaciones de nombre de la lista para coincidir con el archivo
        candidates = []
        for n in (sys_name, plat_name):
            if not n:
                continue
            if n not in candidates:
                candidates.append(n)
            # Sin contenido entre paréntesis, ej: "Super Nintendo (SNES)" -> "Super Nintendo"
            clean_paren = re.sub(r"\s*\(.*?\)", "", n).strip()
            if clean_paren and clean_paren not in candidates:
                candidates.append(clean_paren)
            # Reemplazar barras o guiones
            clean_slash = n.replace("/", " - ").replace("\\", " - ").strip()
            if clean_slash and clean_slash not in candidates:
                candidates.append(clean_slash)

        # 1. Wheel Logos
        wheel_folder = row_dict.get("menu_wheel_path") or row_dict.get("wheel_path")
        if wheel_folder and os.path.isdir(wheel_folder):
            for cand in candidates:
                found = find_media_file(wheel_folder, cand, IMAGE_EXTS)
                if found:
                    media["wheel"] = found
                    break

        # 2. Video Snaps
        video_folder = row_dict.get("menu_video_path") or row_dict.get("video_path")
        if video_folder and os.path.isdir(video_folder):
            for cand in candidates:
                found = find_media_file(video_folder, cand, VIDEO_EXTS)
                if found:
                    media["video"] = found
                    media["snap"] = found
                    break

        # 3. Box Art
        box_folder = row_dict.get("menu_boxart_path") or row_dict.get("boxart_path")
        if box_folder and os.path.isdir(box_folder):
            for cand in candidates:
                found = find_media_file(box_folder, cand, IMAGE_EXTS)
                if found:
                    media["boxart"] = found
                    break

        # 4. Cart Art
        cart_folder = row_dict.get("menu_cartart_path") or row_dict.get("cartart_path")
        if cart_folder and os.path.isdir(cart_folder):
            for cand in candidates:
                found = find_media_file(cart_folder, cand, IMAGE_EXTS)
                if found:
                    media["cartart"] = found
                    break


    # Carátula personalizada asignada manualmente a un juego individual (games.cover_path)
    if row_dict and not media["boxart"] and not row_dict.get("is_menu_target"):
        c_path = row_dict.get("cover_path")
        if c_path and os.path.isfile(c_path):
            media["boxart"] = c_path

    # Sincronizar clave snap con video
    media["snap"] = media["video"]
    return media
