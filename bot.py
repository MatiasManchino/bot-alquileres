import requests
from bs4 import BeautifulSoup
import time
import datetime
import os

# === CONFIGURACIÓN (cambiá solo si querés) ===
TOKEN = "8472437110:AAE86sPmyyXUpkIxDrCoMLrLOJc0--oLSi8"   # ← tu token
CHAT_ID = "380944998"                                      # ← tu chat ID
URL = "https://inmuebles.mercadolibre.com.ar/departamentos/alquiler/mas-de-2-ambientes/capital-federal/barracas-o-palermo-o-palermo-chico-o-palermo-hollywood-o-palermo-soho-o-palermo-viejo-o-puerto-madero-o-retiro-o-recoleta-o-san-telmo-o-san-nicolas-o-monserrat-o-balvanera-o-almagro/alquiler_OrderId_PRICE_PriceRange_250000ARS-0ARS_NoIndex_True_TOTAL*AREA_50m%C2%B2-*"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept-Language": "es-AR,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Referer": "https://www.mercadolibre.com.ar/",
    "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
}

def obtener_departamentos():
    for intento in range(3):  # 3 intentos por si hay lag
        try:
            r = requests.get(URL, headers=headers, timeout=15)
            if r.status_code != 200:
                time.sleep(2)
                continue
                
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Selectores actualizados 2026 (probados y robustos)
            items = soup.select("li.ui-search-layout__item")[:10]
            if not items:
                items = soup.select(".ui-search-result")[:10]
            
            resultados = []
            for item in items:
                try:
                    # Link y dirección
                    titulo = item.select_one("a.poly-component__title") or item.select_one(".ui-search-item__title a")
                    direccion = titulo.text.strip() if titulo else "Sin dirección"
                    link = titulo["href"] if titulo else "#"
                    
                    # Precio alquiler
                    precio_tag = item.select_one(".andes-money-amount__fraction")
                    precio = precio_tag.text.strip().replace(".", "") if precio_tag else "?"
                    
                    # Expensas (casi nunca aparece en lista → 0)
                    expensas = "0"
                    
                    # Ambientes y m²
                    ambientes = "?"
                    m2 = "?"
                    for attr in item.select(".ui-search-card-attributes__attribute, .poly-component__attributes"):
                        txt = attr.text.lower()
                        if "amb" in txt:
                            ambientes = attr.text.strip()
                        if "m²" in txt or "m2" in txt:
                            m2 = attr.text.strip()
                    
                    resultados.append({
                        "precio": precio,
                        "expensas": expensas,
                        "direccion": direccion,
                        "ambientes": ambientes,
                        "m2": m2,
                        "link": link
                    })
                except:
                    continue
            return resultados
        except:
            time.sleep(3)
    return []

def crear_mensaje(data):
    mensaje = "Buen día Mati, te paso los alquileres del día de hoy:\n\n"
    for i, d in enumerate(data, 1):
        linea = f"{i} - {d['precio']} ARS + {d['expensas']} ARS (Expensas) | {d['direccion']} | {d['ambientes']} | {d['m2']} | {d['link']}"
        mensaje += linea + "\n"
    return mensaje

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": mensaje})

def main():
    data = obtener_departamentos()
    if not data:
        enviar_telegram("⚠️ No se encontraron departamentos hoy (ML puede estar temporalmente bloqueando). Volvé a probar mañana.")
        return
    msg = crear_mensaje(data)
    enviar_telegram(msg)

if __name__ == "__main__":
    main()
