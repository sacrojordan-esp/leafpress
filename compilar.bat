@echo off
chcp 65001 >nul
title Compilador - LeafPress

echo.
echo ======================================
echo    Compilando LeafPress 1.0...
echo ======================================
echo.

REM Verificar Python
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no instalado.
    echo Descargalo de: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/4] Instalando dependencias...
py -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al instalar dependencias
    pause
    exit /b 1
)

echo [2/4] Instalando PyInstaller...
py -m pip install pyinstaller
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al instalar PyInstaller
    pause
    exit /b 1
)

echo [3/4] Verificando PyInstaller...
py -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller no se instalo correctamente
    echo Intenta: py -m pip install pyinstaller
    pause
    exit /b 1
)

echo [4/4] Compilando ejecutable...
py -m PyInstaller --onefile --noconfirm --name leafpress --icon=icono.ico leafpress.py
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al compilar
    pause
    exit /b 1
)

echo.
echo Verificando executable existente...
if exist "leafpress.exe" (
    echo El archivo leafpress.exe existe.
    echo Intentando reemplazar...
    
    REM Intentar borrar el archivo existente
    del /f "leafpress.exe" 2>nul
    
    REM Si no se pudo borrar, esta en uso
    if exist "leafpress.exe" (
        echo.
        echo [ADVERTENCIA] No se puede reemplazar leafpress.exe
        echo Es probable que este abierto o en uso.
        echo.
        echo Por favor, cierra el programa si esta ejecutandose.
        echo.
        echo Archivo compilado disponible en: dist\leafpress.exe
        echo Puedes copiarlo manualmente despues.
        echo.
        pause
        exit /b 1
    )
)

echo Copiando executable...
if exist "dist\leafpress.exe" (
    copy "dist\leafpress.exe" ".\"
    echo.
    echo ======================================
    echo [OK] Compilacion exitosa!
    echo ======================================
    echo.
    echo Archivo creado: leafpress.exe
    echo.
) else (
    echo [ERROR] No se genero el .exe
    pause
    exit /b 1
)

REM Limpiar carpeta
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "leafpress.spec" del /q leafpress.spec
if exist "__pycache__" rmdir /s /q __pycache__

echo Presiona ENTER para salir...
pause