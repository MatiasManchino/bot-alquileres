import requests
from bs4 import BeautifulSoup

TOKEN = "8472437110:AAE86sPmyyXUpkIxDrCoMLrLOJc0--oLSi8"
CHAT_ID = "380944998"

URL = "https://inmuebles.mercadolibre.com.ar/departamentos/alquiler/mas-de-2-ambientes/capital-federal/barracas-o-palermo-o-palermo-chico-o-palermo-hollywood-o-palermo-soho-o-palermo-viejo-o-puerto-madero-o-retiro-o-recoleta-o-san-telmo-o-san-nicolas-o-monserrat-o-balvanera-o-almagro/alquiler_OrderId_PRICE_PriceRange_250000ARS-0ARS_NoIndex_True_TOTAL*AREA_50m%C2%B2-*"

headers = {
    "User-Agent": "Mozilla/5.0"
}


def obtener_departamentos():

    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    items = soup.select("li.ui-search-layout__item")[:10]

    departamentos = []

    for item in items:

        titulo = item.select_one("a.poly-component__title")

        if titulo:
            link = titulo["href"]
            direccion = titulo.text.strip()
        else:
            continue

        precio = item.select_one(".andes-money-amount__fraction")
        precio = precio.text if precio else "?"

        detalles = item.select(".ui-search-card-attributes__attribute")

        ambientes = "?"
        m2 = "?"

        for d in detalles:

            texto = d.text.lower()

            if "amb" in texto:
                ambientes = d.text

            if "m²" in texto:
                m2 = d.text

        departamentos.append({
            "precio": precio,
            "direccion": direccion,
            "ambientes": ambientes,
            "m2": m2,
            "link": link
        })

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

    mensaje = crear_mensaje(data)

    enviar_telegram(mensaje)


if __name__ == "__main__":
    main()
