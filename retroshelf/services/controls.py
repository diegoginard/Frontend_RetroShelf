"""
Módulo de gestión y configuración de controles y teclado de RetroShelf.
Permite asignar teclas personalizadas para navegación, selección y cierre de emuladores,
guardando la configuración en la base de datos de RetroShelf.
"""

from PySide6.QtCore import Qt

# Identificadores de acciones configurables
ACTION_CLOSE_EMULATOR = "close_emulator"
ACTION_NAV_UP = "nav_up"
ACTION_NAV_DOWN = "nav_down"
ACTION_PAGE_UP = "page_up"
ACTION_PAGE_DOWN = "page_down"
ACTION_SELECT = "select_game"
ACTION_MUTE = "mute_video"

# Metadatos de cada acción (nombre para mostrar, descripción y tecla por defecto)
ACTIONS_INFO = [
    {
        "id": ACTION_CLOSE_EMULATOR,
        "name": "Cerrar emulador en ejecución",
        "desc": "Cierra el proceso del emulador activo y restaura el frontend",
        "default": "Escape",
    },
    {
        "id": ACTION_NAV_UP,
        "name": "Subir (Ruleta / Lista)",
        "desc": "Sube un elemento en la ruleta de juegos o en las listas",
        "default": "Up",
    },
    {
        "id": ACTION_NAV_DOWN,
        "name": "Bajar (Ruleta / Lista)",
        "desc": "Baja un elemento en la ruleta de juegos o en las listas",
        "default": "Down",
    },
    {
        "id": ACTION_PAGE_UP,
        "name": "Página / Letra anterior",
        "desc": "Retrocede 5 juegos o salta a la letra anterior",
        "default": "PageUp",
    },
    {
        "id": ACTION_PAGE_DOWN,
        "name": "Página / Letra siguiente",
        "desc": "Avanza 5 juegos o salta a la siguiente letra",
        "default": "PageDown",
    },
    {
        "id": ACTION_SELECT,
        "name": "Seleccionar / Ejecutar juego",
        "desc": "Ejecuta el juego actualmente enfocado",
        "default": "Return",
    },
    {
        "id": ACTION_MUTE,
        "name": "Silenciar / Activar audio video",
        "desc": "Alterna el sonido del video snap en el diseño visual",
        "default": "M",
    },
]

# Mapa de nombres legibles a códigos de teclas virtuales de Windows (VK Codes)
VK_MAP = {
    "Escape": 0x1B,
    "Return": 0x0D,
    "Enter": 0x0D,
    "Space": 0x20,
    "Up": 0x26,
    "Down": 0x28,
    "Left": 0x25,
    "Right": 0x27,
    "PageUp": 0x21,
    "PageDown": 0x22,
    "Home": 0x24,
    "End": 0x23,
    "Tab": 0x09,
    "Backspace": 0x08,
    "Delete": 0x2E,
    "Insert": 0x2D,
    "F1": 0x70,
    "F2": 0x71,
    "F3": 0x72,
    "F4": 0x73,
    "F5": 0x74,
    "F6": 0x75,
    "F7": 0x76,
    "F8": 0x77,
    "F9": 0x78,
    "F10": 0x79,
    "F11": 0x7A,
    "F12": 0x7B,
}

# Mapa de Qt.Key a nombres amigables
QT_TO_NAME = {
    Qt.Key_Escape: "Escape",
    Qt.Key_Return: "Return",
    Qt.Key_Enter: "Return",
    Qt.Key_Space: "Space",
    Qt.Key_Up: "Up",
    Qt.Key_Down: "Down",
    Qt.Key_Left: "Left",
    Qt.Key_Right: "Right",
    Qt.Key_PageUp: "PageUp",
    Qt.Key_PageDown: "PageDown",
    Qt.Key_Home: "Home",
    Qt.Key_End: "End",
    Qt.Key_Tab: "Tab",
    Qt.Key_Backspace: "Backspace",
    Qt.Key_Delete: "Delete",
    Qt.Key_Insert: "Insert",
    Qt.Key_F1: "F1",
    Qt.Key_F2: "F2",
    Qt.Key_F3: "F3",
    Qt.Key_F4: "F4",
    Qt.Key_F5: "F5",
    Qt.Key_F6: "F6",
    Qt.Key_F7: "F7",
    Qt.Key_F8: "F8",
    Qt.Key_F9: "F9",
    Qt.Key_F10: "F10",
    Qt.Key_F11: "F11",
    Qt.Key_F12: "F12",
}

# Mapa de nombres a lista de Qt.Key equivalentes
NAME_TO_QT = {
    "Escape": [Qt.Key_Escape],
    "Return": [Qt.Key_Return, Qt.Key_Enter],
    "Space": [Qt.Key_Space],
    "Up": [Qt.Key_Up],
    "Down": [Qt.Key_Down],
    "Left": [Qt.Key_Left],
    "Right": [Qt.Key_Right],
    "PageUp": [Qt.Key_PageUp],
    "PageDown": [Qt.Key_PageDown],
    "Tab": [Qt.Key_Tab],
}

# Alias secundarios por defecto (por conveniencia de teclado)
ACTION_ALIASES = {
    ACTION_NAV_UP: [Qt.Key_Up, Qt.Key_W, Qt.Key_K],
    ACTION_NAV_DOWN: [Qt.Key_Down, Qt.Key_S, Qt.Key_J],
    ACTION_PAGE_UP: [Qt.Key_PageUp, Qt.Key_Left],
    ACTION_PAGE_DOWN: [Qt.Key_PageDown, Qt.Key_Right],
    ACTION_SELECT: [Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space],
}


def key_name_to_vk(key_name: str) -> int:
    """Convierte un nombre de tecla a su código Virtual Key (VK) de Windows."""
    name = (key_name or "").strip()
    if name in VK_MAP:
        return VK_MAP[name]
    if len(name) == 1:
        ch = name.upper()
        if 'A' <= ch <= 'Z' or '0' <= ch <= '9':
            return ord(ch)
    return 0x1B  # Fallback a VK_ESCAPE


def qt_key_to_name(qt_key: int) -> str:
    """Convierte un código Qt.Key a un nombre de tecla legible."""
    if qt_key in QT_TO_NAME:
        return QT_TO_NAME[qt_key]
    if Qt.Key_A <= qt_key <= Qt.Key_Z:
        return chr(qt_key - Qt.Key_A + ord('A'))
    if Qt.Key_0 <= qt_key <= Qt.Key_9:
        return chr(qt_key - Qt.Key_0 + ord('0'))
    return f"Key_{qt_key}"


def name_to_qt_keys(key_name: str) -> list[int]:
    """Convierte un nombre de tecla a los códigos Qt.Key equivalentes."""
    name = (key_name or "").strip()
    if name in NAME_TO_QT:
        return NAME_TO_QT[name]
    if len(name) == 1:
        ch = name.upper()
        if 'A' <= ch <= 'Z':
            return [Qt.Key_A + (ord(ch) - ord('A'))]
        if '0' <= ch <= '9':
            return [Qt.Key_0 + (ord(ch) - ord('0'))]
    return [Qt.Key_Escape]


def get_binding(db, action: str) -> str:
    """Obtiene el nombre de la tecla configurada para una acción, o su valor predeterminado."""
    default = "Escape"
    for info in ACTIONS_INFO:
        if info["id"] == action:
            default = info["default"]
            break
    if db is None:
        return default
    return db.get_setting(f"control_{action}", default)


def set_binding(db, action: str, key_name: str):
    """Guarda una asignación de tecla en la base de datos."""
    if db:
        db.set_setting(f"control_{action}", key_name.strip())


def reset_default_bindings(db):
    """Restablece todas las teclas a sus valores predeterminados."""
    if db:
        for info in ACTIONS_INFO:
            db.set_setting(f"control_{info['id']}", info["default"])


def get_all_bindings(db) -> list[dict]:
    """Retorna una lista con la información completa y tecla actual de cada acción."""
    result = []
    for info in ACTIONS_INFO:
        current_key = get_binding(db, info["id"])
        result.append({
            "id": info["id"],
            "name": info["name"],
            "desc": info["desc"],
            "key": current_key,
            "default": info["default"],
        })
    return result


def matches_action(event_key: int, action: str, db=None) -> bool:
    """
    Verifica si la tecla presionada (código Qt.Key) coincide con la tecla asignada
    para una acción, incluyendo alias estándar si la tecla es la predeterminada.
    """
    assigned = get_binding(db, action)
    target_keys = name_to_qt_keys(assigned)
    if event_key in target_keys:
        return True

    # Si la acción está en su valor predeterminado, admitir también alias secundarios estándar
    default = next((info["default"] for info in ACTIONS_INFO if info["id"] == action), "")
    if assigned == default and action in ACTION_ALIASES:
        if event_key in ACTION_ALIASES[action]:
            return True

    return False
