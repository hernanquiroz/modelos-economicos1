import streamlit as st
from streamlit_drawable_canvas import st_canvas
import matplotlib.pyplot as plt
import io
import numpy as np
import base64

# --- Configuración de la página ---
st.set_page_config(page_title="Pizarra Económica Interactiva", layout="wide", initial_sidebar_state="collapsed")

# --- CSS para Responsividad, TV y Lápiz Óptico ---
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0;
        max-width: 100%;
    }
    canvas {
        touch-action: none;
        -ms-touch-action: none;
    }
    #MainMenu, footer, header {visibility: hidden;}
    .stButton>button {
        width: 100%;
        height: 40px;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# FUNCIONES DE GENERACIÓN DE FONDOS (16:9)
# ==========================================
def fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    return buf.getvalue()

def configurar_ejes(ax, xlabel, ylabel, title):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axhline(0, color='black', linewidth=2)
    ax.axvline(0, color='black', linewidth=2)
    ax.set_xlabel(xlabel, fontsize=14, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=14, fontweight='bold')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
    ax.grid(True, linestyle='--', alpha=0.4)

def generar_fondo_is_lm():
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Ingreso / Producto (Y)', 'Tasa de Interés (r)', 'Modelo IS-LM (Keynesiano)')
    x = np.linspace(1, 9, 100)
    ax.plot(x, 8 - 0.7*x, 'b-', linewidth=3, label='IS (Bienes)')
    ax.plot(x, 1 + 0.8*x, 'r-', linewidth=3, label='LM (Dinero)')
    ax.plot(4.1, 4.3, 'ko', markersize=10)
    ax.text(4.3, 4.8, 'Equilibrio', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=12)
    return fig_to_bytes(fig)

def generar_fondo_oa_da():
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Producto Real (Y)', 'Nivel de Precios (P)', 'Oferta y Demanda Agregada (OA-DA)')
    x = np.linspace(1, 9, 100)
    ax.plot(x, 9 - 0.8*x, 'b-', linewidth=3, label='Demanda Agregada (DA)')
    ax.plot(x, 1 + 0.8*x, 'r-', linewidth=3, label='Oferta Agregada (OACP)')
    ax.plot(5, 5, 'ko', markersize=10)
    ax.text(5.2, 5.3, 'Equilibrio', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=12)
    return fig_to_bytes(fig)

def generar_fondo_phillips():
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Tasa de Desempleo (u)', 'Tasa de Inflación (π)', 'Curva de Phillips (Corto Plazo)')
    x = np.linspace(1, 9, 100)
    y = 1 + 8 / x
    ax.plot(x, y, 'g-', linewidth=3, label='Curva de Phillips')
    ax.plot(4, 3, 'ko', markersize=10)
    ax.text(4.2, 3.5, 'Punto A', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=12)
    return fig_to_bytes(fig)

def generar_fondo_fpp():
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Bien X (Ej. Alimentos)', 'Bien Y (Ej. Manufactura)', 'Frontera de Posibilidades de Producción (FPP)')
    x = np.linspace(0, 10, 100)
    y = np.sqrt(100 - x**2)
    ax.plot(x, y, 'purple', linewidth=3, label='FPP')
    ax.plot(3, 3, 'ro', markersize=8, label='Ineficiente')
    ax.plot(7, 7, 'bx', markersize=10, markeredgewidth=3, label='Inalcanzable')
    ax.legend(loc='upper right', fontsize=12)
    return fig_to_bytes(fig)

def generar_fondo_monopolio():
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Cantidad (Q)', 'Precio / Costo (P, C)', 'Monopolio vs. Competencia Perfecta')
    x = np.linspace(0.1, 9, 100)
    ax.plot(x, 10 - x, 'b-', linewidth=3, label='Demanda (D)')
    ax.plot(x, 10 - 2*x, 'b--', linewidth=2, label='Ingreso Marginal (IMg)')
    ax.plot(x, 2 + 0.5*x, 'r-', linewidth=3, label='Costo Marginal (CMg)')
    
    q_eq = 3.2
    p_eq = 10 - q_eq
    ax.axvline(q_eq, color='gray', linestyle=':', linewidth=1.5)
    ax.axhline(p_eq, color='gray', linestyle=':', linewidth=1.5)
    ax.plot(q_eq, p_eq, 'ko', markersize=10)
    ax.text(q_eq + 0.2, p_eq + 0.5, 'Equilibrio\nMonopólico', fontsize=11, fontweight='bold')
    ax.legend(loc='upper right', fontsize=11)
    return fig_to_bytes(fig)

def generar_fondo_krugman():
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Escala de Producción (Q)', 'Precio / Costo (P/C)', 'Nueva Teoría Comercio (Krugman)')
    x = np.linspace(1, 9, 100)
    ax.plot(x, 9/x + 1, 'g-', linewidth=3, label='Costo Medio (CC)')
    ax.plot(x, 10 - 0.8*x, 'm-', linewidth=3, label='Precio (PP)')
    ax.plot(3.5, 3.6, 'ko', markersize=10)
    ax.text(3.7, 4.0, 'Equilibrio', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=12)
    return fig_to_bytes(fig)

def generar_fondo_enfermedad_holandesa():
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Tiempo (t)', 'Tipo de Cambio Real (TCR)', 'Enfermedad Holandesa (Colombia)')
    x = np.linspace(0, 9, 100)
    y1 = 3 + 0.2*x
    y2 = np.where(x < 4, 3 + 0.2*x, 3 + 0.2*4 + 1.5 + 0.1*(x-4))
    ax.plot(x, y1, 'b--', linewidth=2, label='Tendencia Inicial')
    ax.plot(x, y2, 'r-', linewidth=3, label='Auge Materias Primas')
    ax.axvline(4, color='gray', linestyle=':', linewidth=2)
    ax.text(4.1, 8, 'Boom Precios', fontsize=11, color='red', fontweight='bold')
    ax.legend(loc='upper left', fontsize=12)
    return fig_to_bytes(fig)

def generar_fondo_blanco():
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    return fig_to_bytes(fig)

# ==========================================
# INTERFAZ DE USUARIO
# ==========================================
st.title("📊 Pizarra Económica Interactiva")

col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])

with col1:
    modelo = st.selectbox(
        "Modelo Económico:",
        ("Pizarra en Blanco", "IS-LM (Keynesiano)", "OA-DA (Agregado)", "Curva de Phillips", 
         "Frontera Posibilidades Producción", "Monopolio", "Krugman (Comercio)", "Enfermedad Holandesa")
    )

with col2:
    stroke_color = st.color_picker("Color:", "#000000")

with col3:
    stroke_width = st.slider("Grosor:", 1, 20, 5)

with col4:
    drawing_mode = st.selectbox("Herramienta:", ("freedraw", "eraser", "transform"))

with col5:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("️ Limpiar Pizarra", type="primary"):
        st.session_state["canvas_key"] = st.session_state.get("canvas_key", 0) + 1

# ==========================================
# LÓGICA DEL FONDO Y RENDERIZADO
# ==========================================
mapa_modelos = {
    "Pizarra en Blanco": generar_fondo_blanco,
    "IS-LM (Keynesiano)": generar_fondo_is_lm,
    "OA-DA (Agregado)": generar_fondo_oa_da,
    "Curva de Phillips": generar_fondo_phillips,
    "Frontera Posibilidades Producción": generar_fondo_fpp,
    "Monopolio": generar_fondo_monopolio,
    "Krugman (Comercio)": generar_fondo_krugman,
    "Enfermedad Holandesa": generar_fondo_enfermedad_holandesa
}

bg_image = mapa_modelos[modelo]()

# ✅ CORREGIDO: Se eliminó display_toolbar y se usaron solo parámetros válidos
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_image=bg_image,
    drawing_mode=drawing_mode,
    key=f"canvas_{st.session_state.get('canvas_key', 0)}",
    height=700,
    width=1200,
    update_streamlit=True,
)

# Botón de descarga
if canvas_result.image_data is not None and canvas_result.image_data.any():
    st.markdown("---")
    img_bytes = canvas_result.image_data
    b64 = base64.b64encode(img_bytes).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="pizarra_{modelo.replace(" ", "_")}.png" style="font-size: 18px; padding: 10px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 5px;">📥 Descargar Pizarra en PNG</a>'
    st.markdown(href, unsafe_allow_html=True)
