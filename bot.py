import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === CONFIGURACIÓN ===
TOKEN = "8472437110:AAE86sPmyyXUpkIxDrCoMLrLOJc0--oLSi8"
CHAT_ID = "380944998"
URL = "https://inmuebles.mercadolibre.com.ar/departamentos/alquiler/mas-de-2-ambientes/capital-federal/barracas-o-palermo-o-palermo-chico-o-palermo-hollywood-o-palermo-soho-o-palermo-viejo-o-puerto-madero-o-retiro-o-recoleta-o-san-telmo-o-san-nicolas-o-monserrat-o-balvanera-o-almagro/alquiler_OrderId_PRICE_PriceRange_250000ARS-0ARS_NoIndex_True_TOTAL*AREA_50m%C2%B2-*"

def iniciar_driver():
    options = Options()
    options.add_argument("--headless=new")           # sin ventana visible
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    # ←←← USAMOS TU PERFIL LOGUEADO DE CHROME (nunca más verificación)
    options.add_argument(f"--user-data-dir={os.path.expanduser('~')}\\AppData\\Local\\Google\\Chrome\\User Data")
    options.add_argument("--profile-directory=Default")   # perfil principal

    driver = webdriver.Chrome(options=options)
    return driver

def obtener_departamentos():
    driver = iniciar_driver()
    driver.get(URL)
    
    try:
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-search-layout__item, .poly-component__title")))
        time.sleep(4)  # dejar que cargue todo
        
        items = driver.find_elements(By.CSS_SELECTOR, "li.ui-search-layout__item")[:10]
        
        resultados = []
        for item in items:
            try:
                titulo = item.find_element(By.CSS_SELECTOR, "a.poly-component__title")
                direccion = titulo.text.strip()
                link = titulo.get_attribute("href")
                
                precio = item.find_element(By.CSS_SELECTOR, ".andes-money-amount__fraction").text.replace(".", "")
                
                ambientes = "?"
                m2 = "?"
                for attr in item.find_elements(By.CSS_SELECTOR, ".poly-component__attributes span"):
                    txt = attr.text.lower()
                    if "amb" in txt: ambientes = attr.text
                    if "m²" in txt or "m2" in txt: m2 = attr.text
                
                resultados.append({
                    "precio": precio,
                    "expensas": "0",
                    "direccion": direccion,
                    "ambientes": ambientes,
                    "m2": m2,
                    "link": link
                })
            except:
                continue
                
    except Exception as e:
        # ←←← CAPTURA AUTOMÁTICA CUANDO FALLA (para debug)
        driver.save_screenshot(f"debug_ml_{datetime.now().strftime('%Y%m%d_%H%M')}.png")
        print(f"Error capturado. Screenshot guardado: debug_ml_*.png")
        driver.quit()
        return []
    
    driver.quit()
    return resultados

def crear_mensaje(data):
    mensaje = "Buen día Mati, te paso los alquileres del día de hoy:\n\n"
    for i, d in enumerate(data, 1):
        linea = f"{i} - {d['precio']} ARS + {d['expensas']} ARS (Expensas) | {d['direccion']} | {d['ambientes']} | {d['m2']} | {d['link']}"
        mensaje += linea + "\n"
    return mensaje

def enviar_telegram(mensaje):
    import requests
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": mensaje})

def main():
    data = obtener_departamentos()
    if not data:
        enviar_telegram("⚠️ No se encontraron departamentos (ML mostró verificación). Screenshot guardado en la carpeta para que lo veas.")
        return
    msg = crear_mensaje(data)
    enviar_telegram(msg)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
