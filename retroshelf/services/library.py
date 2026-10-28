from pathlib import Path
from contextlib import nullcontext
import json
import os
import re
import xml.etree.ElementTree as ET

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


def parse_rom_folders(folders_raw: str | list[str | Path] | Path | None) -> list[str]:
    """
    Convierte una cadena de carpetas separadas por ';' (o salto de línea) o una lista de rutas
    en una lista limpia de rutas de carpetas sin duplicados.
    """
    if not folders_raw:
        return []
    if isinstance(folders_raw, Path):
        s = str(folders_raw).strip()
        return [s] if s else []
    if isinstance(folders_raw, str):
        tokens = re.split(r"[;\r\n]+", folders_raw)
    else:
        tokens = []
        for item in folders_raw:
            if item:
                tokens.extend(re.split(r"[;\r\n]+", str(item)))

    result: list[str] = []
    seen: set[str] = set()
    for tok in tokens:
        clean = tok.strip().strip('"').strip("'")
        if not clean:
            continue
        norm_key = clean.replace("/", "\\").rstrip("\\").lower()
        if norm_key not in seen:
            seen.add(norm_key)
            result.append(clean)
    return result


def format_rom_folders(folders: list[str | Path] | str | None) -> str:
    """
    Serializa una lista de carpetas de ROMs en una cadena separada por punto y coma (;).
    """
    return ";".join(parse_rom_folders(folders))


def scan_rom_folder(folder: str | Path | list[str | Path], allowed_extensions: list[str] | str) -> list[Path]:
    """
    Escanea recursivamente una o varias carpetas en busca de archivos cuyas extensiones
    coincidan con la lista permitida para la lista seleccionada.
    """
    folder_list = parse_rom_folders(folder)
    valid_roots: list[Path] = []
    for f_str in folder_list:
        p = Path(f_str)
        if p.is_dir():
            valid_roots.append(p)

    if not valid_roots:
        raise ValueError("Ninguna de las rutas seleccionadas es una carpeta válida o accesible.")

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
    seen_resolved: set[str] = set()
    for root in valid_roots:
        for dirpath, _dirnames, filenames in os.walk(str(root)):
            for fname in filenames:
                _, ext = os.path.splitext(fname)
                if ext.lower() in allowed_set:
                    full_str = os.path.abspath(os.path.join(dirpath, fname))
                    res_key = full_str.lower()
                    if res_key not in seen_resolved:
                        seen_resolved.add(res_key)
                        matched.append(Path(full_str))

    return sorted(matched, key=lambda p: str(p).lower())


scan_rom_folders = scan_rom_folder


def _parse_xml_root(xml_file: Path) -> ET.Element:
    """
    Lee y parsea un archivo XML de ROMs (HyperSpin, MAME, Logiqx DAT, EmulationStation gamelist.xml, etc.).
    Incluye recuperación automática ante caracteres '&' sin escapar o distintas codificaciones.
    """
    try:
        tree = ET.parse(str(xml_file))
        return tree.getroot()
    except Exception:
        raw_bytes = xml_file.read_bytes()
        text = None
        for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                text = raw_bytes.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        if text is None:
            text = raw_bytes.decode("utf-8", errors="replace")

        # Sanitizar posibles '&' sueltos muy comunes en XMLs de HyperSpin / MAME (ej: "Track & Field")
        sanitized = re.sub(
            r"&(?!amp;|lt;|gt;|apos;|quot;|#\d+;|#x[0-9a-fA-F]+;)",
            "&amp;",
            text,
        )
        return ET.fromstring(sanitized)


def _extract_entry_from_element(elem: ET.Element) -> tuple[list[str], dict] | None:
    """
    Extrae las claves de asociación de la ROM (denominación / archivo) y el diccionario
    completo con el nombre completo y todas las propiedades definidas en el nodo XML.
    """
    props: dict[str, str] = {}
    raw_children: dict[str, str] = {}
    rom_child_names: list[str] = []

    # 1. Atributos directos del nodo (<game name="sf2" index="true" ...> o <machine name="sf2" cloneof="..." ...>)
    for k, v in elem.attrib.items():
        if v is None:
            continue
        val = str(v).strip()
        if val:
            k_clean = k.strip()
            props[k_clean] = val
            props[k_clean.lower()] = val

    # 2. Sub-elementos hijos (<description>, <year>, <manufacturer>, <genre>, <players>, <path>, <name>, etc.)
    for ch in elem:
        tag = ch.tag.split("}")[-1].strip() if isinstance(ch.tag, str) else ""
        if not tag:
            continue
        tag_lower = tag.lower()
        text = (ch.text or "").strip()

        if tag_lower == "rom":
            # En DATs / MAME puede haber <rom name="..." crc="..." md5="..." sha1="..." size="..."/>
            r_name = (ch.attrib.get("name") or "").strip()
            if r_name:
                rom_child_names.append(r_name)
            for rk in ("crc", "md5", "sha1", "size"):
                rv = (ch.attrib.get(rk) or "").strip()
                if rv and rk not in props:
                    props[rk] = rv
            if text and "rom" not in raw_children:
                raw_children["rom"] = text
                props["rom"] = text
        elif tag_lower == "input":
            # MAME <input players="2" coins="2"><control type="joy" buttons="6" ways="8"/></input>
            for ik, iv in ch.attrib.items():
                iv_s = str(iv).strip()
                if iv_s:
                    ik_l = ik.lower().strip()
                    if ik_l == "players" and not props.get("players"):
                        props["players"] = iv_s
                    props[f"input_{ik_l}"] = iv_s
            for sub in ch:
                sub_tag = sub.tag.split("}")[-1].lower() if isinstance(sub.tag, str) else ""
                if sub_tag == "control":
                    for ck, cv in sub.attrib.items():
                        cv_s = str(cv).strip()
                        if cv_s and f"control_{ck.lower()}" not in props:
                            props[f"control_{ck.lower()}"] = cv_s
        elif tag_lower == "driver":
            # MAME <driver status="good" emulation="good" savestate="supported"/>
            for dk, dv in ch.attrib.items():
                dv_s = str(dv).strip()
                if dv_s:
                    dk_l = dk.lower().strip()
                    props[f"driver_{dk_l}"] = dv_s
                    if dk_l == "status" and "status" not in props:
                        props["status"] = dv_s
        else:
            if text:
                raw_children[tag_lower] = text
                props[tag] = text
                props[tag_lower] = text
            for ak, av in ch.attrib.items():
                av_s = str(av).strip()
                if av_s:
                    props[f"{tag_lower}_{ak.lower().strip()}"] = av_s

    # 3. Determinar la denominación de la ROM (claves de búsqueda) y el Nombre Completo (title)
    attr_rom = (
        elem.attrib.get("name")
        or elem.attrib.get("rom")
        or elem.attrib.get("filename")
        or elem.attrib.get("file")
        or ""
    ).strip()

    path_child = (
        raw_children.get("path")
        or raw_children.get("rom")
        or raw_children.get("filename")
        or raw_children.get("file")
        or raw_children.get("romname")
        or ""
    ).strip()

    keys: list[str] = []
    full_title = ""

    if attr_rom:
        # Formato HyperSpin / MAME / Logiqx DAT (<game name="sf2"><description>Street Fighter II</description>...)
        keys.append(attr_rom)
        if path_child:
            keys.append(path_child)
        full_title = (
            raw_children.get("description")
            or raw_children.get("title")
            or raw_children.get("fullname")
            or raw_children.get("label")
            or raw_children.get("name")
            or elem.attrib.get("description")
            or elem.attrib.get("title")
            or attr_rom
        ).strip()
    elif path_child:
        # Formato EmulationStation gamelist.xml (<game><path>./sf2.zip</path><name>Street Fighter II</name>...)
        keys.append(path_child)
        full_title = (
            raw_children.get("name")
            or raw_children.get("title")
            or raw_children.get("fullname")
            or raw_children.get("label")
            or raw_children.get("description")
            or Path(path_child.replace("\\", "/")).stem
        ).strip()
    else:
        # Otros formatos (<game><name>sf2</name><description>Street Fighter II</description></game>)
        fallback_key = (
            raw_children.get("name")
            or elem.attrib.get("id")
            or raw_children.get("id")
            or ""
        ).strip()
        if not fallback_key and len(rom_child_names) == 1:
            fallback_key = rom_child_names[0]
        if fallback_key:
            keys.append(fallback_key)
        full_title = (
            raw_children.get("description")
            or raw_children.get("title")
            or raw_children.get("fullname")
            or raw_children.get("label")
            or raw_children.get("name")
            or fallback_key
        ).strip()

    # Si hay un único <rom name="..."/> hijo (ej. DATs No-Intro), agregarlo como clave secundaria
    if len(rom_child_names) == 1:
        keys.append(rom_child_names[0])

    if not keys:
        return None

    # Normalizar claves (tanto nombre de archivo como stem sin extensión, en minúsculas)
    normalized_keys: list[str] = []
    primary_rom_name = ""
    for k in keys:
        clean_k = k.replace("\\", "/").strip()
        if not clean_k:
            continue
        fname = Path(clean_k).name
        stem = Path(clean_k).stem
        if not primary_rom_name:
            primary_rom_name = stem or fname
        for candidate in (stem.lower(), fname.lower(), clean_k.lower()):
            if candidate and candidate not in normalized_keys:
                normalized_keys.append(candidate)

    if not normalized_keys:
        return None

    # 4. Extraer campos estructurados principales
    year = (props.get("year") or props.get("date") or "").strip()
    if not year and props.get("releasedate"):
        m = re.match(r"^(\d{4})", props["releasedate"].strip())
        if m:
            year = m.group(1)

    manufacturer = (
        props.get("manufacturer")
        or props.get("developer")
        or props.get("publisher")
        or props.get("company")
        or props.get("maker")
        or ""
    ).strip()

    genre = (
        props.get("genre")
        or props.get("category")
        or props.get("type")
        or ""
    ).strip()

    players = (
        props.get("players")
        or props.get("nplayers")
        or ""
    ).strip()

    cloneof = (
        props.get("cloneof")
        or props.get("romof")
        or ""
    ).strip()

    rating = (
        props.get("rating")
        or props.get("score")
        or ""
    ).strip()

    crc = (props.get("crc") or "").strip()

    # Sinopsis / Notas (evitando duplicar el título cuando <description> es el nombre del juego)
    notes = (
        raw_children.get("desc")
        or raw_children.get("plot")
        or raw_children.get("synopsis")
        or raw_children.get("story")
        or raw_children.get("history")
        or raw_children.get("notes")
        or ""
    ).strip()

    # Guardar todas las propiedades limpias para que estén disponibles si se requieren
    clean_props: dict[str, str] = {}
    for pk, pv in props.items():
        if pk == pk.lower() and pv:
            clean_props[pk] = pv
    clean_props["rom_name"] = primary_rom_name
    clean_props["title"] = full_title or primary_rom_name

    entry = {
        "title": full_title or primary_rom_name,
        "rom_name": primary_rom_name,
        "year": year,
        "manufacturer": manufacturer,
        "genre": genre,
        "players": players,
        "cloneof": cloneof,
        "rating": rating,
        "crc": crc,
        "notes": notes,
        "properties": clean_props,
    }
    return normalized_keys, entry


_XML_CACHE: dict[tuple[str, float], dict[str, dict]] = {}


def parse_rom_xml(xml_path: str | Path | None) -> dict[str, dict]:
    """
    Parsea un archivo XML de ROMs y retorna un diccionario indexado por la denominación
    de la ROM (stem y nombre de archivo en minúsculas) con su nombre completo ('title')
    y todas sus propiedades ('year', 'manufacturer', 'genre', 'players', 'cloneof',
    'rating', 'crc', 'notes', 'properties').
    Incluye caché en memoria por ruta y fecha de modificación para evitar re-parsear el mismo XML.
    """
    if not xml_path:
        return {}
    xml_file = Path(xml_path)
    if not xml_file.is_file():
        raise ValueError(f"El archivo XML especificado no existe:\n{xml_file}")

    abs_key = os.path.abspath(str(xml_file)).lower()
    try:
        mtime = os.path.getmtime(xml_file)
    except OSError:
        mtime = 0.0

    cache_key = (abs_key, mtime)
    if cache_key in _XML_CACHE:
        return _XML_CACHE[cache_key]

    root = _parse_xml_root(xml_file)
    xml_map: dict[str, dict] = {}

    # Buscar nodos <game>, <machine>, o <rom> de primer/segundo nivel
    candidate_nodes: list[ET.Element] = []
    for elem in root.iter():
        if elem is root:
            continue
        tag = elem.tag.split("}")[-1].lower() if isinstance(elem.tag, str) else ""
        if tag in ("game", "machine", "item"):
            candidate_nodes.append(elem)

    # Si el XML usa directamente etiquetas <rom> como entradas principales (sin <game>/<machine>)
    if not candidate_nodes:
        for elem in root.iter():
            if elem is root:
                continue
            tag = elem.tag.split("}")[-1].lower() if isinstance(elem.tag, str) else ""
            if tag == "rom":
                candidate_nodes.append(elem)

    for elem in candidate_nodes:
        extracted = _extract_entry_from_element(elem)
        if not extracted:
            continue
        keys, entry = extracted
        # La primera clave es la principal (ej. name="sf2"), las secundarias no pisan una principal existente
        for idx, k in enumerate(keys):
            if idx == 0 or k not in xml_map:
                xml_map[k] = entry

    _XML_CACHE[cache_key] = xml_map
    return xml_map


def lookup_xml_for_rom(xml_map: dict[str, dict] | None, rom_path: str | Path) -> dict | None:
    """
    Busca una ROM dentro del mapa XML por su denominación (nombre sin extensión o con extensión).
    """
    if not xml_map or not rom_path:
        return None
    p = Path(rom_path)
    stem_key = p.stem.lower().strip()
    if stem_key in xml_map:
        return xml_map[stem_key]
    name_key = p.name.lower().strip()
    if name_key in xml_map:
        return xml_map[name_key]
    return None


def enrich_game_dict(row) -> dict:
    """
    Convierte una fila de la tabla 'games' en un diccionario enriquecido con todas
    las propiedades del XML (tanto en 'xml_properties' como directamente en el diccionario).
    """
    d = dict(row) if not isinstance(row, dict) else dict(row)
    rom_path = d.get("rom_path") or ""
    if not d.get("rom_name") and rom_path:
        d["rom_name"] = Path(rom_path).stem

    raw_meta = d.get("xml_metadata")
    if raw_meta and isinstance(raw_meta, str):
        try:
            meta = json.loads(raw_meta)
            if isinstance(meta, dict):
                d["xml_properties"] = meta
                for k, v in meta.items():
                    if k not in d or d[k] in (None, ""):
                        d[k] = v
            else:
                d["xml_properties"] = {}
        except Exception:
            d["xml_properties"] = {}
    elif isinstance(d.get("xml_properties"), dict):
        pass
    else:
        d["xml_properties"] = {}
    return d


def apply_xml_to_list(db, list_id: int, xml_path: str | Path | None = None, xml_map: dict[str, dict] | None = None) -> dict:
    """
    Asocia las ROMs ya registradas en una lista con el archivo XML indicado,
    asignándoles su nombre completo y todas sus propiedades.
    """
    if xml_map is None:
        if not xml_path:
            row_l = db.get_list(list_id)
            xml_path = row_l.get("xml_path", "") if row_l else ""
        if not xml_path or not Path(xml_path).is_file():
            return {"total_games": 0, "matched": 0}
        xml_map = parse_rom_xml(xml_path)

    games = db.get_games(list_id, enriched=False)
    matched = 0

    batch_ctx = db.batch() if hasattr(db, "batch") else nullcontext()
    with batch_ctx:
        for g in games:
            g_dict = dict(g)
            rom_path = g_dict.get("rom_path") or ""
            if not rom_path:
                continue
            info = lookup_xml_for_rom(xml_map, rom_path)
            if not info:
                continue

            new_title = info.get("title") or Path(rom_path).stem
            rom_name = info.get("rom_name") or Path(rom_path).stem
            year = info.get("year") or g_dict.get("year") or ""
            manufacturer = info.get("manufacturer") or g_dict.get("manufacturer") or ""
            genre = info.get("genre") or g_dict.get("genre") or ""
            players = info.get("players") or g_dict.get("players") or ""
            cloneof = info.get("cloneof") or g_dict.get("cloneof") or ""
            rating = info.get("rating") or g_dict.get("rating") or ""
            crc = info.get("crc") or g_dict.get("crc") or ""
            notes = g_dict.get("notes") or info.get("notes") or ""
            xml_metadata = json.dumps(info.get("properties", {}), ensure_ascii=False)

            db.update_game(
                g_dict["id"],
                title=new_title,
                rom_name=rom_name,
                year=year,
                manufacturer=manufacturer,
                genre=genre,
                players=players,
                cloneof=cloneof,
                rating=rating,
                crc=crc,
                notes=notes,
                xml_metadata=xml_metadata,
            )
            matched += 1

    return {
        "total_games": len(games),
        "matched": matched,
    }


def import_scanned_games(db, list_id: int, paths: list[Path], xml_path: str | Path | None = None) -> dict:
    """
    Importa una lista de rutas de juegos a una lista determinada en texto plano,
    evitando duplicar archivos ya importados previamente.
    Si la lista tiene un archivo XML asociado (o se recibe xml_path), asigna el
    nombre completo y todas las propiedades del XML a cada ROM coincidente.
    Retorna un diccionario con el resumen de la importación.
    """
    if not xml_path:
        row_l = db.get_list(list_id)
        if row_l and row_l.get("xml_path"):
            xml_path = row_l["xml_path"]

    xml_map: dict[str, dict] = {}
    if xml_path and Path(xml_path).is_file():
        xml_map = parse_rom_xml(xml_path)

    rows = db.get_games(list_id, enriched=False)
    existing_by_path = {os.path.abspath(str(r["rom_path"])).lower(): dict(r) for r in rows}

    added = 0
    skipped = 0
    xml_matched = 0

    batch_ctx = db.batch() if hasattr(db, "batch") else nullcontext()
    with batch_ctx:
        for path in paths:
            try:
                resolved = os.path.abspath(str(path))
                resolved_lower = resolved.lower()
                rom_stem = path.stem if isinstance(path, Path) else Path(path).stem
                info = lookup_xml_for_rom(xml_map, path) if xml_map else None

                if resolved_lower in existing_by_path:
                    skipped += 1
                    # Si ya existía pero ahora tenemos información del XML, actualizar su nombre completo y propiedades
                    if info:
                        ex_row = existing_by_path[resolved_lower]
                        new_title = info.get("title") or rom_stem
                        rom_name = info.get("rom_name") or rom_stem
                        notes = ex_row.get("notes") or info.get("notes") or ""
                        xml_metadata = json.dumps(info.get("properties", {}), ensure_ascii=False)
                        db.update_game(
                            ex_row["id"],
                            title=new_title,
                            rom_name=rom_name,
                            year=info.get("year", ""),
                            manufacturer=info.get("manufacturer", ""),
                            genre=info.get("genre", ""),
                            players=info.get("players", ""),
                            cloneof=info.get("cloneof", ""),
                            rating=info.get("rating", ""),
                            crc=info.get("crc", ""),
                            notes=notes,
                            xml_metadata=xml_metadata,
                        )
                        xml_matched += 1
                    continue

                if info:
                    title = info.get("title") or rom_stem
                    rom_name = info.get("rom_name") or rom_stem
                    year = info.get("year", "")
                    manufacturer = info.get("manufacturer", "")
                    genre = info.get("genre", "")
                    players = info.get("players", "")
                    cloneof = info.get("cloneof", "")
                    rating = info.get("rating", "")
                    crc = info.get("crc", "")
                    notes = info.get("notes", "")
                    xml_metadata = json.dumps(info.get("properties", {}), ensure_ascii=False)
                    xml_matched += 1
                else:
                    title = rom_stem
                    rom_name = rom_stem
                    year = ""
                    manufacturer = ""
                    genre = ""
                    players = ""
                    cloneof = ""
                    rating = ""
                    crc = ""
                    notes = ""
                    xml_metadata = "{}"

                new_id = db.insert_game(
                    list_id,
                    title=title,
                    rom_path=resolved,
                    rom_name=rom_name,
                    year=year,
                    manufacturer=manufacturer,
                    genre=genre,
                    players=players,
                    cloneof=cloneof,
                    rating=rating,
                    crc=crc,
                    notes=notes,
                    xml_metadata=xml_metadata,
                )
                existing_by_path[resolved_lower] = {"id": new_id, "rom_path": resolved, "notes": notes}
                added += 1
            except Exception:
                skipped += 1

    return {
        "total_found": len(paths),
        "added": added,
        "skipped": skipped,
        "xml_matched": xml_matched,
        "xml_total_entries": len(xml_map),
    }


def add_game(
    db,
    list_id: int,
    path: str | Path,
    title: str | None = None,
    xml_map: dict[str, dict] | None = None,
) -> int | None:
    """
    Agrega un juego individual a una lista dada evitando duplicados.
    Si la lista posee un archivo XML configurado (o se pasa xml_map), asocia
    automáticamente la denominación de la ROM con su nombre completo y propiedades.
    """
    p = Path(path)
    resolved = os.path.abspath(str(p))

    if xml_map is None:
        row_l = db.get_list(list_id)
        if row_l and row_l.get("xml_path"):
            xml_p = Path(row_l["xml_path"])
            if xml_p.is_file():
                try:
                    xml_map = parse_rom_xml(xml_p)
                except Exception:
                    xml_map = None

    info = lookup_xml_for_rom(xml_map, p) if xml_map else None

    existing = db.get_game_by_path(list_id, resolved)
    if existing:
        if info:
            ex_dict = dict(existing)
            new_title = title or info.get("title") or p.stem
            rom_name = info.get("rom_name") or p.stem
            notes = ex_dict.get("notes") or info.get("notes") or ""
            xml_metadata = json.dumps(info.get("properties", {}), ensure_ascii=False)
            db.update_game(
                ex_dict["id"],
                title=new_title,
                rom_name=rom_name,
                year=info.get("year", ""),
                manufacturer=info.get("manufacturer", ""),
                genre=info.get("genre", ""),
                players=info.get("players", ""),
                cloneof=info.get("cloneof", ""),
                rating=info.get("rating", ""),
                crc=info.get("crc", ""),
                notes=notes,
                xml_metadata=xml_metadata,
            )
        return existing["id"]

    if info:
        final_title = title or info.get("title") or p.stem
        rom_name = info.get("rom_name") or p.stem
        year = info.get("year", "")
        manufacturer = info.get("manufacturer", "")
        genre = info.get("genre", "")
        players = info.get("players", "")
        cloneof = info.get("cloneof", "")
        rating = info.get("rating", "")
        crc = info.get("crc", "")
        notes = info.get("notes", "")
        xml_metadata = json.dumps(info.get("properties", {}), ensure_ascii=False)
    else:
        final_title = title or p.stem
        rom_name = p.stem
        year = ""
        manufacturer = ""
        genre = ""
        players = ""
        cloneof = ""
        rating = ""
        crc = ""
        notes = ""
        xml_metadata = "{}"

    return db.insert_game(
        list_id,
        title=final_title,
        rom_path=resolved,
        rom_name=rom_name,
        year=year,
        manufacturer=manufacturer,
        genre=genre,
        players=players,
        cloneof=cloneof,
        rating=rating,
        crc=crc,
        notes=notes,
        xml_metadata=xml_metadata,
    )
