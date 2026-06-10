import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_gen import generar_envios

# ── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Logístico · Paquetería",
    page_icon="📦",
    layout="wide",
)

st.title("📦 Dashboard Operativo de Paquetería")
st.caption("Análisis de envíos nacionales · Datos simulados")

# ── Datos ────────────────────────────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    df = generar_envios(n=5000)
    df["mes"] = df["fecha_envio"].dt.to_period("M").astype(str)
    df["semana"] = df["fecha_envio"].dt.isocalendar().week
    return df

df_raw = cargar_datos()

# ── Sidebar: Filtros ─────────────────────────────────────────────────────────
st.sidebar.header("Filtros")

zonas_opciones = ["Todas"] + sorted(df_raw["zona"].unique().tolist())
zona_sel = st.sidebar.selectbox("Zona geográfica", zonas_opciones)

servicios_opciones = df_raw["servicio"].unique().tolist()
servicios_sel = st.sidebar.multiselect(
    "Tipo de servicio", servicios_opciones, default=servicios_opciones
)

meses_disponibles = sorted(df_raw["mes"].unique().tolist())
mes_inicio, mes_fin = st.sidebar.select_slider(
    "Rango de meses",
    options=meses_disponibles,
    value=(meses_disponibles[0], meses_disponibles[-1]),
)

# ── Aplicar filtros ───────────────────────────────────────────────────────────
df = df_raw.copy()
if zona_sel != "Todas":
    df = df[df["zona"] == zona_sel]
if servicios_sel:
    df = df[df["servicio"].isin(servicios_sel)]
df = df[(df["mes"] >= mes_inicio) & (df["mes"] <= mes_fin)]

# ── KPIs ─────────────────────────────────────────────────────────────────────
st.subheader("Indicadores Clave")
k1, k2, k3, k4 = st.columns(4)

total_envios     = len(df)
tasa_puntualidad = df["a_tiempo"].mean() * 100
ticket_promedio  = df["precio"].mean()
en_transito      = (df["estado_envio"] == "En tránsito").sum()

k1.metric("Total de envíos",        f"{total_envios:,}")
k2.metric("Entrega a tiempo",       f"{tasa_puntualidad:.1f}%")
k3.metric("Ticket promedio",        f"${ticket_promedio:,.0f} MXN")
k4.metric("Envíos en tránsito",     f"{en_transito:,}")

st.divider()

# ── Fila 1: Volumen mensual + Distribución por servicio ──────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Volumen mensual de envíos")
    vol_mensual = df.groupby("mes").size().reset_index(name="envios")
    fig_linea = px.line(
        vol_mensual, x="mes", y="envios",
        markers=True,
        labels={"mes": "Mes", "envios": "Envíos"},
    )
    fig_linea.update_layout(xaxis_tickangle=-45, height=320)
    st.plotly_chart(fig_linea, use_container_width=True)

with col2:
    st.subheader("Mix de servicios")
    mix = df["servicio"].value_counts().reset_index()
    mix.columns = ["servicio", "count"]
    fig_pie = px.pie(
        mix, names="servicio", values="count",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_pie.update_layout(height=320)
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# ── Fila 2: Rendimiento por zona + Tiempo de entrega por servicio ─────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Envíos y puntualidad por zona")
    zona_stats = (
        df.groupby("zona")
        .agg(envios=("id_envio", "count"), puntualidad=("a_tiempo", "mean"))
        .reset_index()
    )
    zona_stats["puntualidad_pct"] = (zona_stats["puntualidad"] * 100).round(1)
    fig_zona = px.bar(
        zona_stats.sort_values("envios", ascending=True),
        x="envios", y="zona",
        orientation="h",
        color="puntualidad_pct",
        color_continuous_scale="RdYlGn",
        range_color=[70, 100],
        labels={"envios": "Envíos", "zona": "", "puntualidad_pct": "% a tiempo"},
        text="puntualidad_pct",
    )
    fig_zona.update_traces(texttemplate="%{text}%", textposition="inside")
    fig_zona.update_layout(height=320)
    st.plotly_chart(fig_zona, use_container_width=True)

with col4:
    st.subheader("Días de entrega por servicio")
    fig_box = px.box(
        df, x="servicio", y="dias_entrega",
        color="servicio",
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={"servicio": "Servicio", "dias_entrega": "Días"},
    )
    fig_box.update_layout(showlegend=False, height=320)
    st.plotly_chart(fig_box, use_container_width=True)

st.divider()

# ── Fila 3: Incidencias ───────────────────────────────────────────────────────
st.subheader("Incidencias operativas")
col5, col6 = st.columns([1, 2])

with col5:
    incidencias = df[df["estado_envio"].isin(["Retrasado", "Devuelto", "Extraviado"])]
    inc_counts  = incidencias["estado_envio"].value_counts().reset_index()
    inc_counts.columns = ["estado", "count"]
    fig_inc = px.pie(
        inc_counts, names="estado", values="count",
        hole=0.4,
        color_discrete_sequence=["#f4a261", "#e76f51", "#e63946"],
        title="Distribución de incidencias"
    )
    fig_inc.update_layout(height=300)
    st.plotly_chart(fig_inc, use_container_width=True)

with col6:
    inc_mensual = (
        df[df["estado_envio"].isin(["Retrasado", "Devuelto", "Extraviado"])]
        .groupby(["mes", "estado_envio"])
        .size()
        .reset_index(name="count")
    )
    fig_inc_line = px.bar(
        inc_mensual, x="mes", y="count", color="estado_envio",
        barmode="stack",
        labels={"mes": "Mes", "count": "Incidencias", "estado_envio": "Tipo"},
        color_discrete_sequence=["#f4a261", "#e76f51", "#e63946"],
        title="Incidencias por mes"
    )
    fig_inc_line.update_layout(xaxis_tickangle=-45, height=300)
    st.plotly_chart(fig_inc_line, use_container_width=True)