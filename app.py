import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
from agtech import cargar_y_limpiar_base, generar_mapa, CATEGORIAS, agregar_valores_barras, grafico_categoria_por_provincia,grafico_empresas_por_categoria, grafico_empresas_por_provincia



# CONFIG GENERAL

st.set_page_config(
    page_title="Mapa AgTech Argentina",
    layout="wide"
)

# TABS
tab_contexto, tab_visualizacion = st.tabs(
    [" Contexto", " Visualización"]
)


# TAB 1 — CONTEXTO

with tab_contexto:
    st.title("Ecosistema AgTech Argentina")

    st.image("unraf_logo.png", width=300)

    st.markdown("""
    ### Sobre el proyecto
    Acá podemos escribir sobre  que se trata el proyecto y con lo que se van a encontrar
    """)
    st.markdown("""
    **Becarias del proyecto**  
    - Andereggen, Valentina  
    - Kühn, Priscila  
    """)

# TAB 2 — VISUALIZACIÓN

with tab_visualizacion:

    st.title("Visualización del ecosistema AgTech")

    
    # SIDEBAR
    
    st.sidebar.header("Panel de control")

    mostrar_mapa = st.sidebar.checkbox(" Mapa", value=True)
    mostrar_stats = st.sidebar.checkbox("Estadísticas", value=False)
    mostrar_algoritmos = st.sidebar.checkbox("Algoritmos", value=False)

    # DATA
  
    df = cargar_y_limpiar_base()

    st.markdown("### Buscar empresa")

    texto_busqueda = st.text_input(
        "Escribí el nombre de la empresa",
        placeholder="Ej: Agro, Bio, Tech."
    )

    centro = None        
    empresa_sel = None
    opciones = []   # ← CLAVE: inicializar

    if texto_busqueda:
        opciones = (
        df["nombre de la empresa"]
        .dropna()
        .astype(str)
        [df["nombre de la empresa"]
            .str.contains(texto_busqueda, case=False, na=False)]
        .sort_values()
        .unique()
        )

    if len(opciones) == 0:
        st.info("No se encontraron empresas con ese nombre.")
    else:
        empresa_sel = st.selectbox(
            "Resultados",
            opciones
        )


      
    if empresa_sel:
        fila = df[df["nombre de la empresa"] == empresa_sel].iloc[0]

        lat = fila.get("latitud")
        lon = fila.get("longitud")

        if pd.notnull(lat) and pd.notnull(lon):
            centro = [lat, lon]



    # MAPA
 
    if mostrar_mapa:
        st.subheader("Mapa interactivo")

        mapa = generar_mapa(df, centro)   # ← ACÁ se crea

        st_folium(
            mapa,
            width=None,
            height=600,
            use_container_width=True,
            key="mapa_principal"
        )



    # ESTADÍSTICAS Y GRÁFICOS

    if mostrar_stats:
        st.subheader("Estadísticas del ecosistema")

        # Gráficos superiores
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Empresas por provincia")
            st.pyplot(grafico_empresas_por_provincia(df))

        with col2:
            st.markdown("### Empresas por categoría")
            st.pyplot(grafico_empresas_por_categoria(df))

        # Gráfico por categoría seleccionada
        st.markdown("### Empresas por provincia según categoría")

        col_sel, col_graf = st.columns([1, 2])

        with col_sel:
            categoria_sel = st.selectbox(
                "Seleccioná una categoría",
                CATEGORIAS,
                key="categoria_stats"
            )

        with col_graf:
            fig = grafico_categoria_por_provincia(df, categoria_sel)
            if fig:
                st.pyplot(fig)
            else:
                st.info("No hay datos para esta categoría.")


    
    if mostrar_algoritmos:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.subheader(" Algoritmos")

        st.info("Esta sección se completará cuando estén disponibles los algoritmos.")

        st.markdown("</div>", unsafe_allow_html=True)

# FOOTER



#st.set_page_config(layout="wide")

st.markdown("""
<style>
.stApp { background-color: #f4f8fb; }
h1 { color: #1a5276; }
</style>
""", unsafe_allow_html=True)


st.markdown("---")
st.markdown(
    "<center style='font-size:11px;'>Proyecto AgTech UNRaf· Streamlit</center>",
    unsafe_allow_html=True
)
