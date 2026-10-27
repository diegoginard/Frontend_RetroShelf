# Carpetas de Layouts por Sistema en RetroShelf

En esta carpeta podés agregar una subcarpeta para cada sistema emulado con sus recursos visuales (fondos, TV CRT, consolas, mandos, carátulas y scripts de layout).

## Estructura de ejemplo:
```
Layouts/
├── Super Nintendo Entertainment System/
│   ├── bkg.jpg               (Fondo temático principal)
│   ├── tv.png                (Marco de TV CRT para videos)
│   ├── console.png           (Imagen de la consola)
│   ├── console_cover.png     (Tapa/ranura de cartucho)
│   ├── joystick.png          (Control/gamepad)
│   ├── avatar.png            (Decoración/personaje/mascota)
│   ├── logo.png              (Logo oficial de la plataforma)
│   ├── cartart.png           (Plantilla o marco de cartucho)
│   ├── boxart.png            (Plantilla o marco de caja)
│   ├── layout.nut            (Script de Attract-Mode con coordenadas y animaciones)
│   └── pointers/             (Punteros animados de rueda)
│
├── Sega Genesis/
│   └── ...
└── Sony PlayStation/
    └── ...
```

RetroShelf detecta automáticamente cada carpeta dentro de `Layouts/` para que puedas asignarla a tus listas desde el Configurador y disfrutarla en pantalla completa.

## Configuración Autónoma (`theme_layout.py`)
Cada carpeta contiene su propio `theme_layout.py` que administra de manera 100% autónoma sus propios archivos:
```python
# Asignación directa en theme_layout.py:
BKG_IMAGE = "bkg.jpg"
TV_IMAGE = "tv.png"
CONSOLE_IMAGE = "console.png"
AVATAR_IMAGE = "avatar.png"
LOGO_IMAGE = "logo.png"
CARTART_IMAGE = "cartart.png"
BOXART_IMAGE = "boxart.png"
WHEEL_IMAGE = "wheel.png"
POINTER_IMAGE = "pointers/default.png"
FONT_FILES = ["Handel Gothic BT.ttf", "BebasNeue Bold.otf"]

# Ajustes de tamaño y posición:
AVATAR_SCALE = 1.0
AVATAR_X = 0.0
AVATAR_Y = 0.0
```
Para cambiar cualquier fondo, logo, puntero o fuente de un sistema, solo modificás las constantes correspondientes en su propio `theme_layout.py` sin depender de ningún archivo global.
