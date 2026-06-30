import pandas as pd
import folium
from folium.plugins import MarkerCluster
import urllib.parse
import matplotlib.pyplot as plt


CONFIG_VISUAL = {
    "Agricultura de precisión, IoT y sensórica agroambiental": {"color": "green", "icon": "microchip"},
    "Biotecnología y productos biológicos": {"color": "purple", "icon": "flask"},
    "Ganadería y monitoreo animal": {"color": "orange", "icon": "cow"},
    "Software, análisis de datos e inteligencia artificial": {"color": "blue", "icon": "laptop"},
    "Servicios, consultoría, educación y comunicación": {"color": "cadetblue", "icon": "users"},
    "Sustentabilidad, energía y economía circular": {"color": "darkgreen", "icon": "leaf"},
    "Comercio, logística y marketplaces": {"color": "beige", "icon": "shopping-cart"},
    "Robótica, automatización y maquinaria": {"color": "red", "icon": "cogs"},
    "Trazabilidad y seguridad alimentaria": {"color": "darkpurple", "icon": "barcode"},
    "Nanotecnología y materiales avanzados": {"color": "pink", "icon": "atom"},
    "Fintech, seguros y riesgo agrícola": {"color": "lightblue", "icon": "money-bill-wave"},
    "FoodTech e innovación alimentaria": {"color": "lightred", "icon": "utensils"},
    "Agroquímicos y protección de cultivos": {"color": "darkred", "icon": "eye-dropper"},
    "Laboratorios y análisis avanzados": {"color": "gray", "icon": "vials"}
}

CATEGORIAS = list(CONFIG_VISUAL.keys())




# CARGA Y LIMPIEZA

def cargar_y_limpiar_base():
    df = pd.read_excel("ListadoAgtech.xlsx",sheet_name="BASE DE DATOS")
    df.columns = df.columns.str.strip().str.lower()
    for col in ["latitud", "longitud"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(" ", "", regex=False)  # ← ESTA LÍNEA FALTABA
            .str.replace(",", ".", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")



    return df


def generar_mapa(df, centro=None):
    if centro:
        m = folium.Map(location=centro, zoom_start=13, tiles=None)
    else:
        m = folium.Map(location=[-38, -64], zoom_start=5, tiles=None)

    folium.TileLayer("OpenStreetMap", control=False).add_to(m)

    # FontAwesome
    m.get_root().header.add_child(
        folium.Element(
            '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">'
        )
    )

    # CAPAS POR CATEGORÍA
    dict_filtros = {}
    for i, cat in enumerate(CATEGORIAS):
        fg = folium.FeatureGroup(name=cat, show=(i == 0)).add_to(m)
        cluster = MarkerCluster(spiderfy_on_max_zoom=True).add_to(fg)
        dict_filtros[cat] = cluster

    # Función para limpiar texto
    def obtener(row, col):
        val = row.get(col.lower())
        invalidos = ["nan", "", "none", "n/d", "nd", "null", "0", "-", "vacio"]
        if pd.isnull(val) or str(val).strip().lower() in invalidos:
            return None
        return str(val).strip()

    def limpiar_texto(txt):
        if not txt:
            return ""
        return str(txt).strip().lower()

    # MARKERS + POPUPS
    for _, row in df.iterrows():
        lat, lon = row.get("latitud"), row.get("longitud")
        exis = limpiar_texto(row.get("existencia"))


        if ( pd.notnull(lat) and pd.notnull(lon) and str(row["existencia"]).strip().upper() == "SI"):
            nombre = obtener(row, "nombre de la empresa")
            if not nombre:
                nombre = "Sin nombre"


            # Ubicación
            direccion = obtener(row, "dirección")
            ciudad = obtener(row, "ciudad")
            provincia = obtener(row, "provincia")

            # Logo
            logo = obtener(row, "logo")
            img_html = (
                f'<img src="{logo}" style="max-height:45px; max-width:100%; border-radius:4px;">'
                if logo else ""
            )

            # Contactos
            web = obtener(row, "pag web")
            wsp = obtener(row, "whatsapp")
            ins = obtener(row, "instagram")
            lin = obtener(row, "linkedin")
            fbk = obtener(row, "facebook")

            iconos_html = ""
            estilo = "margin:0 4px; font-size:14px; text-decoration:none;"

            if lin:
                url = lin if "linkedin.com" in lin.lower() else f"https://www.linkedin.com/search/results/all/?keywords={urllib.parse.quote(lin)}"
                iconos_html += f'<a href="{url}" target="_blank" style="{estilo} color:#0077b5;"><i class="fab fa-linkedin"></i></a>'

            if ins:
                user = ins.replace("@", "").split("/")[-1]
                iconos_html += f'<a href="https://www.instagram.com/{user}/" target="_blank" style="{estilo} color:#E1306C;"><i class="fab fa-instagram"></i></a>'

            if wsp:
                num = "".join(filter(str.isdigit, wsp))
                iconos_html += f'<a href="https://wa.me/{num}" target="_blank" style="{estilo} color:#25D366;"><i class="fab fa-whatsapp"></i></a>'

            if web:
                url = web if web.startswith("http") else f"https://{web}"
                iconos_html += f'<a href="{url}" target="_blank" style="{estilo} color:#28a745;"><i class="fas fa-globe"></i></a>'

            if fbk:
                url = fbk if "facebook.com" in fbk.lower() else f"https://www.facebook.com/search/top/?q={urllib.parse.quote(fbk)}"
                iconos_html += f'<a href="{url}" target="_blank" style="{estilo} color:#1877F2;"><i class="fab fa-facebook"></i></a>'

            # Categorías activas
            mis_cats = []
            if not mis_cats:
                print("SIN CATEGORÍAS:", nombre)

            for c in CATEGORIAS:
                col = c.lower()
                if col in df.columns:
                    if str(row[col]).strip().upper() == "SI":
                        mis_cats.append(c)




            # Obtener categoría principal
            cat_principal = obtener(row, "categoría principal")
            if cat_principal:
                cat_principal = cat_principal.strip().lower()

            # Construir lista de categorías con principal resaltada
            lista_cat = ""
            for c in mis_cats:
                c_norm = c.strip().lower()
                if cat_principal and c_norm == cat_principal:
                    lista_cat += (
                        f"<li style='font-size:11px; font-weight:bold; border:1px solid #0077b5;"
                        f"background-color:#D6EAF8; padding:2px 4px; border-radius:4px; text-align:center;"
                        f"margin-bottom:2px;'>{c}</li>"
                    )
                else:
                    lista_cat += f"<li style='font-size:10px'>{c}</li>"

            # Popup HTML
            popup_html = f"""
            <div style="width:210px; font-family:Arial;">
                <div style="text-align:center; margin-bottom:6px;">
                    {img_html}
                </div>

                <h4 style="text-align:center; font-size:13px; margin:4px 0;">
                    {nombre}
                </h4>

                <div style="font-size:9px; text-align:center;">
                    {direccion or ""}<br>{ciudad or ""} {provincia or ""}
                </div>

                <ul style="padding-left:14px;">
                    {lista_cat}
                </ul>

                <div style="text-align:center;">
                    {iconos_html}
                </div>
            </div>
            """

            # Agregar marcador al mapa (por cada categoría activa)
            for cat_actual in mis_cats:
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=260),
                    tooltip=nombre,
                    icon=folium.Icon(
                        color=CONFIG_VISUAL[cat_actual]["color"],
                        icon=CONFIG_VISUAL[cat_actual]["icon"],
                        prefix="fa",
                    ),
                ).add_to(dict_filtros[cat_actual])

    # Agregar control de capas al mapa
    folium.LayerControl(collapsed=True).add_to(m)
    print(
        "ROW:",
        nombre,
        "LAT:", lat,
        "LON:", lon,
        "EXIS:", row.get("existencia"),
        "CATS:", mis_cats
    )

    return m

def grafico_empresas_por_provincia(df):
    df_ok = df[df["existencia"].astype(str).str.upper() == "SI"]

    conteo = (
        df_ok["provincia"]
        .dropna()
        .astype(str)
        .str.strip()
        .value_counts()
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(5,4))

    ax.barh(conteo.index, conteo.values, color="#4C78A8")
    agregar_valores_barras(ax, orientacion="horizontal")

    ax.set_title("Empresas por provincia", fontsize=12)
    ax.set_xlabel("Cantidad")
    ax.set_ylabel("")

    # estilo más limpio
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.3)

    plt.tight_layout()

    return fig


def grafico_empresas_por_categoria(df):
    totales = {}

    for cat in CATEGORIAS:
        col = cat.lower()
        if col not in df.columns:
            continue

        df_cat = df[
            (df["existencia"].astype(str).str.upper() == "SI") &
            (df[col].astype(str).str.upper() == "SI")
        ]

        totales[cat] = len(df_cat)

    serie = pd.Series(totales).sort_values()

    fig, ax = plt.subplots(figsize=(5,4))

    ax.barh(serie.index, serie.values, color="#4C78A8")
    agregar_valores_barras(ax, orientacion="horizontal")

    ax.set_title("Empresas por categoría", fontsize=12)
    ax.set_xlabel("Cantidad")
    ax.set_ylabel("")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.3)

    plt.tight_layout()

    return fig


def grafico_categoria_por_provincia(df, categoria):

    col = categoria.lower()

    if col not in df.columns:
        return None

    df_cat = df[
        (df["existencia"].astype(str).str.upper() == "SI") &
        (df[col].astype(str).str.upper() == "SI")
    ]

    conteo = (
        df_cat["provincia"]
        .dropna()
        .astype(str)
        .str.strip()
        .value_counts()
        .sort_values()
    )

    if conteo.empty:
        return None

    fig, ax = plt.subplots(figsize=(5,4))

    barras = ax.bar(conteo.index, conteo.values, color="#4C78A8")

    ax.bar_label(barras, fontsize=8)

    ax.set_ylabel("Cantidad")
    ax.set_ylim(0, max(conteo.values) * 1.15)

    plt.xticks(rotation=45, ha="right", fontsize=9)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    plt.tight_layout()

    return fig


def agregar_valores_barras(ax, orientacion="vertical"):

    if orientacion == "horizontal":

        for barra in ax.patches:

            ancho = barra.get_width()

            ax.text(
                ancho + 0.1,
                barra.get_y() + barra.get_height() / 2,
                f"{int(ancho)}",
                va="center",
                fontsize=8
            )

    else:

        for barra in ax.patches:

            alto = barra.get_height()

            ax.text(
                barra.get_x() + barra.get_width() / 2,
                alto + 0.2,
                f"{int(alto)}",
                ha="center",
                va="bottom",
                fontsize=8
            )
