import streamlit as st
import pandas as pd
import numpy as np

COLOR_PRINCIPAL = "#00B8AA"

st.set_page_config(
    page_title="Ski Resort Recommender",
    page_icon="🎿",
    layout="wide"
)

st.markdown(
    f"""
    <style>
    .stButton>button {{
        background-color: {COLOR_PRINCIPAL};
        color: white;
        border-radius: 10px;
        border: none;
    }}
    [data-testid="stMetricValue"] {{
        color: {COLOR_PRINCIPAL};
    }}
    h1, h2, h3 {{
        color: {COLOR_PRINCIPAL};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/ski_resorts_powerbi.csv")
    df = df.dropna()

    if "Categoría tamaño" in df.columns:
        df = df[~df["Categoría tamaño"].isin(["Muy pequeña", "Pequeña"])]

    return df


df = load_data()


def get_col(posibles_nombres):
    for col in posibles_nombres:
        if col in df.columns:
            return col
    st.error(f"No se encontró ninguna de estas columnas: {posibles_nombres}")
    st.stop()


COL_ESTACION = get_col(["Estación", "Resort", "Ski resort"])
COL_PAIS = get_col(["País", "Country"])
COL_CONTINENTE = get_col(["Continente", "Continent"])
COL_KM_TOTALES = get_col(["Km totales", "Total Kms"])
COL_KM_FACILES = get_col(["Km fáciles", "Easy slopes"])
COL_KM_INTERMEDIOS = get_col(["Km intermedios", "Intermediate slopes"])
COL_KM_DIFICILES = get_col(["Km difíciles", "Difficult slopes"])
COL_KM_FREERIDE = get_col(["Km freeride", "Freeride"])
COL_PRECIO_EUR = get_col(["Precio forfait EUR", "Adult price EUR"])
COL_PRECIO_KM_EUR = get_col(["Precio por km EUR", "Price per km EUR"])
COL_VALORACION = get_col(["Valoración", "Rating"])
COL_NIEVE = get_col(["Fiabilidad de nieve", "Snow reliability"])
COL_ALTITUD = get_col(["Altitud", "Altitude"])
COL_FAMILIAS = get_col(["Familias y niños", "Families and children"])
COL_APRES = get_col(["Après-ski", "Apres-ski"])
COL_SNOWPARK = get_col(["Snowparks", "Snow parks", "Snowpark"])
COL_GASTRONOMIA = get_col(["Gastronomía", "Mountain restaurants, ski huts, gastronomy"])
COL_ACCESO = get_col(["Acceso y aparcamiento", "Access, on-site parking"])
COL_SENALIZACION = get_col(["Señalización", "Orientation (trail map, information boards, sign-postings)"])
COL_LIMPIEZA = get_col(["Limpieza e higiene", "Cleanliness and hygiene"])
COL_REMONTES = get_col(["Remontes y teleféricos", "Lifts and cable cars"])
COL_ALOJAMIENTO = get_col([
    "Alojamiento en pistas",
    "Accommodation offering at the slopes",
    "Accommodation directly at the slopes and lifts"
])


def normalize(series):
    if series.max() == series.min():
        return series * 0
    return (series - series.min()) / (series.max() - series.min())


def recomendar_estaciones(data, perfil, tipo_viaje):
    data = data.copy()

    data["score_valoracion"] = normalize(data[COL_VALORACION])
    data["score_nieve"] = normalize(data[COL_NIEVE])
    data["score_km"] = normalize(data[COL_KM_TOTALES])
    data["score_precio"] = 1 - normalize(data[COL_PRECIO_KM_EUR])

    if perfil == "Principiante":
        data = data[data[COL_KM_FACILES] > 0]
        data["score_perfil"] = normalize(data[COL_KM_FACILES])
    elif perfil == "Intermedio":
        data = data[data[COL_KM_INTERMEDIOS] > 0]
        data["score_perfil"] = normalize(data[COL_KM_INTERMEDIOS])
    elif perfil == "Experto":
        data = data[data[COL_KM_DIFICILES] > 0]
        data["score_perfil"] = normalize(data[COL_KM_DIFICILES])
    elif perfil == "Freeride":
        data = data[data[COL_KM_FREERIDE] > 0]
        data["score_perfil"] = normalize(data[COL_KM_FREERIDE])

    if data.empty:
        return data

    if tipo_viaje == "Familia":
        data["score_viaje"] = normalize(data[COL_FAMILIAS])
    elif tipo_viaje == "Fiesta":
        data["score_viaje"] = normalize(data[COL_APRES])
    elif tipo_viaje == "Barato":
        data["score_viaje"] = data["score_precio"]
    elif tipo_viaje == "Snowpark":
        data["score_viaje"] = normalize(data[COL_SNOWPARK])
    elif tipo_viaje == "Gastronomía":
        data["score_viaje"] = normalize(data[COL_GASTRONOMIA])
    else:
        data["score_viaje"] = normalize(data[COL_VALORACION])

    data["score_final"] = (
        data["score_valoracion"] * 0.20 +
        data["score_nieve"] * 0.20 +
        data["score_km"] * 0.15 +
        data["score_precio"] * 0.15 +
        data["score_perfil"] * 0.20 +
        data["score_viaje"] * 0.10
    )

    return data.sort_values("score_final", ascending=False)


st.sidebar.title("Preferencias del viaje")

continentes = sorted(df[COL_CONTINENTE].dropna().unique())
continente = st.sidebar.multiselect("Continente", continentes, default=continentes)

paises = sorted(df[df[COL_CONTINENTE].isin(continente)][COL_PAIS].dropna().unique())
pais = st.sidebar.multiselect("País", paises, default=paises)

perfil = st.sidebar.selectbox(
    "Perfil de esquiador",
    ["Principiante", "Intermedio", "Experto", "Freeride"]
)

tipo_viaje = st.sidebar.selectbox(
    "Tipo de viaje",
    ["General", "Familia", "Fiesta", "Barato", "Snowpark", "Gastronomía"]
)

precio_max = st.sidebar.slider(
    "Precio máximo forfait (€)",
    int(df[COL_PRECIO_EUR].min()),
    int(df[COL_PRECIO_EUR].max()),
    int(df[COL_PRECIO_EUR].quantile(0.75))
)

km_min = st.sidebar.slider(
    "Km esquiables mínimos",
    int(df[COL_KM_TOTALES].min()),
    int(df[COL_KM_TOTALES].max()),
    50
)

st.sidebar.subheader("Filtros de calidad (0-5)")

snow_min = st.sidebar.slider("Fiabilidad de nieve", 0.0, 5.0, 0.0, 0.1)
alojamiento_min = st.sidebar.slider("Alojamiento en pistas", 0.0, 5.0, 0.0, 0.1)
access_min = st.sidebar.slider("Acceso y aparcamiento", 0.0, 5.0, 0.0, 0.1)
orientation_min = st.sidebar.slider("Señalización", 0.0, 5.0, 0.0, 0.1)
clean_min = st.sidebar.slider("Limpieza e higiene", 0.0, 5.0, 0.0, 0.1)
food_min = st.sidebar.slider("Gastronomía", 0.0, 5.0, 0.0, 0.1)
lifts_min = st.sidebar.slider("Remontes y teleféricos", 0.0, 5.0, 0.0, 0.1)
snowpark_min = st.sidebar.slider("Snowpark", 0.0, 5.0, 0.0, 0.1)
families_min = st.sidebar.slider("Familias y niños", 0.0, 5.0, 0.0, 0.1)
fiesta_min = st.sidebar.slider("Fiesta / Après-ski", 0.0, 5.0, 0.0, 0.1)

num_recomendaciones = st.sidebar.slider("Número de recomendaciones", 3, 5, 5)

df_filtrado = df[
    (df[COL_CONTINENTE].isin(continente)) &
    (df[COL_PAIS].isin(pais)) &
    (df[COL_PRECIO_EUR] <= precio_max) &
    (df[COL_KM_TOTALES] >= km_min) &
    (df[COL_NIEVE] >= snow_min) &
    (df[COL_ALOJAMIENTO] >= alojamiento_min) &
    (df[COL_ACCESO] >= access_min) &
    (df[COL_SENALIZACION] >= orientation_min) &
    (df[COL_LIMPIEZA] >= clean_min) &
    (df[COL_GASTRONOMIA] >= food_min) &
    (df[COL_REMONTES] >= lifts_min) &
    (df[COL_SNOWPARK] >= snowpark_min) &
    (df[COL_FAMILIAS] >= families_min) &
    (df[COL_APRES] >= fiesta_min)
]

st.title("🎿 Ski Resort Recommender")
st.markdown(
    "Encuentra estaciones de esquí adaptadas a tu perfil, presupuesto y preferencias de viaje."
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Estaciones disponibles", len(df_filtrado))
col2.metric("Países", df_filtrado[COL_PAIS].nunique() if not df_filtrado.empty else 0)
col3.metric("Km esquiables de media", f"{df_filtrado[COL_KM_TOTALES].mean():.0f}" if not df_filtrado.empty else "0")
col4.metric("Precio forfait medio", f"{df_filtrado[COL_PRECIO_EUR].mean():.0f} €" if not df_filtrado.empty else "0 €")

st.divider()

if df_filtrado.empty:
    st.warning("No hay estaciones que cumplan todos los filtros seleccionados.")
    st.info(
        "Prueba a relajar algunos filtros. Para una recomendación realista, prioriza 2 o 3 preferencias clave: "
        "precio, kilómetros esquiables, nieve, familia, fiesta o snowpark."
    )

    st.subheader("🔎 Alternativa sugerida")

    alternativa = df[
        (df[COL_CONTINENTE].isin(continente)) &
        (df[COL_PAIS].isin(pais)) &
        (df[COL_KM_TOTALES] >= max(20, km_min * 0.5))
    ].sort_values([COL_VALORACION, COL_NIEVE, COL_KM_TOTALES], ascending=False).head(5)

    if not alternativa.empty:
        st.dataframe(
            alternativa[[COL_ESTACION, COL_PAIS, COL_KM_TOTALES, COL_PRECIO_EUR, COL_VALORACION, COL_NIEVE]],
            use_container_width=True
        )

else:
    recomendaciones = recomendar_estaciones(df_filtrado, perfil, tipo_viaje).head(num_recomendaciones)

    if recomendaciones.empty:
        st.warning(f"No hay estaciones válidas para el perfil {perfil}.")
        st.info("Por ejemplo, si eliges Freeride, solo se recomiendan estaciones con más de 0 km freeride.")
    else:
        st.subheader("🏔️ Estaciones recomendadas")

        for _, row in recomendaciones.iterrows():
            st.markdown(f"### {row[COL_ESTACION]} — {row[COL_PAIS]}")

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Score", f"{row['score_final']:.2f}")
            c2.metric("Km esquiables", f"{row[COL_KM_TOTALES]:.0f} km")
            c3.metric("Forfait", f"{row[COL_PRECIO_EUR]:.0f} €")
            c4.metric("€/km", f"{row[COL_PRECIO_KM_EUR]:.2f} €")
            c5.metric("Valoración", f"{row[COL_VALORACION]:.1f}")

            razones = []

            if perfil == "Principiante":
                razones.append(f"{row[COL_KM_FACILES]:.0f} km de pistas fáciles")
            elif perfil == "Intermedio":
                razones.append(f"{row[COL_KM_INTERMEDIOS]:.0f} km de pistas intermedias")
            elif perfil == "Experto":
                razones.append(f"{row[COL_KM_DIFICILES]:.0f} km de pistas difíciles")
            elif perfil == "Freeride":
                razones.append(f"{row[COL_KM_FREERIDE]:.0f} km de freeride")

            if tipo_viaje == "Familia":
                razones.append(f"buena valoración para familias ({row[COL_FAMILIAS]:.1f})")
            elif tipo_viaje == "Fiesta":
                razones.append(f"buena oferta de fiesta y après-ski ({row[COL_APRES]:.1f})")
            elif tipo_viaje == "Barato":
                razones.append(f"precio competitivo por km ({row[COL_PRECIO_KM_EUR]:.2f} €/km)")
            elif tipo_viaje == "Snowpark":
                razones.append(f"snowparks bien valorados ({row[COL_SNOWPARK]:.1f})")
            elif tipo_viaje == "Gastronomía":
                razones.append(f"buena gastronomía ({row[COL_GASTRONOMIA]:.1f})")

            razones.append(f"fiabilidad de nieve de {row[COL_NIEVE]:.1f}")

            st.write("Esta estación destaca por " + ", ".join(razones) + ".")

            with st.expander("Ver detalles"):
                detalle = pd.DataFrame({
                    "Métrica": [
                        "Continente",
                        "País",
                        "Altitud",
                        "Km fáciles",
                        "Km intermedios",
                        "Km difíciles",
                        "Km freeride",
                        "Acceso y aparcamiento",
                        "Señalización",
                        "Limpieza e higiene",
                        "Gastronomía",
                        "Remontes y teleféricos",
                        "Snowpark",
                        "Alojamiento en pistas",
                        "Familias y niños",
                        "Fiesta / Après-ski",
                    ],
                    "Valor": [
                        row[COL_CONTINENTE],
                        row[COL_PAIS],
                        row[COL_ALTITUD],
                        row[COL_KM_FACILES],
                        row[COL_KM_INTERMEDIOS],
                        row[COL_KM_DIFICILES],
                        row[COL_KM_FREERIDE],
                        row[COL_ACCESO],
                        row[COL_SENALIZACION],
                        row[COL_LIMPIEZA],
                        row[COL_GASTRONOMIA],
                        row[COL_REMONTES],
                        row[COL_SNOWPARK],
                        row[COL_ALOJAMIENTO],
                        row[COL_FAMILIAS],
                        row[COL_APRES],
                    ]
                })

                st.dataframe(detalle, use_container_width=True)

            st.divider()

st.subheader("📊 Comparador de estaciones")

opciones = sorted(df_filtrado[COL_ESTACION].unique()) if not df_filtrado.empty else []

seleccion = st.multiselect(
    "Selecciona estaciones para comparar",
    opciones,
    default=list(recomendaciones[COL_ESTACION].head(3)) if not df_filtrado.empty and "recomendaciones" in locals() and not recomendaciones.empty else []
)

if seleccion:
    df_comp = df_filtrado[df_filtrado[COL_ESTACION].isin(seleccion)]

    columnas_comp = [
        COL_ESTACION,
        COL_PAIS,
        COL_KM_TOTALES,
        COL_KM_FACILES,
        COL_KM_INTERMEDIOS,
        COL_KM_DIFICILES,
        COL_KM_FREERIDE,
        COL_PRECIO_EUR,
        COL_PRECIO_KM_EUR,
        COL_VALORACION,
        COL_NIEVE,
        COL_APRES,
        COL_FAMILIAS,
        COL_SNOWPARK,
        COL_GASTRONOMIA,
    ]

    st.dataframe(df_comp[columnas_comp], use_container_width=True)
