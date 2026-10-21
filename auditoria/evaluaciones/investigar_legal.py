from auditoria.comprobaciones import descargar_html

URL = "https://www.colegiodelibes.es/"

if __name__ == "__main__":
    soup = descargar_html(URL)
    html = str(soup)
    print("Título:", soup.title.get_text(strip=True) if soup.title else None)
    print("Tamaño del HTML:", len(html), "caracteres")


    print("¿Aparece 'privacidad' en algún sitio del HTML?", "privacidad" in html.lower())
    print("¿Aparece 'aviso legal'?", "aviso legal" in html.lower())

    print("\nEnlaces que mencionan algo legal:")
    for enlace in soup.find_all("a"):
        texto = enlace.get_text(" ", strip=True)
        href = enlace.get("href")
        if "privac" in texto.lower() or "legal" in texto.lower():
            print(repr(texto), "→ href:", repr(href))