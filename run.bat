@echo off
cd /d "%~dp0"

echo ===================================================
echo             RetroShelf - Launcher
echo ===================================================
echo.
echo Selecciona el modo que deseas iniciar:
echo.
echo  [1] Iniciar Frontend de Juegos (Jugar)
echo  [2] Abrir Configurador (Listas, Emuladores, Layouts)
echo.
set /p opt="Opcion (1 o 2, por defecto 1): "

if "%opt%"=="2" (
    call configurador.bat
) else (
    call jugar.bat
)
