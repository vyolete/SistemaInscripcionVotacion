import streamlit as st

st.set_page_config(page_title="Concurso ITM - Dashboard", layout="wide")

st.image("https://c0.klipartz.com/pngpicture/349/183/gratis-png-instituto-tecnologico-metropolitano-de-medellin-universidad-itm-campus-prado-technology-institute-medellin.png", width=120)
st.title("Concurso de Analítica Financiera – Panel de Inscripciones")

# Métricas generales
st.metric("Total de equipos", data['Equipo'].nunique())
st.metric("Total de participantes", sum(data['Integrantes'].apply(lambda x: len(x.split(',')))))
st.metric("Total de docentes vinculados", data['Docente'].nunique())

# Filtro por docente
docente_sel = st.selectbox("Seleccione docente:", options=["Todos"] + data['Docente'].unique().tolist())

if docente_sel != "Todos":
    df_filtrado = data[data['Docente'] == docente_sel]
else:
    df_filtrado = data

# Tabla de detalle
st.dataframe(df_filtrado[['Equipo', 'Integrantes', 'Docente', 'Código']])

# Gráficos
import plotly.express as px

fig_bar = px.bar(df_filtrado.groupby('Docente')['Equipo'].nunique().reset_index(),
                 x='Docente', y='Equipo', labels={'Equipo': 'Número de equipos'})
st.plotly_chart(fig_bar, use_container_width=True)
