"""
SINAVE ETVs Downloader
Herramienta para descargar automáticamente bases de datos del SINAVE
(Enfermedades Transmitidas por Vectores)
"""

import os
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# Enfermedades disponibles
ENFERMEDADES_DISPONIBLES = [
    "RICKETT", "CHAGAS", "FIEBRE_NILO", "LEISHMAN", 
    "ENCEFALITIS", "FIEBREMAYARO", "FIEBREAMARILLA", 
    "PALUDISMO", "ZIKA", "CHIKUNGUNYA", "DENGUE"
]

def sinave_etvs(user, password, output_folder=None, download_single=None):
    """
    Descarga bases de datos del SINAVE - Enfermedades Transmitidas por Vectores
    
    Parámetros:
    -----------
    user : str
        Usuario para acceder al SINAVE
    password : str
        Contraseña para acceder al SINAVE
    output_folder : str, optional
        Ruta de la carpeta donde guardar los archivos descargados.
        Por defecto: Desktop/SINAVE_Bases
    download_single : str, optional
        Nombre de una enfermedad específica para descargar (ej: "DENGUE", "ZIKA").
        Si es None, descarga todas las enfermedades disponibles.
    
    Returns:
    --------
    dict
        Diccionario con resultados de la descarga
    """
    
    # Configuración
    SINAVE_URL = "https://vectores.sinave.gob.mx"
    
    # Definir carpeta de destino
    if output_folder is None:
        DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "SINAVE_Bases")
    else:
        DESKTOP_PATH = output_folder
        if not os.path.exists(DESKTOP_PATH):
            os.makedirs(DESKTOP_PATH)
    
    # Filtrar enfermedades según parámetro
    if download_single:
        download_single_upper = download_single.upper()
        if download_single_upper in ENFERMEDADES_DISPONIBLES:
            ENFERMEDADES = [download_single_upper]
            print(f"🎯 Modo descarga única: {download_single_upper}")
        else:
            print(f"⚠️ '{download_single}' no es válido. Opciones: {', '.join(ENFERMEDADES_DISPONIBLES)}")
            return {"error": "Enfermedad no válida", "exitosas": [], "fallidas": []}
    else:
        ENFERMEDADES = ENFERMEDADES_DISPONIBLES.copy()
        print(f"🎯 Modo descarga completa: {len(ENFERMEDADES)} enfermedades")
    
    def configurar_driver():
        """Configura el driver de Chrome en modo headless"""
        chrome_options = Options()
        
        # Modo headless
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Preferencias de descarga
        prefs = {
            "download.default_directory": DESKTOP_PATH,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": DESKTOP_PATH
        })
        
        return driver
    
    def login(driver):
        """Realiza el login en SINAVE"""
        print("\n🔐 Iniciando sesión...")
        
        driver.get(SINAVE_URL)
        wait = WebDriverWait(driver, 25)
        time.sleep(3)
        
        # Buscar campos (código simplificado)
        try:
            usuario_field = wait.until(EC.presence_of_element_located(
                (By.NAME, "ctl00$cphContent$Login1$UserName")
            ))
            password_field = wait.until(EC.presence_of_element_located(
                (By.NAME, "ctl00$cphContent$Login1$Password")
            ))
            
            usuario_field.clear()
            usuario_field.send_keys(user)
            password_field.clear()
            password_field.send_keys(password)
            
            login_button = wait.until(EC.element_to_be_clickable(
                (By.ID, "ctl00_cphContent_Login1_LoginButton")
            ))
            driver.execute_script("arguments[0].click();", login_button)
            
            time.sleep(5)
            
            if "login" in driver.current_url.lower():
                print("❌ Error de autenticación")
                return False
            
            print("✅ Login exitoso")
            return True
            
        except Exception as e:
            print(f"❌ Error en login: {e}")
            return False
    
    def descargar_archivos(driver):
        """Descarga los archivos de enfermedades"""
        url_descarga = "https://vectores.sinave.gob.mx/Reportes/descargaEdo.aspx?estado=99"
        driver.get(url_descarga)
        time.sleep(5)
        
        archivos_descargables = []
        
        try:
            # Buscar tabla y enlaces
            tabla = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder2_gvDescarga"))
            )
            enlaces = tabla.find_elements(By.TAG_NAME, "a")
            
            for enlace in enlaces:
                texto = enlace.text.strip()
                if texto and '.rar' in texto.lower():
                    for enfermedad in ENFERMEDADES:
                        if enfermedad.lower() in texto.lower():
                            archivos_descargables.append({
                                'enlace': enlace,
                                'texto': texto,
                                'enfermedad': enfermedad
                            })
                            print(f"  ✓ Encontrado: {texto}")
                            break
            
            # Descargar archivos
            exitosas = []
            fallidas = []
            
            for i, archivo in enumerate(archivos_descargables, 1):
                print(f"\n📥 [{i}/{len(archivos_descargables)}] Descargando {archivo['enfermedad']}...")
                
                try:
                    archivos_antes = set(os.listdir(DESKTOP_PATH))
                    driver.execute_script("arguments[0].click();", archivo['enlace'])
                    
                    # Esperar descarga
                    time.sleep(10)
                    archivos_despues = set(os.listdir(DESKTOP_PATH))
                    nuevos = archivos_despues - archivos_antes
                    
                    if nuevos:
                        exitosas.append(archivo['texto'])
                        print(f"   ✅ Completado: {list(nuevos)[0]}")
                    else:
                        fallidas.append(archivo['texto'])
                        print(f"   ❌ Falló la descarga")
                    
                    # Regresar a página de descargas
                    driver.get(url_descarga)
                    time.sleep(3)
                    
                except Exception as e:
                    fallidas.append(archivo['texto'])
                    print(f"   ❌ Error: {e}")
            
            return exitosas, fallidas
            
        except Exception as e:
            print(f"❌ Error buscando archivos: {e}")
            return [], []
    
    def generar_reporte(exitosas, fallidas):
        """Genera reporte final"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        reporte = f"""
{'='*60}
REPORTE DE DESCARGA - SINAVE ETVs
{'='*60}
Fecha: {timestamp}
Ubicación: {DESKTOP_PATH}
Exitosas: {len(exitosas)}
Fallidas: {len(fallidas)}

EXITOSAS:
{chr(10).join(f'  ✅ {b}' for b in exitosas) if exitosas else '  Ninguna'}

FALLIDAS:
{chr(10).join(f'  ❌ {b}' for b in fallidas) if fallidas else '  Ninguna'}
{'='*60}
"""
        
        reporte_path = os.path.join(DESKTOP_PATH, f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(reporte_path, 'w', encoding='utf-8') as f:
            f.write(reporte)
        
        print(reporte)
        return reporte_path
    
    # Ejecución principal
    driver = None
    try:
        print("""
╔═══════════════════════════════════════════════════════════╗
║     SINAVE ETVs Downloader                               ║
║     Enfermedades Transmitidas por Vectores               ║
╚═══════════════════════════════════════════════════════════╝
        """)
        
        driver = configurar_driver()
        
        if login(driver):
            exitosas, fallidas = descargar_archivos(driver)
            generar_reporte(exitosas, fallidas)
            
            print(f"\n🎉 Proceso completado!")
            print(f"📁 Archivos en: {DESKTOP_PATH}")
            
            return {"exitosas": exitosas, "fallidas": fallidas, "carpeta": DESKTOP_PATH}
        else:
            return {"error": "Login fallido", "exitosas": [], "fallidas": []}
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "exitosas": [], "fallidas": []}
        
    finally:
        if driver:
            driver.quit()


# Ejemplo de uso
if __name__ == "__main__":
    # Reemplazar con tus credenciales
    USUARIO = "tu_usuario"
    CONTRASENA = "tu_contraseña"
    
    # Ejemplos:
    # sinave_etvs(USUARIO, CONTRASENA)  # Todas las bases
    # sinave_etvs(USUARIO, CONTRASENA, download_single="DENGUE")  # Solo Dengue
    # sinave_etvs(USUARIO, CONTRASENA, output_folder="C:/MisBases")  # Carpeta personalizada
    
    resultado = sinave_etvs(USUARIO, CONTRASENA)
    print(f"\nResultado: {resultado}")