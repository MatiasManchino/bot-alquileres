import json
import time
import requests

import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


TOKEN = "8472437110:AAE86sPmyyXUpkIxDrCoMLrLOJc0--oLSi8"
CHAT_ID = "380944998"

URL_BASE = "https://inmuebles.mercadolibre.com.ar/departamentos/alquiler/mas-de-2-ambientes/capital-federal/barracas-o-palermo-o-palermo-chico-o-palermo-hollywood-o-palermo-soho-o-palermo-viejo-o-puerto-madero-o-retiro-o-recoleta-o-san-telmo-o-san-nicolas-o-monserrat-o-balvanera-o-almagro/alquiler_OrderId_PRICE_PriceRange_250000ARS-0ARS_NoIndex_True_TOTAL*AREA_50m%C2%B2-*"

HISTORIAL_FILE = "historial.json"

PAGINAS = 5


def iniciar_driver():

    options = uc.ChromeOptions()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)

    return driver


def obtener_departamentos():

    driver = iniciar_driver()

    resultados = []

    for pagina in range(PAGINAS):

        offset = pagina * 48

        url = f"{URL_BASE}_Desde_{offset}"

        driver.get(url)

        wait = WebDriverWait(driver, 20)

        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-search-layout__item"))
        )

        items = driver.find_elements(By.CSS_SELECTOR, "li.ui-search-layout__item")

        for item in items:

            try:

                titulo = item.find_element(By.CSS_SELECTOR, "a.poly-component__title")

                direccion = titulo.text

                link = titulo.get_attribute("href")

            except:
                continue

            try:
                precio = item.find_element(By.CSS_SELECTOR, ".andes-money-amount__fraction").text
                precio = int(precio.replace(".", ""))
            except:
                precio = 0

            ambientes = "?"
            m2 = "?"

            detalles = item.find_elements(By.CSS_SELECTOR, ".ui-search-card-attributes__attribute")

            for d in detalles:

                texto = d.text.lower()

                if "amb" in texto:
                    ambientes = d.text

                if "m²" in texto:
                    m2 = d.text

            resultados.append({
                "precio": precio,
                "direccion": direccion,
                "ambientes": ambientes,
                "m2": m2,
                "link": link
            })

        time.sleep(2)

    driver.quit()

    return resultados


def cargar_historial():

    try:
        with open(HISTORIAL_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def guardar_historial(data):

    with open(HISTORIAL_FILE, "w") as f:
        json.dump(data, f)


def filtrar_nuevos(data, historial):

    links_vistos = set(historial)

    nuevos = []

    for d in data:

        if d["link"] not in links_vistos:

            nuevos.append(d)

    return nuevos


def detectar_baratos(data):

    baratos = []

    for d in data:

        if d["precio"] != 0 and d["precio"] < 500000:

            baratos.append(d)

    return baratos


def crear_mensaje(data, titulo):

    mensaje = f"{titulo}\n\n"

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

    departamentos = obtener_departamentos()

    historial = cargar_historial()

    nuevos = filtrar_nuevos(departamentos, historial)

    baratos = detectar_baratos(departamentos)

    if nuevos:

        msg = crear_mensaje(nuevos[:10], "🏠 Departamentos nuevos detectados:")

        enviar_telegram(msg)

    if baratos:

        msg = crear_mensaje(baratos[:5], "💰 Posibles gangas:")

        enviar_telegram(msg)

    guardar_historial([d["link"] for d in departamentos])


if __name__ == "__main__":
    main()
