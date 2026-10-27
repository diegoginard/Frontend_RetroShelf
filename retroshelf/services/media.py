import os
from pathlib import Path

# Nombres comunes de subcarpetas para cada tipo de medio en emulación y frontends
BOXART_NAMES = ("boxart", "box", "boxes", "flyer", "flyers", "covers", "2d_boxes", "3d_boxes", "media/boxart")
WHEEL_NAMES = ("wheel", "wheels", "logo", "logos", "clearlogo", "clearlogos", "media/wheel")
VIDEO_NAMES = ("videos", "video", "snap", "snaps", "video_snaps", "media/videos", "media/snap", "media/snaps")
CART_NAMES = ("cartart", "cart", "carts", "cartridge", "media/cartart")

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
VIDEO_EXTS = (".mp4", ".mkv", ".avi", ".webm", ".m4v")


COMMON_ALIASES = {
    "video": ("videos", "video", "snap", "snaps", "video_snaps", "gameplay"),
    "wheel": ("wheel", "wheels", "logo", "logos", "clearlogo", "clearlogos"),
    "cartart": ("cartart", "cart", "carts", "cartridge", "discs", "disc", "cd", "cds"),
    "boxart": ("boxart", "box", "boxes", "flyer", "flyers", "covers", "cover", "2d_boxes", "3d_boxes")
}


def detect_media_folders(base_path: str | Path | None, media_root: str | Path | None = None, media_spec: list[dict] | None = None) -> dict[str, str]:
    """
    Escanea la carpeta de medios o la carpeta de ROMs buscando automáticamente
    las subcarpetas de medios requeridas según la especificación del layout (media_spec).
    """
    detected = {
        "media_path": "",
        "boxart_path": "",
        "wheel_path": "",
        "video_path": "",
        "cartart_path": ""
    }

    candidates_dirs: list[Path] = []

    # 1. Si el usuario especificó una carpeta Media raíz directa
    if media_root:
        mr_path = Path(media_root)
        if mr_path.is_dir():
            candidates_dirs.append(mr_path)
            detected["media_path"] = str(mr_path)

    # 2. Si no o adicionalmente, buscar en base_path (carpeta de ROMs o padre)
    if base_path:
        p = Path(base_path)
        if p.is_dir():
            if p.name.lower() in ("media", "medias"):
                candidates_dirs.append(p)
                if not detected["media_path"]:
                    detected["media_path"] = str(p)

            # Subcarpeta media dentro de ROMs
            m_sub = p / "media"
            if m_sub.is_dir():
                candidates_dirs.append(m_sub)
                if not detected["media_path"]:
                    detected["media_path"] = str(m_sub)

            # Carpeta media hermana al mismo nivel que ROMs
            if p.parent and p.parent != p:
                m_sibling = p.parent / "media"
                if m_sibling.is_dir():
                    candidates_dirs.append(m_sibling)
                    if not detected["media_path"]:
                        detected["media_path"] = str(m_sibling)

            candidates_dirs.append(p)
            if p.parent and p.parent != p:
                candidates_dirs.append(p.parent)

    for c in candidates_dirs:
        try:
            subdirs = {entry.name.lower(): entry.path for entry in os.scandir(c) if entry.is_dir()}
        except Exception:
            continue

        if media_spec:
            for item in media_spec:
                key = item.get("key", "")
                target_field = f"{key}_path"
                if target_field not in detected:
                    detected[target_field] = ""
                if detected[target_field]:
                    continue

                folder_name = (item.get("folder") or key).lower()
                cand_names = [folder_name]
                if key in COMMON_ALIASES:
                    cand_names.extend(COMMON_ALIASES[key])

                for name in cand_names:
                    if name in subdirs:
                        sub_path = subdirs[name]
                        # Opcional: verificar que contenga al menos un archivo con extensiones esperadas
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
        else:
            # Detección genérica clásica
            if not detected["boxart_path"]:
                for name in ("boxart", "box", "boxes", "flyer", "covers", "cover"):
                    if name in subdirs:
                        detected["boxart_path"] = subdirs[name]
                        break

            if not detected["wheel_path"]:
                for name in ("wheel", "wheels", "logo", "logos", "clearlogo"):
                    if name in subdirs:
                        detected["wheel_path"] = subdirs[name]
                        break

            if not detected["video_path"]:
                for name in ("videos", "video", "snap", "snaps", "video_snaps"):
                    if name in subdirs:
                        detected["video_path"] = subdirs[name]
                        break

            if not detected["cartart_path"]:
                for name in ("cartart", "cart", "carts", "cartridge", "discs", "disc"):
                    if name in subdirs:
                        detected["cartart_path"] = subdirs[name]
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
        box_folder = row_dict.get("boxart_path") or (str(m_root_path / "boxart") if m_root_path and (m_root_path / "boxart").is_dir() else None)
        if box_folder and os.path.isdir(box_folder):
            media["boxart"] = find_media_file(box_folder, stem, IMAGE_EXTS)

        # 2. Wheel Logos
        wheel_folder = row_dict.get("wheel_path") or (str(m_root_path / "wheel") if m_root_path and (m_root_path / "wheel").is_dir() else None)
        if wheel_folder and os.path.isdir(wheel_folder):
            media["wheel"] = find_media_file(wheel_folder, stem, IMAGE_EXTS)

        # 3. Video Snaps
        video_folder = row_dict.get("video_path") or (str(m_root_path / "videos") if m_root_path and (m_root_path / "videos").is_dir() else None)
        if video_folder and os.path.isdir(video_folder):
            media["video"] = find_media_file(video_folder, stem, VIDEO_EXTS)

        # 4. Cart Art
        cart_folder = row_dict.get("cartart_path") or (str(m_root_path / "cartart") if m_root_path and (m_root_path / "cartart").is_dir() else None)
        if cart_folder and os.path.isdir(cart_folder):
            media["cartart"] = find_media_file(cart_folder, stem, IMAGE_EXTS)

    # Resolución de medios para Menú de Sistemas (cuando el item representa una lista/consola)
    if (not stem or row_dict.get("is_menu_target")) and row_dict:
        sys_name = row_dict.get("title") or ""
        plat_name = row_dict.get("platform") or sys_name
        candidates = [c for c in (sys_name, plat_name) if c]

        root_m = row_dict.get("media_path")
        m_root_path = Path(root_m) if root_m and os.path.isdir(root_m) else None

        # 1. Wheel Logos desde carpeta wheel_path o fallback
        wheel_folder = row_dict.get("wheel_path") or (str(m_root_path / "wheel") if m_root_path and (m_root_path / "wheel").is_dir() else None)
        if wheel_folder and os.path.isdir(wheel_folder) and not media["wheel"]:
            for cand in candidates:
                found = find_media_file(wheel_folder, cand, IMAGE_EXTS)
                if found:
                    media["wheel"] = found
                    break

        # 2. Box Art desde carpeta boxart_path o fallback
        box_folder = row_dict.get("boxart_path") or (str(m_root_path / "boxart") if m_root_path and (m_root_path / "boxart").is_dir() else None)
        if box_folder and os.path.isdir(box_folder) and not media["boxart"]:
            for cand in candidates:
                found = find_media_file(box_folder, cand, IMAGE_EXTS)
                if found:
                    media["boxart"] = found
                    break

        # 3. Video Snaps desde carpeta video_path o fallback
        video_folder = row_dict.get("video_path") or (str(m_root_path / "videos") if m_root_path and (m_root_path / "videos").is_dir() else None)
        if video_folder and os.path.isdir(video_folder) and not media["video"]:
            for cand in candidates:
                found = find_media_file(video_folder, cand, VIDEO_EXTS)
                if found:
                    media["video"] = found
                    break

        # 4. Fallback automático a los recursos de temas (Layouts/<Sistema>/logo.png, etc.)
        try:
            from retroshelf.services.themes import get_all_theme_layouts
            from retroshelf.ui.layouts import resolve_theme_name
            themes = get_all_theme_layouts()
            matched = resolve_theme_name(plat_name, themes) or resolve_theme_name(sys_name, themes)
            if matched and matched in themes:
                th_folder = Path(themes[matched]["folder"])
                if not media["wheel"]:
                    logo_file = th_folder / "logo.png"
                    if logo_file.is_file():
                        media["wheel"] = str(logo_file)
                if not media["boxart"]:
                    for art_name in ("console.png", "avatar.png", "boxart.png"):
                        art_file = th_folder / art_name
                        if art_file.is_file():
                            media["boxart"] = str(art_file)
                            break
                if not media["cartart"]:
                    cart_file = th_folder / "cartart.png"
                    if cart_file.is_file():
                        media["cartart"] = str(cart_file)
        except Exception:
            pass

    # Fallbacks directos si los campos contienen rutas de archivo directas
    if row_dict:
        if not media["boxart"]:
            for k in ("cover_path", "boxart_path", "boxart"):
                val = row_dict.get(k)
                if val and os.path.isfile(val):
                    media["boxart"] = val
                    break

        if not media["cartart"]:
            for k in ("cartart_path", "cartart", "cart_path"):
                val = row_dict.get(k)
                if val and os.path.isfile(val):
                    media["cartart"] = val
                    break

        if not media["video"]:
            for k in ("video_path", "snap_path", "video", "snap"):
                val = row_dict.get(k)
                if val and os.path.isfile(val):
                    media["video"] = val
                    break

        if not media["wheel"]:
            for k in ("wheel_path", "logo_path", "wheel", "logo"):
                val = row_dict.get(k)
                if val and os.path.isfile(val):
                    media["wheel"] = val
                    break

    # Sincronizar clave snap con video
    media["snap"] = media["video"]
    return media
