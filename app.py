import streamlit as st
import pandas as pd
import numpy as np

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="Ski Resort Recommender",
    page_icon="🎿",
    layout="wide"
)

# =========================
# CARGA DE DATOS
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/ski_resorts_powerbi.csv")

    # Nos quedamos con estaciones con datos completos
    df = df.dropna()

    # Filtramos estaciones relevantes para agencia de viajes
    if "Categoría tamaño" in df.columns:
        df = df[~df["Categoría tamaño"].isin(["Muy pequeña", "Pequeña"])]

    return df


df = load_data()

# =========================
# FUNCIONES
# =========================
def normalize(series):
    if series.max() == series.min():
        return series * 0
    return (series - series.min()) / (series.max() - series.min())


def recomendar_estaciones(data, perfil, tipo_viaje):
    data = data.copy()

    # Variables base
    data["score_valoracion"] = normalize(data["Valoración"])
    data["score_nieve"] = normalize(data["Fiabilidad de nieve"])
    data["score_km"] = normalize(data["Km totales"])

    # Precio: cuanto menor, mejor
    data["score_precio"] = 1 - normalize(data["Precio por km EUR"])

    # Perfil esquiador
    if perfil == "Principiante":
        data["score_perfil"] = normalize(data["Km fáciles"])
    elif perfil == "Intermedio":
        data["score_perfil"] = normalize(data["Km intermedios"])
    elif perfil == "Experto":
        data["score_perfil"] = normalize(data["Km difíciles"])
    elif perfil == "Freeride":
        data["score_perfil"] = normalize(data["Km freeride"])
    else:
        data["score_perfil"] = normalize(data["Km totales"])

    # Tipo de viaje
    if tipo_viaje == "Familia":
        data["score_viaje"] = normalize(data["Familias y niños"])
    elif tipo_viaje == "Après-ski":
        data["score_viaje"] = normalize(data["Après-ski"])
    elif tipo_viaje == "Calidad-precio":
        data["score_viaje"] = data["score_precio"]
    elif tipo_viaje == "Premium":
        data["score_viaje"] = normalize(data["Valoración"])
    else:
        data["score_viaje"] = normalize(data["Km totales"])

    data["score_final"] = (
        data["score_valoracion"] * 0.25 +
        data["score_nieve"] * 0.20 +
        data["score_km"] * 0.15 +
        data["score_precio"] * 0.15 +
        data["score_perfil"] * 0.15 +
        data["score_viaje"] * 0.10
    )

    return data.sort_values("score_final", ascending=False)


# =========================
# SIDEBAR
# =========================
st.sidebar.title("🎿 Preferencias del viaje")

continentes = sorted(df["Continente"].dropna().unique())
continente = st.sidebar.multiselect(
    "Continente",
    continentes,
    default=continentes
)

paises = sorted(df[df["Continente"].isin(continente)]["País"].dropna().unique())
pais = st.sidebar.multiselect(
    "País",
    paises,
    default=paises
)

perfil = st.sidebar.selectbox(
    "Perfil de esquiador",
    ["Principiante", "Intermedio", "Experto", "Freeride"]
)

tipo_viaje = st.sidebar.selectbox(
    "Tipo de viaje",
    ["Familia", "Après-ski", "Calidad-precio", "Premium", "General"]
)

precio_max = st.sidebar.slider(
    "Precio máximo forfait (€)",
    int(df["Precio forfait EUR"].min()),
    int(df["Precio forfait EUR"].max()),
    int(df["Precio forfait EUR"].quantile(0.75))
)

km_min = st.sidebar.slider(
    "Km esquiables mínimos",
    int(df["Km totales"].min()),
    int(df["Km totales"].max()),
    50
)

nieve_min = st.sidebar.slider(
    "Fiabilidad de nieve mínima",
    float(df["Fiabilidad de nieve"].min()),
    float(df["Fiabilidad de nieve"].max()),
    float(df["Fiabilidad de nieve"].median())
)

num_recomendaciones = st.sidebar.slider(
    "Número de recomendaciones",
    3,
    5,
    5
)

# =========================
# FILTRADO
# =========================
df_filtrado = df[
    (df["Continente"].isin(continente)) &
    (df["País"].isin(pais)) &
    (df["Precio forfait EUR"] <= precio_max) &
    (df["Km totales"] >= km_min) &
    (df["Fiabilidad de nieve"] >= nieve_min)
]

# =========================
# HEADER
# =========================
st.title("🎿 Ski Resort Recommender")
st.markdown(
    "Encuentra estaciones de esquí adaptadas a tu presupuesto, perfil de esquiador y tipo de viaje."
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Estaciones disponibles", len(df_filtrado))
col2.metric("Países", df_filtrado["País"].nunique())
col3.metric("Km medios", f"{df_filtrado['Km totales'].mean():.0f}")
col4.metric("Precio medio", f"{df_filtrado['Precio forfait EUR'].mean():.0f} €")

st.divider()

# =========================
# RESULTADOS
# =========================
if df_filtrado.empty:
    st.warning("No hay estaciones que cumplan los filtros seleccionados.")
else:
    recomendaciones = recomendar_estaciones(
        df_filtrado,
        perfil,
        tipo_viaje
    ).head(num_recomendaciones)

    st.subheader("🏔️ Estaciones recomendadas")

    for i, row in recomendaciones.iterrows():
        with st.container():
            st.markdown(f"### {row['Estación']} — {row['País']}")

            c1, c2, c3, c4, c5 = st.columns(5)

            c1.metric("Score", f"{row['score_final']:.2f}")
            c2.metric("Km esquiables", f"{row['Km totales']:.0f} km")
            c3.metric("Forfait", f"{row['Precio forfait EUR']:.0f} €")
            c4.metric("€/km", f"{row['Precio por km EUR']:.2f} €")
            c5.metric("Valoración", f"{row['Valoración']:.1f}")

            st.markdown("**Por qué se recomienda:**")

            razones = []

            if perfil == "Principiante":
                razones.append(f"tiene {row['Km fáciles']:.0f} km de pistas fáciles")
            elif perfil == "Intermedio":
                razones.append(f"tiene {row['Km intermedios']:.0f} km de pistas intermedias")
            elif perfil == "Experto":
                razones.append(f"tiene {row['Km difíciles']:.0f} km de pistas difíciles")
            elif perfil == "Freeride":
                razones.append(f"tiene {row['Km freeride']:.0f} km de freeride")

            if tipo_viaje == "Familia":
                razones.append(f"buena valoración para familias ({row['Familias y niños']:.1f})")
            elif tipo_viaje == "Après-ski":
                razones.append(f"buen après-ski ({row['Après-ski']:.1f})")
            elif tipo_viaje == "Calidad-precio":
                razones.append(f"buen precio por km esquiable ({row['Precio por km EUR']:.2f} €/km)")
            elif tipo_viaje == "Premium":
                razones.append(f"alta valoración general ({row['Valoración']:.1f})")

            razones.append(f"fiabilidad de nieve de {row['Fiabilidad de nieve']:.1f}")

            st.write("Esta estación destaca porque " + ", ".join(razones) + ".")

            with st.expander("Ver detalles"):
                detalle = {
                    "Continente": row["Continente"],
                    "País": row["País"],
                    "Altitud": row["Altitud"],
                    "Km fáciles": row["Km fáciles"],
                    "Km intermedios": row["Km intermedios"],
                    "Km difíciles": row["Km difíciles"],
                    "Km freeride": row["Km freeride"],
                    "Gastronomía": row["Gastronomía"],
                    "Après-ski": row["Après-ski"],
                    "Familias y niños": row["Familias y niños"],
                    "Snowparks": row["Snowparks"],
                    "Fiabilidad de nieve": row["Fiabilidad de nieve"],
                }

                st.dataframe(pd.DataFrame(detalle.items(), columns=["Métrica", "Valor"]))

            st.divider()

# =========================
# COMPARADOR
# =========================
st.subheader("📊 Comparador de estaciones")

opciones = sorted(df_filtrado["Estación"].unique())

seleccion = st.multiselect(
    "Selecciona estaciones para comparar",
    opciones,
    default=list(recomendaciones["Estación"].head(3)) if not df_filtrado.empty else []
)

if seleccion:
    df_comp = df_filtrado[df_filtrado["Estación"].isin(seleccion)]

    columnas_comp = [
        "Estación",
        "País",
        "Km totales",
        "Km fáciles",
        "Km intermedios",
        "Km difíciles",
        "Km freeride",
        "Precio forfait EUR",
        "Precio por km EUR",
        "Valoración",
        "Fiabilidad de nieve",
        "Après-ski",
        "Familias y niños",
        "Snowparks"
    ]

    st.dataframe(df_comp[columnas_comp], use_container_width=True)

    st.scatter_chart(
        df_comp,
        x="Precio por km EUR",
        y="Valoración",
        size="Km totales",
        color="País"
    )