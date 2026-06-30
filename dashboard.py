import streamlit as st
import pandas as pd
import plotly.express as px

# 🔹 Cargar datos
@st.cache_data
def cargar_datos():
    # Leer la primera hoja del Excel
    df = pd.read_excel('retail.xlsx')
    
    # Asegurar tipos numéricos (robusto frente a comas decimales o formatos de texto)
    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce')
    df['total'] = pd.to_numeric(df['total'], errors='coerce')
    df['precio_unitario'] = pd.to_numeric(df['precio_unitario'], errors='coerce')
    
    return df

df = cargar_datos()

# Convertir fecha a datetime
df['fecha'] = pd.to_datetime(df['fecha'])

# 🔍 Sidebar para filtros
st.sidebar.title("🔍 Filtros")
ciudad = st.sidebar.multiselect("Ciudad", sorted(df['ciudad'].dropna().unique()))
categoria = st.sidebar.multiselect("Categoría", sorted(df['categoria'].dropna().unique()))
metodo_pago = st.sidebar.multiselect("Método de Pago", sorted(df['metodo_pago'].dropna().unique()))

# Aplicar filtros
df_filtrado = df.copy()
if ciudad:
    df_filtrado = df_filtrado[df_filtrado['ciudad'].isin(ciudad)]
if categoria:
    df_filtrado = df_filtrado[df_filtrado['categoria'].isin(categoria)]
if metodo_pago:
    df_filtrado = df_filtrado[df_filtrado['metodo_pago'].isin(metodo_pago)]

# Validar si quedan datos tras filtrar
if df_filtrado.empty:
    st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados.")
    st.stop()

# 📊 KPIs
st.title("📊 Dashboard Retail")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 Ventas Totales", f"€{df_filtrado['total'].sum():,.2f}")
with col2:
    st.metric("🧾 Transacciones", len(df_filtrado))
with col3:
    st.metric("🛒 Ticket Promedio", f"€{df_filtrado['total'].mean():.2f}")
with col4:
    st.metric("📦 Productos Vendidos", int(df_filtrado['cantidad'].sum()))

# 📈 Gráfico: Ventas por categoría
st.subheader("📈 Ventas por Categoría")
ventas_cat = df_filtrado.groupby('categoria')['total'].sum().reset_index()
fig = px.bar(ventas_cat, x='categoria', y='total', color='categoria',
             labels={'categoria': 'Categoría', 'total': 'Total (€)'})
st.plotly_chart(fig, use_container_width=True)

# 📅 Gráfico: Evolución temporal
st.subheader("📅 Evolución de Ventas")
ventas_fecha = df_filtrado.groupby(df_filtrado['fecha'].dt.date)['total'].sum().reset_index()
fig2 = px.line(ventas_fecha, x='fecha', y='total', markers=True,
               labels={'fecha': 'Fecha', 'total': 'Total (€)'})
st.plotly_chart(fig2, use_container_width=True)

# 🔍 Tabla detallada
with st.expander("📋 Ver datos detallados"):
    st.dataframe(df_filtrado.head(100), use_container_width=True, hide_index=True)
