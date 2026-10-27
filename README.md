# RetroShelf — Frontend de Emulación para Windows

Frontend modular, rápido y elegante para organizar, visualizar y ejecutar videojuegos retro mediante emuladores en Windows 10 y Windows 11. Desarrollado con **Python 3.11+**, **PySide6** y **SQLite**.

---

## 🚀 Guía de inicio rápido: Cómo crear el entorno

RetroShelf incluye un script automatizado (`run.bat`) que detecta Python, crea el entorno virtual e instala las dependencias por vos. Si preferís hacerlo manualmente, seguí los pasos detallados a continuación:

### Lanzadores rápidos incluidos:
- **`jugar.bat`**: Inicia el **Modo Frontend / Reproductor**, una interfaz limpia de pantalla completa pensada exclusivamente para jugar, sin menús de configuración técnica.
- **`configurador.bat`**: Abre el **Configurador**, donde podés crear listas, seleccionar carpetas de ROMs, registrar emuladores y asignar layouts.
- **`run.bat`**: Menú interactivo que te permite elegir entre iniciar el Modo Frontend o el Configurador.

Ambos scripts crean automáticamente el entorno virtual `.venv` e instalan las dependencias si no existen en tu equipo.

---

### Método Manual (PowerShell o CMD)
1. **Crear y activar el entorno virtual:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. **Ejecutar en modo Configurador:**
   ```bash
   python -m retroshelf
   ```
3. **Ejecutar en modo Frontend / Jugador:**
   ```bash
   python -m retroshelf --player
   ```

---

## 📋 Características principales

### 1. Biblioteca por Listas y Plataformas
- Creación, edición y eliminación de listas dedicadas para cada consola o colección.
- **Selección de carpeta de juegos al crear la lista:** Al dar de alta o editar una lista, contás con un campo y botón «Examinar…» para indicar la carpeta donde están almacenadas las ROMs.
- **Escaneo e importación automática:** Si definís una carpeta al crear la lista, RetroShelf te ofrece escanearla e importar los juegos de forma inmediata al pulsar «Guardar».
- Cada lista almacena de forma independiente su nombre, plataforma, carpeta de juegos asociada, emulador predeterminado, diseño visual y extensiones permitidas.
- Eliminar o modificar una lista nunca altera la configuración de las demás ni borra archivos del disco.


### 2. Configuración manual de extensiones por lista
- **Campo de texto dedicado:** El usuario escribe manualmente las extensiones admitidas.
- **Separador estricto por punto y coma (`;`):**
  - Ejemplo: `.cue;.bin;.chd;.iso`
  - GBA: `.gba;.zip;.7z`
  - SNES: `.sfc;.smc;.zip`
- **Normalización automática:**
  - Acepta extensiones con o sin punto inicial (`sfc` o `.sfc`).
  - Limpia espacios en blanco alrededor de cada extensión.
  - Convierte automáticamente a minúsculas (`.ISO` $\rightarrow$ `.iso`).
  - Elimina duplicados conservando el orden ingresado.
  - Valida el formato y prohíbe el uso de comas (`,`) como separador.
  - Advierte al usuario si se especifica la extensión genérica `.bin` (frecuente en pistas secundarias de discos).
- **Escaneo recursivo:** RetroShelf busca en todas las subcarpetas del directorio seleccionado, compara únicamente contra las extensiones de la lista actual, ignora las no configuradas y evita duplicar juegos ya presentes en la biblioteca.
- **Resumen de escaneo:** Al finalizar la exploración se muestra una ventana detallada con archivos encontrados, juegos agregados y omitidos.

### 3. Gestión y registro de emuladores
- Administrador visual accesible desde **⚙ Administrar emuladores**:
  - Registro, edición y eliminación de emuladores.
  - Selector de archivos nativo de Windows para ubicar el ejecutable (`.exe`).
  - Plantilla de argumentos personalizable:
    - `{rom}`: Ruta completa al archivo del juego.
    - `{rom_dir}`: Carpeta donde se aloja el juego.
    - `{rom_name}`: Nombre del archivo sin extensión.
  - Sin rutas fijas ni dependencias de instalación rígidas.

### 4. Prioridad de ejecución
Al lanzar un juego (haciendo doble clic o presionando **▶ EJECUTAR JUEGO**):
1. **Prioridad 1:** Emulador asignado individualmente al juego (sobrescritura).
2. **Prioridad 2:** Emulador predeterminado de la lista.
3. Si ninguno está asignado, RetroShelf guía al usuario para que configure uno.

### 5. Sistema de Layouts Personalizados, Modulares y Temáticos por Sistema
RetroShelf cuenta con un motor desacoplado de layouts (`retroshelf/ui/layouts/`) y soporte para temas dedicados por consola:
- **Carpeta `Layouts/`:** Podés agregar una subcarpeta para cada sistema emulado (por ejemplo `Layouts/Super Nintendo Entertainment System/`) con sus elementos visuales (fondo `bkg.jpg`, TV CRT `tv.png`, consola `console.png`, controles, carátula, cartucho y logos). RetroShelf los detecta y renderiza automáticamente.
- **Grid (Estantería / Cuadrícula):** Tarjetas visuales de juegos con distintivos de formato y **control deslizante de zoom en vivo** para ajustar el tamaño de las tarjetas a gusto.
- **Showcase (Modo Cinemático / Big Screen):** Inspirado en consolas modernas. Gran banner superior con tipografía destacada, datos técnicos, botón «JUGAR AHORA» y carrusel inferior de selección rápida.
- **Wheel (Rueda Clásica):** Rueda arcade interactiva con logos transparentes (`wheel`) y video snaps.
- **Banners (Tarjetas Horizontales):** Filas amplias estilo LaunchBox / Steam con resumen visual y detalles técnicos.
- **Detalles (Tabla Técnica):** Vista completa y ordenable por columnas (Título, Archivo, Formato, Tamaño, Emulador efectivo).
- **Personalización por Lista:** Cada lista recuerda de forma independiente su layout preferido en SQLite (`game_lists.layout`).

### 6. Configuración de Video y Resoluciones
Desde el botón **🖥 Configuración de video** en la barra de herramientas del Configurador podés definir cómo se visualizará el Frontend:
- **Modos de pantalla:**
  - *Pantalla completa (Fullscreen):* Ocupa todo el monitor (ideal para gabinetes arcade y TVs).
  - *Ventana sin bordes (Borderless):* Se expande al tamaño del monitor sin marcos de ventana.
  - *Modo Ventana (Windowed):* Ventana centrada y redimensionable.
- **Resoluciones compatibles:** 4K UHD (3840x2160), 2K QHD (2560x1440), Full HD (1920x1080), 1600x900, 1366x768, 720p (1280x720), 16:10 (1920x1200, 1680x1050, 1280x800), 4:3 (1024x768, 800x600, 640x480), resolución nativa automática o personalización exacta en píxeles.
- **Soporte multi-monitor:** Selección del monitor específico donde se abrirá el Frontend.
- **Escala de interfaz (UI Scale):** 100%, 125%, 150%, 175% y 200%.

---


## 🗂 Estructura del proyecto

```text
RetroShelf/
├── README.md                 # Documentación técnica y de usuario
├── requirements.txt          # Dependencias (PySide6)
├── run.bat                   # Menú selector interactivo
├── configurador.bat          # Lanzador directo del Modo Configurador
├── jugar.bat                 # Lanzador directo del Modo Frontend / Jugador
└── retroshelf/
    ├── __init__.py
    ├── __main__.py           # Enrutador principal (--player o configurador)
    ├── db.py                 # Capa de base de datos SQLite y migraciones
    ├── services/
    │   ├── __init__.py
    │   ├── launcher.py       # Resolución de prioridades y ejecución de emuladores
    │   └── library.py        # Normalización de extensiones y escaneo de ROMs
    └── ui/
        ├── __init__.py
        ├── dialogs.py        # Diálogos: Listas, Emuladores, Resumen de Escaneo, Edición
        ├── cover_utils.py    # Generador procedural de carátulas dinámicas y carga de arte
        ├── main_window.py    # Ventana del Configurador (gestión de listas y emuladores)
        ├── player_window.py  # Ventana del Frontend / Jugador (interfaz limpia, pantalla completa)
        └── layouts/          # Motor de layouts personalizados
            ├── __init__.py   # Registro y fábrica de layouts
            ├── base.py       # Clase base abstracta BaseLayout
            ├── grid_layout.py      # Cuadrícula con zoom regulable y carátulas
            ├── showcase_layout.py  # Modo Cinemático / Showcase con carrusel
            ├── banner_layout.py    # Modo Banners horizontales estilo Steam
            └── table_layout.py     # Modo Tabla técnica de detalles
```


---

## 💾 Persistencia de datos

La base de datos SQLite se almacena en:
`%APPDATA%\RetroShelf\data\retroshelf.db`

La aplicación incluye un sistema de migración que actualiza el esquema automáticamente preservando todas las listas y juegos creados con anterioridad.
