import time
import os
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

# === CONFIGURACIÓN ===
TOKEN = '8472437110:AAE86sPmyyXUpkIxDrCoMLrLOJc0--oLSi8'
CHAT_ID = '380944998'
URL = 'https://inmuebles.mercadolibre.com.ar/departamentos/alquiler/mas-de-2-ambientes/capital-federal/barracas-o-palermo-o-palermo-chico-o-palermo-hollywood-o-palermo-soho-o-palermo-viejo-o-puerto-madero-o-retiro-o-recoleta-o-san-telmo-o-san-nicolas-o-monserrat-o-balvanera-o-almagro/alquiler_OrderId_PRICE_PriceRange_250000ARS-0ARS_NoIndex_True_TOTAL*AREA_50m%C2%B2-*'

def iniciar_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('--incognito')
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222')
    options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    
    driver = webdriver.Chrome(options=options)
    return driver

def extraer_expensas(driver, url):
    """Entra a la página del departamento y extrae las expensas usando XPATH"""
    try:
        print(f"  🔍 Extrayendo expensas de: {url[:50]}...")
        driver.get(url)
        time.sleep(2)
        
        # XPATH que me pasaste para expensas
        try:
            expensas_element = driver.find_element(By.XPATH, "//*[@id='maintenance_fee_vis']/p/span")
            expensas_text = expensas_element.text.strip()
            # Extraer solo números
            expensas = re.sub(r'[^0-9]', '', expensas_text)
            print(f"  ✅ Expensas encontradas: ${expensas}")
            return expensas if expensas else "0"
        except:
            # Si no encuentra el XPATH exacto, buscar alternativas
            try:
                # Buscar por texto que contenga "expensas"
                expensas_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Expensas')]/following::span[contains(@class, 'andes-money-amount__fraction')]")
                expensas = expensas_element.text.replace('.', '')
                return expensas
            except:
                print("  ⚠️ No se encontraron expensas")
                return "0"
    except Exception as e:
        print(f"  ❌ Error extrayendo expensas: {e}")
        return "0"

def obtener_datos_detalle(driver, url):
    """Extrae todos los datos de la página de detalle"""
    try:
        driver.get(url)
        time.sleep(2)
        
        datos = {}
        
        # Dirección (XPATH que me pasaste)
        try:
            direccion = driver.find_element(By.XPATH, "//*[@id='header']/div/div[3]/a/span").text.strip()
            datos['direccion'] = direccion
        except:
            datos['direccion'] = "No disponible"
        
        # Ambientes (XPATH que me pasaste)
        try:
            ambientes = driver.find_element(By.XPATH, "//*[@id='highlighted_specs_res']/div/div[1]/span[2]/span").text.strip()
            datos['ambientes'] = ambientes
        except:
            datos['ambientes'] = "?"
        
        # Metros cuadrados (XPATH que me pasaste)
        try:
            m2 = driver.find_element(By.XPATH, "//*[@id='highlighted_specs_res']/div/div[3]/span[2]/span").text.strip()
            datos['m2'] = m2
        except:
            datos['m2'] = "?"
        
        # Expensas (XPATH que me pasaste)
        try:
            expensas = driver.find_element(By.XPATH, "//*[@id='maintenance_fee_vis']/p/span").text.strip()
            expensas = re.sub(r'[^0-9]', '', expensas)
            datos['expensas'] = expensas if expensas else "0"
        except:
            datos['expensas'] = "0"
        
        return datos
    except Exception as e:
        print(f"  ❌ Error en página de detalle: {e}")
        return None

def obtener_departamentos():
    driver = iniciar_driver()
    print("🔍 Navegando a MercadoLibre...")
    driver.get(URL)
    
    try:
        print("⏳ Esperando que carguen los resultados...")
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-search-layout__item, .poly-card__content")))
        time.sleep(3)
        
        # Obtener items del listado
        items = driver.find_elements(By.CSS_SELECTOR, "li.ui-search-layout__item")[:10]
        print(f"📊 Encontrados {len(items)} departamentos")
        
        resultados = []
        
        # Primero extraemos datos básicos del listado
        for i, item in enumerate(items, 1):
            try:
                # Link (lo necesitamos para después)
                link_element = item.find_element(By.CSS_SELECTOR, "a.poly-component__title, a.ui-search-item__group__element")
                link = link_element.get_attribute("href")
                
                # Precio
                precio_tag = item.find_element(By.CSS_SELECTOR, ".andes-money-amount__fraction")
                precio = precio_tag.text.replace(".", "")
                
                # Guardamos datos básicos
                resultados.append({
                    "precio": precio,
                    "link": link,
                    "expensas": "0",  # placeholder
                    "direccion": "",   # placeholder
                    "ambientes": "",    # placeholder
                    "m2": ""           # placeholder
                })
                
                print(f"  📍 {i}. Link obtenido: {link[:50]}...")
                
            except Exception as e:
                print(f"  ❌ Error en item {i}: {e}")
                continue
        
        # Ahora entramos a cada link para obtener los datos detallados
        print("\n🔍 Extrayendo datos detallados de cada departamento...")
        for i, depto in enumerate(resultados, 1):
            print(f"\n📄 Procesando departamento {i}/10:")
            datos_detalle = obtener_datos_detalle(driver, depto['link'])
            
            if datos_detalle:
                depto['direccion'] = datos_detalle.get('direccion', 'No disponible')
                depto['ambientes'] = datos_detalle.get('ambientes', '?')
                depto['m2'] = datos_detalle.get('m2', '?')
                depto['expensas'] = datos_detalle.get('expensas', '0')
                
                print(f"  ✅ Datos completos:")
                print(f"     Dirección: {depto['direccion']}")
                print(f"     Ambientes: {depto['ambientes']}")
                print(f"     Metros: {depto['m2']}")
                print(f"     Expensas: ${depto['expensas']}")
            else:
                print(f"  ⚠️ Usando datos del listado para este departamento")
        
        driver.quit()
        return resultados
        
    except Exception as e:
        print(f"❌ ERROR GENERAL: {e}")
        screenshot_path = f"debug_ml_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot guardado: {screenshot_path}")
        driver.quit()
        return []

def crear_mensaje(data):
    if not data:
        return "No se encontraron departamentos hoy."
    
    mensaje = "🏠 *Buen día Mati, te paso los alquileres del día de hoy:*\n\n"
    for i, d in enumerate(data, 1):
        mensaje += f"{i} - ${d['precio']} ARS + ${d['expensas']} ARS (Expensas) | {d['direccion']} | {d['ambientes']} | {d['m2']} | [Ver más]({d['link']})\n"
    return mensaje

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("✅ Mensaje enviado a Telegram")
    else:
        print(f"❌ Error enviando a Telegram: {response.status_code}")

def main():
    print("🚀 Iniciando bot de alquileres...")
    print("⏱️  Este proceso puede tomar 1-2 minutos (entrando a 10 páginas)...")
    
    data = obtener_departamentos()
    
    if not data:
        print("⚠️ No se encontraron datos")
        enviar_telegram("⚠️ No se encontraron departamentos. Revisá la carpeta del bot para ver el screenshot.")
        return
    
    mensaje = crear_mensaje(data)
    enviar_telegram(mensaje)
    print("✨ Proceso completado!")

if __name__ == "__main__":
    main()
