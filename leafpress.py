#!/usr/bin/env python3
"""
LeafPress 1.0 - Compresor de Imágenes (Método PRO)
Para Windows - Compilar con: pyinstaller --onefile leafpress.py
"""

import os
import sys
from pathlib import Path

# Intentar importar Pillow (se instala automáticamente si no existe)
try:
    from PIL import Image
except ImportError:
    print("Instalando Pillow...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "Pillow"])
    from PIL import Image


# ==================== CONFIGURACIÓN ====================

# Detectar si es exe o script
if getattr(sys, 'frozen', False):
    # Es un exe compilado
    INPUT_DIR = os.path.dirname(sys.executable)
else:
    # Es un script Python
    INPUT_DIR = os.path.dirname(os.path.abspath(__file__))

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif', '.bmp', '.tiff'}


# ==================== UTILIDADES ====================

def format_bytes(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1024**2:
        return f"{size/1024:.2f} KB"
    elif size < 1024**3:
        return f"{size/(1024**2):.2f} MB"
    else:
        return f"{size/(1024**3):.2f} GB"


def analyze_image(image, sample_size=5000):
    """Análisis rápido con muestreo - solo procesa 5000 pixels en lugar de millones."""
    gray = image.convert('L')
    pixels = list(gray.getdata())
    
    if len(pixels) < 2:
        return 0.5
    
    # Muestreo: si hay muchos pixels, tomar solo una muestra
    if len(pixels) > sample_size:
        step = len(pixels) // sample_size
        pixels = [pixels[i] for i in range(0, len(pixels), step)][:sample_size]
    
    mean = sum(pixels) / len(pixels)
    variance = sum((p - mean) ** 2 for p in pixels) / len(pixels)
    return min(1.0, variance / 5000)


# ==================== COMPRESOR ====================

def compress_pro(input_path, output_path):
    img = Image.open(input_path)
    
    # 1. Convertir a RGB (manejar transparencias)
    if img.mode != 'RGB':
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[3])
            elif img.mode == 'LA':
                background.paste(img, mask=img.split()[1])
            else:
                background.paste(img)
            img = background
        else:
            img = img.convert('RGB')
    
    # 2. Resize dinámico (max 1920px) - ANTIALIAS es más rápido que LANCZOS
    width, height = img.size
    if max(width, height) > 1920:
        scale = 1920 / max(width, height)
        img = img.resize((int(width*scale), int(height*scale)), Image.Resampling.BILINEAR)
    
    # 3. Calidad adaptativa
    quality = 75
    if analyze_image(img) > 0.5:
        quality = 80
    
    # 4. Sharpen removido - era muy costoso y poco necesario
    # (Si necesitás sharpen, usá webp con libwebp o configurá external)
    
    # 5. Guardar como JPEG - optimize=False para velocidad (ahorra ~30% tiempo)
    img.save(output_path, format='JPEG', quality=quality, optimize=False, subsampling=1)
    return quality


# ==================== MAIN ====================

def main():
    print("======================================")
    print("       LeafPress 1.0 - COMPRESOR")
    print("======================================")
    print()
    
    # Buscar imágenes
    all_files = os.listdir(INPUT_DIR)
    
    files = [f for f in all_files 
             if Path(f).suffix.lower() in IMAGE_EXTENSIONS]
    
    # Filtrar solo archivos existentes (excluir el propio script, exe, bat, txt, spec y archivos ya comprimidos)
    files = [f for f in files if os.path.isfile(os.path.join(INPUT_DIR, f)) 
             and not f.endswith('.py') 
             and not f.endswith('.exe')
             and not f.endswith('.bat')
             and not f.endswith('.txt')
             and not f.endswith('.spec')
             and not '-crp' in f]
    
    if not files:
        print("No se encontraron imagenes en la carpeta.")
        print(f"Archivos en carpeta: {all_files}")
        print("Presiona ENTER para salir...")
        input()
        return
    
    # Calcular peso total original
    total_original = sum(os.path.getsize(os.path.join(INPUT_DIR, f)) for f in files if os.path.isfile(os.path.join(INPUT_DIR, f)))
    
    # MOSTRAR: cantidad de imágenes y peso total
    print(f"Imagenes encontradas: {len(files)}")
    print(f"Peso total: {format_bytes(total_original)}")
    print()
    print("Cargando...")
    print()
    
    # Comprimir cada imagen
    processed = 0
    total_compressed = 0
    
    for filename in files:
        input_path = os.path.join(INPUT_DIR, filename)
        name_without_ext = Path(filename).stem
        output_filename = f"{name_without_ext}-crp.jpg"
        output_path = os.path.join(INPUT_DIR, output_filename)
        
        try:
            compress_pro(input_path, output_path)
            compressed_size = os.path.getsize(output_path)
            total_compressed += compressed_size
            processed += 1
            print(f"  [OK] {filename}")
            
            # Intentar borrar la imagen original
            try:
                os.remove(input_path)
            except OSError:
                pass
                
        except Exception as e:
            print(f"  [ERROR] {filename}: {e}")
    
    # Resumen final
    print()
    print(f"Se procesaron {processed} imagen(es)")
    print("======================================")
    print(f"Peso original:    {format_bytes(total_original)}")
    print(f"Peso comprimido: {format_bytes(total_compressed)}")
    
    if total_original > 0:
        reduction = ((total_original - total_compressed) / total_original * 100)
        print(f"Reduccion:        {reduction:.1f}%")
    
    print("======================================")
    print()
    print("Presiona ENTER para salir...")
    input()


if __name__ == '__main__':
    main()