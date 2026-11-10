"""Dashboard interactivo de notas — Programación 2.
Ejecutar: streamlit run app.py
"""
from pathlib import Path
from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard interactivo de notas", page_icon="📘", layout="wide")

st.markdown("""<style>
.block-container {padding-top: 2.2rem; padding-bottom: 2rem}
[data-testid="stSidebar"] {background: #f0f2f6}
[data-testid="stMetricValue"] {font-size: 2rem}
</style>""", unsafe_allow_html=True)

REQUIRED = {"id", "estudiante", "sexo", "seccion", "nota_1", "nota_2", "asistencia"}

@st.cache_data(show_spinner=False)
def leer_csv(contenido: bytes) -> pd.DataFrame:
    # utf-8-sig elimina la marca BOM que suelen exportar las hojas de cálculo.
    datos = pd.read_csv(BytesIO(contenido), encoding="utf-8-sig", sep=None, engine="python")
    datos.columns = datos.columns.str.strip().str.lower()
    faltantes = REQUIRED - set(datos.columns)
    if faltantes:
        raise ValueError("Faltan columnas: " + ", ".join(sorted(faltantes)))
    for campo in ("nota_1", "nota_2", "asistencia"):
        datos[campo] = pd.to_numeric(datos[campo], errors="coerce")
    datos = datos.dropna(subset=["nota_1", "nota_2", "asistencia"]).copy()
    if datos.empty:
        raise ValueError("El archivo no contiene notas y asistencias válidas.")
    if not datos["nota_1"].between(1, 7).all() or not datos["nota_2"].between(1, 7).all():
        raise ValueError("Las notas deben estar entre 1,0 y 7,0.")
    if not datos["asistencia"].between(0, 100).all():
        raise ValueError("La asistencia debe estar entre 0 y 100 %.")
    datos["promedio"] = (datos["nota_1"] * 0.5 + datos["nota_2"] * 0.5).round(2)
    datos["aprobado"] = datos["promedio"] >= 4.0
    return datos

st.sidebar.header("Datos y filtros")
archivo = st.sidebar.file_uploader("Carga el archivo de estudiantes", type=["csv"], help="Columnas: id, estudiante, sexo, seccion, nota_1, nota_2 y asistencia")
try:
    contenido = archivo.getvalue() if archivo is not None else (Path(__file__).parent / "estudiantes_notas.csv").read_bytes()
    df = leer_csv(contenido)
except (ValueError, OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
    st.error(f"No fue posible cargar el CSV: {error}")
    st.stop()

sexos = sorted(df["sexo"].dropna().astype(str).unique().tolist())
secciones = sorted(df["seccion"].dropna().astype(str).unique().tolist())
sexo_filtro = st.sidebar.multiselect("Sexo", sexos, default=sexos)
seccion_filtro = st.sidebar.selectbox("Sección", ["Todas"] + secciones)
rango = st.sidebar.slider("Rango del promedio", min_value=1.0, max_value=7.0, value=(1.0, 7.0), step=0.1)
asistencia_minima = st.sidebar.number_input("Asistencia mínima (%)", min_value=0, max_value=100, value=0, step=5)
st.sidebar.caption("Los filtros se combinan. Quitar ambos sexos deja la selección vacía.")

filtrado = df.loc[
    df["sexo"].isin(sexo_filtro)
    & ((df["seccion"] == seccion_filtro) if seccion_filtro != "Todas" else True)
    & df["promedio"].between(*rango)
    & (df["asistencia"] >= asistencia_minima)
].copy()

st.title("Dashboard interactivo de notas")
st.caption("Explora los resultados de un curso combinando filtros. **Promedio:** 50 % de cada evaluación. **Aprobación del ejercicio:** promedio mayor o igual a 4,0. Datos ficticios.")
resumen_sexo = ", ".join(sexo_filtro) if sexo_filtro else "Ninguno"
st.write(f"**Filtros activos:** {resumen_sexo} · **Sección:** {seccion_filtro} · **Promedio:** {rango[0]:.1f} a {rango[1]:.1f} · **Asistencia mínima:** {asistencia_minima} %")

m1, m2, m3 = st.columns(3)
m1.metric("Estudiantes seleccionados", len(filtrado))
m2.metric("Promedio general", f"{filtrado['promedio'].mean():.2f}".replace(".", ",") if not filtrado.empty else "—")
m3.metric("Aprobación", f"{filtrado['aprobado'].mean() * 100:.2f} %".replace(".", ",") if not filtrado.empty else "—")

control1, control2 = st.columns([2, 1])
with control1:
    vista = st.radio("Gráfico", ["Notas por estudiante", "Promedio por sección"], horizontal=True)
with control2:
    mostrar_tabla = st.checkbox("Mostrar tabla", value=True)

if filtrado.empty:
    st.warning("No hay estudiantes con los filtros elegidos. Cambia uno o más filtros para ver resultados.")
else:
    grafico, tabla = st.columns([1.15, 1])
    with grafico:
        st.subheader("Visualización de notas")
        fig, ax = plt.subplots(figsize=(8, 4.3))
        if vista == "Notas por estudiante":
            serie = filtrado.sort_values("estudiante")
            ax.bar(serie["estudiante"], serie["promedio"], color="#1f77b4")
            ax.set_title("Promedio por estudiante")
            ax.set_xlabel("Estudiante")
            ax.tick_params(axis="x", labelrotation=35)
        else:
            serie = filtrado.groupby("seccion", sort=True)["promedio"].mean()
            ax.bar(serie.index.astype(str), serie.values, color="#1f77b4")
            ax.set_title("Promedio por sección")
            ax.set_xlabel("Sección")
        ax.axhline(4.0, color="#e44c4c", linestyle="--", linewidth=1.5, label="Aprobación: 4,0")
        ax.set_ylabel("Promedio de notas")
        ax.set_ylim(0, 7)
        ax.legend(loc="upper right", frameon=False)
        fig.tight_layout()
        st.pyplot(fig, clear_figure=True)
        plt.close(fig)
    with tabla:
        if mostrar_tabla:
            st.subheader("Estudiantes seleccionados")
            vista_tabla = filtrado[["id", "estudiante", "sexo", "seccion", "promedio", "asistencia"]].rename(columns={
                "id": "ID", "estudiante": "Estudiante", "sexo": "Sexo", "seccion": "Sección", "promedio": "Promedio", "asistencia": "Asistencia (%)"
            })
            st.dataframe(vista_tabla, hide_index=True, use_container_width=True)
        else:
            st.info("Activa «Mostrar tabla» para ver los estudiantes seleccionados.")
    descarga = filtrado[["id", "estudiante", "sexo", "seccion", "nota_1", "nota_2", "promedio", "asistencia"]]
    st.download_button("Descargar selección CSV", data=descarga.to_csv(index=False).encode("utf-8-sig"), file_name="estudiantes_filtrados.csv", mime="text/csv")
    st.caption(f"Mostrando {len(filtrado)} de {len(df)} estudiantes. La asistencia solo se usa como filtro; la aprobación depende del promedio.")
