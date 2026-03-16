import time
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


TOKEN = "8472437110:AAE86sPmyyXUpkIxDrCoMLrLOJc0--oLSi8"
CHAT_ID = "380944998"

URL = "https://inmuebles.mercadolibre.com.ar/departamentos/alquiler/mas-de-2-ambientes/capital-federal/barracas-o-palermo-o-palermo-chico-o-palermo-hollywood-o-palermo-soho-o-palermo-viejo-o-puerto-madero-o-retiro-o-recoleta-o-san-telmo-o-san-nicolas-o-monserrat-o-balvanera-o-almagro/alquiler_OrderId_PRICE_PriceRange_250000ARS-0ARS_NoIndex_True_TOTAL*AREA_50m%C2%B2-*"


def obtener_departamentos():

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    driver.get(URL)

    time.sleep(5)

    items = driver.find_elements(By.CSS_SELECTOR, "li.ui-search-layout__item")

    departamentos = []

    for item in items[:10]:

        try:

            titulo = item.find_element(By.CSS_SELECTOR, "a.poly-component__title")

            direccion = titulo.text
            link = titulo.get_attribute("href")

        except:
            continue

        try:
            precio = item.find_element(By.CSS_SELECTOR, ".andes-money-amount__fraction").text
        except:
            precio = "?"

        try:
            detalles = item.find_elements(By.CSS_SELECTOR, ".ui-search-card-attributes__attribute")

            ambientes = "?"
            m2 = "?"

            for d in detalles:

                t = d.text.lower()

                if "amb" in t:
                    ambientes = d.text

                if "m²" in t:
                    m2 = d.text

        except:
            ambientes = "?"
            m2 = "?"

        departamentos.append({
            "precio": precio,
            "direccion": direccion,
            "ambientes": ambientes,
            "m2": m2,
            "link": link
        })

    driver.quit()

    return departamentos


def crear_mensaje(data):

    mensaje = "Buen día Mati, te paso los alquileres del día de hoy:\n\n"

    for i, d in enumerate(data, 1):

        linea = f"{i} - {d['precio']} ARS | {d['direccion']} | {d['ambientes']} | {d['m2']} | {d['link']}"

        mensaje += linea + "\n"

    return mensaje


def enviar_telegram(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=payload)


def main():

    data = obtener_departamentos()

    if not data:
        enviar_telegram("No se encontraron resultados hoy.")
        return

    mensaje = crear_mensaje(data)

    enviar_telegram(mensaje)


if __name__ == "__main__":
    main()
