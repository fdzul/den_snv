
# ============= IMPORTACION DE MODULOS =============
import os
import time
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
import re
# ============= CONFIGURACIÓN =============
SINAVE_URL = "https://vectores.sinave.gob.mx"
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "SINAVE_Bases")

# ============= USER & PASSWORD =============
USUARIO = user
PASSWORD = password

# ============= BASES DEL SINAVE =============
ENFERMEDADES = ["RICKETT", "CHAGAS", "FIEBRE_NILO", "LEISHMAN", 
                "ENCEFALITIS", "FIEBREMAYARO", "FIEBREAMARILLA", 
                "PALUDISMO", "ZIKA", "CHIKUNGUNYA", "DENGUE"]

# ============= CONFIGURAR EL DRIVER =============
def configurar_driver():
    """Configura el driver de Chrome en modo headless"""
    
    # Crear carpeta de destino si no existe
    if not os.path.exists(DESKTOP_PATH):
        os.makedirs(DESKTOP_PATH)
    
    chrome_options = Options()
    
    # MODO HEADLESS - Sin ventanas visibles
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--remote-debugging-port=0")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    
    # Configurar preferencias de descarga para headless
    prefs = {
        "download.default_directory": DESKTOP_PATH,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "safebrowsing.disable_download_protection": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 2,  # Permitir imágenes
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Silenciar logs innecesarios
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Configurar comportamiento de descarga para headless
        driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": DESKTOP_PATH
        })
        
        return driver
    except Exception as e:
        print(f"❌ Error al configurar Chrome en modo headless: {e}")
        raise

# ============= LOGIN SINAVE =============
def login_sinave(driver, usuario, password):
    """Realiza el login en el sistema SINAVE en modo headless"""
    print("\n📝 Paso 1: Accediendo a SINAVE (modo headless)...")
    
    try:
        driver.get(SINAVE_URL)
        wait = WebDriverWait(driver, 25)  # Mayor tiempo de espera para headless
        
        print("⏳ Esperando que cargue la página de login...")
        time.sleep(3)
        
        # Tomar screenshot para debug (útil en headless)
        #driver.save_screenshot(os.path.join(DESKTOP_PATH, "01_pagina_login.png"))
        
        print("🔐 Paso 2: Ingresando credenciales...")
        
        # Campo de usuario
        usuario_field = None
        selectores_usuario = [
            (By.NAME, "ctl00$cphContent$Login1$UserName"),
            (By.ID, "ctl00_cphContent_Login1_UserName"),
            (By.XPATH, "//input[@type='text' and contains(@name, 'UserName')]"),
            (By.XPATH, "//input[contains(@id, 'UserName')]")
        ]
        
        for by, selector in selectores_usuario:
            try:
                usuario_field = wait.until(EC.presence_of_element_located((by, selector)))
                print(f"✓ Campo usuario encontrado: {selector}")
                break
            except TimeoutException:
                continue
        
        if not usuario_field:
            print("❌ No se encontro el campo de usuario")
            driver.save_screenshot(os.path.join(DESKTOP_PATH, "error_campo_usuario.png"))
            return False
        
        # Campo de contraseña
        password_field = None
        selectores_password = [
            (By.NAME, "ctl00$cphContent$Login1$Password"),
            (By.ID, "ctl00_cphContent_Login1_Password"),
            (By.XPATH, "//input[@type='password' and contains(@name, 'Password')]"),
            (By.XPATH, "//input[contains(@id, 'Password')]")
        ]
        
        for by, selector in selectores_password:
            try:
                password_field = wait.until(EC.presence_of_element_located((by, selector)))
                print(f"✓ Campo contraseña encontrado: {selector}")
                break
            except TimeoutException:
                continue
        
        if not password_field:
            print("❌ No se encontró el campo de contraseña")
            driver.save_screenshot(os.path.join(DESKTOP_PATH, "error_campo_password.png"))
            return False
        
        # Ingresar credenciales
        print("📝 Ingresando credenciales...")
        usuario_field.clear()
        usuario_field.send_keys(usuario)
        time.sleep(1)
        
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)
        
        # Botón de login
        login_button = None
        selectores_button = [
            (By.NAME, "ctl00$cphContent$Login1$LoginButton"),
            (By.ID, "ctl00_cphContent_Login1_LoginButton"),
            (By.XPATH, "//input[@type='submit' and contains(@value, 'Iniciar')]"),
            (By.XPATH, "//input[contains(@value, 'Login') or contains(@value, 'Entrar')]")
        ]
        
        for by, selector in selectores_button:
            try:
                login_button = wait.until(EC.element_to_be_clickable((by, selector)))
                print(f"✓ Botón login encontrado: {selector}")
                break
            except:
                continue
        
        if not login_button:
            print("❌ No se encontro el botón de login")
            driver.save_screenshot(os.path.join(DESKTOP_PATH, "error_boton_login.png"))
            return False
        
        # Tomar screenshot antes del login
        #driver.save_screenshot(os.path.join(DESKTOP_PATH, "02_antes_login.png"))
        
        # Hacer click en el botón de login usando JavaScript (más confiable en headless)
        print("🚀 Enviando formulario de login...")
        driver.execute_script("arguments[0].click();", login_button)
        
        # Esperar a que procese el login
        print("⏳ Procesando login...")
        time.sleep(8)  # Más tiempo para procesar en headless
        
        # Tomar screenshot después del login
        #driver.save_screenshot(os.path.join(DESKTOP_PATH, "03_despues_login.png"))
        
        # Verificar si el login fue exitoso
        current_url = driver.current_url
        page_title = driver.title.lower()
        page_source = driver.page_source.lower()
        
        # Indicadores de login fallido
        login_failed_indicators = [
            "login" in current_url.lower(),
            "error" in page_source,
            "invalid" in page_source,
            "incorrect" in page_source,
            "ctl00_cphcontent_login1" in page_source  # Si sigue en página de login
        ]
        
        if any(login_failed_indicators):
            print("❌ Login fallo - aún en página de login o hay errores")
            driver.save_screenshot(os.path.join(DESKTOP_PATH, "error_login_fallido.png"))
            return False
        
        print("✅ Login exitoso")
        print(f"📍 URL actual: {current_url}")
        return True
        
    except Exception as e:
        print(f"❌ Error en login: {str(e)}")
        driver.save_screenshot(os.path.join(DESKTOP_PATH, "error_login_general.png"))
        return False
# ============= ENTRAR EN LA PAGINA DE DESCARGAS =============
def descargar_directamente(driver):
    """Navega directamente a la pagina de descarga y descarga los archivos en headless"""
    
    print("\n🚀 Navegando directamente a la pagina de descarga...")
    
    # URL directa de descarga
    url_descarga = "https://vectores.sinave.gob.mx/Reportes/descargaEdo.aspx?estado=99"
    
    try:
        driver.get(url_descarga)
        wait = WebDriverWait(driver, 30)  # Más tiempo para headless
        
        print("⏳ Esperando que cargue la página de descarga...")
        time.sleep(5)
        
        # Tomar screenshot de la página de descarga
        driver.save_screenshot(os.path.join(DESKTOP_PATH, "04_pagina_descarga.png"))
        
        print("🔍 Buscando tabla de archivos...")
        
        # Buscar la tabla que contiene los archivos
        tabla = None
        selectores_tabla = [
            (By.ID, "ctl00_ContentPlaceHolder2_gvDescarga"),
            (By.CLASS_NAME, "mGrid"),
            (By.XPATH, "//table[contains(@class, 'grid')]"),
            (By.TAG_NAME, "table")
        ]
        
        for by, selector in selectores_tabla:
            try:
                tabla = wait.until(EC.presence_of_element_located((by, selector)))
                print(f"✓ Tabla encontrada: {selector}")
                break
            except:
                continue
        
        if not tabla:
            print("❌ No se encontro la tabla de archivos")
            # Guardar el HTML para debug
            with open(os.path.join(DESKTOP_PATH, "debug_page_source.html"), "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return [], []
        
        # Buscar todos los enlaces de descarga
        print("📥 Buscando enlaces de descarga...")
        
        # Buscar enlaces dentro de la tabla
        enlaces = tabla.find_elements(By.TAG_NAME, "a")
        print(f"✓ Se encontraron {len(enlaces)} enlaces en la tabla")
        
        # Si no hay enlaces en la tabla, buscar en toda la página
        if len(enlaces) == 0:
            print("⚠ No hay enlaces en la tabla, buscando en toda la página...")
            enlaces = driver.find_elements(By.TAG_NAME, "a")
            print(f"✓ Se encontraron {len(enlaces)} enlaces en total")
        
        # Filtrar solo los enlaces que contengan las enfermedades que nos interesan
        archivos_descargables = []
        
        for enlace in enlaces:
            try:
                texto = enlace.text.strip()
                href = enlace.get_attribute('href') or ''
                
                # Verificar si es un archivo RAR de una de nuestras enfermedades
                if texto and '.rar' in texto.lower():
                    # Verificar si coincide con alguna de nuestras enfermedades
                    for enfermedad in ENFERMEDADES:
                        if enfermedad.lower() in texto.lower():
                            archivos_descargables.append({
                                'enlace': enlace,
                                'texto': texto,
                                'href': href,
                                'enfermedad': enfermedad
                            })
                            print(f"  ✓ Archivo encontrado: {texto}")
                            break
            except Exception as e:
                continue
        
        print(f"\n📊 Total de archivos identificados: {len(archivos_descargables)}")
        
        if len(archivos_descargables) == 0:
            print("❌ No se encontraron archivos para descargar")
            # Guardar lista de todos los enlaces para debug
            with open(os.path.join(DESKTOP_PATH, "debug_enlaces.txt"), "w", encoding="utf-8") as f:
                for i, enlace in enumerate(enlaces):
                    try:
                        texto = enlace.text.strip()
                        href = enlace.get_attribute('href') or ''
                        f.write(f"{i+1}. Texto: '{texto}' | Href: '{href}'\n")
                    except:
                        f.write(f"{i+1}. [Error al obtener información]\n")
            return [], []
        
        # Seleccionar solo los archivos más recientes de cada enfermedad
        archivos_filtrados = filtrar_archivos_recientes(archivos_descargables)
        
        # Descargar los archivos seleccionados
        return descargar_archivos_seleccionados(driver, archivos_filtrados)
        
    except Exception as e:
        print(f"❌ Error en descarga directa: {str(e)}")
        driver.save_screenshot(os.path.join(DESKTOP_PATH, "error_descarga_directa.png"))
        return [], []
# ============= SELECCIONAMOS LAS BASES MAS RECIENTES =============
def filtrar_archivos_recientes(archivos_descargables):
    """Filtra los archivos más recientes de cada enfermedad"""
    
    archivos_por_enfermedad = {}
    
    for archivo in archivos_descargables:
        try:
            texto = archivo['texto']
            enfermedad = archivo['enfermedad']
            
            # Extraer fecha (ej: "19-11-2025")
            fecha_match = re.search(r'(\d{2})-(\d{2})-(\d{4})', texto)
            if fecha_match:
                dia, mes, anio = fecha_match.groups()
                fecha_comparable = f"{anio}{mes}{dia}"  # Formato para comparación
                
                # Si es la primera vez que vemos esta enfermedad o encontramos una fecha más reciente
                if enfermedad not in archivos_por_enfermedad:
                    archivos_por_enfermedad[enfermedad] = archivo
                    archivos_por_enfermedad[enfermedad]['fecha'] = fecha_comparable
                else:
                    # Comparar fechas y quedarnos con la más reciente
                    if fecha_comparable > archivos_por_enfermedad[enfermedad]['fecha']:
                        archivos_por_enfermedad[enfermedad] = archivo
                        archivos_por_enfermedad[enfermedad]['fecha'] = fecha_comparable
            else:
                # Si no tiene fecha, lo agregamos de todas formas
                if enfermedad not in archivos_por_enfermedad:
                    archivos_por_enfermedad[enfermedad] = archivo
                    archivos_por_enfermedad[enfermedad]['fecha'] = "00000000"
                        
        except Exception as e:
            print(f"⚠ Error procesando archivo {archivo['texto']}: {str(e)}")
            continue
    
    print(f"\n🎯 Archivos más recientes a descargar ({len(archivos_por_enfermedad)}):")
    for enfermedad, archivo in archivos_por_enfermedad.items():
        print(f"  • {enfermedad}: {archivo['texto']}")
    
    return list(archivos_por_enfermedad.values())
# ============= BAJAMOS LAS BASES =============
def descargar_archivos_seleccionados(driver, archivos_filtrados):
    """Descarga los archivos seleccionados en modo headless"""
    
    bases_exitosas = []
    bases_fallidas = []
    
    total_archivos = len(archivos_filtrados)
    
    if total_archivos == 0:
        print("❌ No se encontraron archivos para descargar")
        return [], []
    
    print(f"\n🚀 Iniciando descarga de {total_archivos} archivos en modo headless...")
    
    for i, archivo in enumerate(archivos_filtrados, 1):
        nombre_archivo = archivo['texto']
        enlace = archivo['enlace']
        enfermedad = archivo['enfermedad']
        href = archivo['href']
        
        print(f"\n{'='*50}")
        print(f"[{i}/{total_archivos}] Descargando: {enfermedad}")
        print(f"Archivo: {nombre_archivo}")
        print(f"{'='*50}")
        
        try:
            # Contar archivos antes de la descarga
            archivos_antes = set(os.listdir(DESKTOP_PATH))
            
            # Método 1: Navegar directamente al href (más confiable en headless)
            if href and 'Archivo.aspx' in href:
                print("   📥 Navegando directamente a la URL de descarga...")
                driver.get(href)
                time.sleep(3)
            else:
                # Método 2: Hacer click en el enlace
                print("   🖱️ Haciendo click en el enlace...")
                driver.execute_script("arguments[0].scrollIntoView(true);", enlace)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", enlace)
            
            # Esperar a que se complete la descarga
            if esperar_descarga_completa(archivos_antes, nombre_archivo):
                bases_exitosas.append(nombre_archivo)
                print(f"   ✅ Descarga completada: {nombre_archivo}")
            else:
                bases_fallidas.append(nombre_archivo)
                print(f"   ❌ Error en descarga: {nombre_archivo}")
            
            # Volver a la página de descargas si es necesario
            if i < total_archivos:
                print("   🔄 Volviendo a la pagina de descargas...")
                driver.get("https://vectores.sinave.gob.mx/Reportes/descargaEdo.aspx?estado=99")
                time.sleep(3)
            
            # Pausa entre descargas
            time.sleep(2)
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            bases_fallidas.append(nombre_archivo)
    
    return bases_exitosas, bases_fallidas
def esperar_descarga_completa(archivos_antes, nombre_esperado, timeout=45):
    """Espera a que se complete una descarga en modo headless"""
    
    print("   ⏳ Esperando que se complete la descarga...")
    
    for intento in range(timeout):
        time.sleep(2)  # Mayor tiempo entre verificaciones en headless
        
        archivos_despues = set(os.listdir(DESKTOP_PATH))
        nuevos_archivos = archivos_despues - archivos_antes
        
        # Verificar si el archivo esperado fue descargado
        for archivo in nuevos_archivos:
            if nombre_esperado in archivo:
                if not archivo.endswith('.crdownload') and not archivo.endswith('.tmp'):
                    return True
                else:
                    print(f"   ... descarga en progreso ({intento*2}s)")
        
        # Verificar si hay archivos temporales de descarga
        descarga_activa = any(
            archivo.endswith('.crdownload') or archivo.endswith('.tmp') 
            for archivo in archivos_despues
        )
        
        if not descarga_activa and intento > 2 and nuevos_archivos:
            # Si no hay descarga activa después de unos segundos y hay nuevos archivos
            archivo_descargado = list(nuevos_archivos)[0]
            print(f"   ⚠ Se descargo: {archivo_descargado}")
            return True
        
        if (intento + 1) % 5 == 0:
            print(f"   ... esperando ({(intento + 1) * 2}s)")
    
    print(f"   ❌ Timeout: La descarga no se completo en {timeout*2} segundos")
    return False
# ============= VERIFICAMOS LAS DECARGAS COMPLETAS =============
def verificar_descargas_completas(bases_exitosas):
    """Verifica que todas las descargas se completaron correctamente"""
    
    print("\n🔍 Verificando descargas completas...")
    
    archivos_descargados = os.listdir(DESKTOP_PATH)
    verificacion = []
    
    for base in bases_exitosas:
        # Buscar el archivo en el directorio
        encontrado = any(base in archivo for archivo in archivos_descargados)
        if encontrado:
            # Encontrar el nombre exacto del archivo descargado
            for archivo in archivos_descargados:
                if base in archivo:
                    verificacion.append((base, "✅", archivo))
                    break
        else:
            verificacion.append((base, "❌", "No encontrado"))
    
    print("\nResultado de la verificacion:")
    for archivo, estado, nombre_real in verificacion:
        print(f"  {estado} {archivo} -> {nombre_real}")
    
    return all(estado == "✅" for _, estado, _ in verificacion)
# ============= GENERAMOS EL REPORTE DE DESCARGAS =============
def generar_reporte(bases_exitosas, bases_fallidas):
    """Genera un reporte de las descargas realizadas"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    reporte = f"""
{'='*60}
REPORTE DE DESCARGA - BASES SINAVE (MODO HEADLESS)
{'='*60}
Fecha: {timestamp}
Ubicación: {DESKTOP_PATH}
Total archivos intentados: {len(bases_exitosas) + len(bases_fallidas)}

ARCHIVOS DESCARGADOS EXITOSAMENTE ({len(bases_exitosas)}):
"""
    
    for base in bases_exitosas:
        reporte += f"  ✅ {base}\n"
    
    if bases_fallidas:
        reporte += f"\nARCHIVOS CON ERRORES ({len(bases_fallidas)}):\n"
        for base in bases_fallidas:
            reporte += f"  ❌ {base}\n"
    
    # Verificar qué enfermedades faltan
    enfermedades_descargadas = set()
    for base in bases_exitosas:
        for enfermedad in ENFERMEDADES:
            if enfermedad.lower() in base.lower():
                enfermedades_descargadas.add(enfermedad)
                break
    
    enfermedades_faltantes = set(ENFERMEDADES) - enfermedades_descargadas
    
    if enfermedades_faltantes:
        reporte += f"\n⚠️  ENFERMEDADES SIN DATOS DESCARGADOS ({len(enfermedades_faltantes)}):\n"
        for enf in enfermedades_faltantes:
            reporte += f"  ⚠️  {enf}\n"
    
    reporte += f"\n{'='*60}\n"
    
    # Guardar reporte en archivo
    reporte_path = os.path.join(DESKTOP_PATH, f"reporte_descarga_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(reporte_path, 'w', encoding='utf-8') as f:
        f.write(reporte)
    
    print(reporte)
    print(f"📄 Reporte guardado en: {reporte_path}")
    
    return reporte

def sinave_etvs(user, password):
    """Función principal del script"""
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     BASES DE DATOS SINAVE                                 ║
    ║     Modulo de Enfermedades Transmitidas por Vectores      ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Verificar credenciales
    if USUARIO == "pon el usuario" or PASSWORD == "pon la clave":
        print("❌ ERROR: Debes configurar tus credenciales en el script")
        print("    Edita USUARIO y PASSWORD en las líneas 14-15")
        return
    
    driver = None
    
    try:
        print("🚀 Iniciando proceso en MODO HEADLESS...")
        print("   El navegador trabajará en segundo plano sin mostrar ventanas\n")
        
        # Configurar driver en modo headless
        driver = configurar_driver()
        print("✅ Navegador configurado en modo headless")
        
        # Login
        print("\n🔐 Iniciando sesión en SINAVE...")
        if not login_sinave(driver, USUARIO, PASSWORD):
            print("\n❌ No se pudo completar el login.")
            print("💡 Revisa los screenshots en el escritorio para debug")
            return
        
        # Descargar archivos directamente
        print("\n📥 Iniciando proceso de descarga...")
        bases_exitosas, bases_fallidas = descargar_directamente(driver)
        
        # Verificar descargas
        if bases_exitosas:
            print("\n✅ Verificando integridad de las descargas...")
            verificar_descargas_completas(bases_exitosas)
        
        # Generar reporte
        print("\n📊 Generando reporte final...")
        generar_reporte(bases_exitosas, bases_fallidas)
        
        print(f"\n🎉 ¡Proceso completado exitosamente!")
        print(f"📁 Archivos guardados en: {DESKTOP_PATH}")
        print(f"🔍 Revisa la carpeta para ver los archivos descargados")
        
    except Exception as e:
        print(f"\n❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("\n🔒 Cerrando navegador headless...")
            driver.quit()
            print("✅ Navegador cerrado")
if __name__ == "__main__":
    main()