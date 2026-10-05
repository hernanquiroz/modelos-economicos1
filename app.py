import streamlit as st
from streamlit_drawable_canvas import st_canvas
import matplotlib.pyplot as plt
import io
import numpy as np
import base64
from PIL import Image

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
def fig_to_image(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    return Image.open(buf)

def configurar_ejes(ax, xlabel, ylabel, title):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axhline(0, color='black', linewidth=2)
    ax.axvline(0, color='black', linewidth=2)
    ax.set_xlabel(xlabel, fontsize=14, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=14, fontweight='bold')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
    ax.grid(True, linestyle='--', alpha=0.4)

# ==========================================
# FUNCIONES DE MODELOS INTERACTIVOS
# ==========================================
def generar_fondo_is_lm(is_shift=0, lm_shift=0):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Ingreso / Producto (Y)', 'Tasa de Interés (r)', 'Modelo IS-LM (Interactivo)')
    x = np.linspace(1, 9, 100)
    ax.plot(x, (8 + is_shift) - 0.7*x, 'b-', linewidth=3, label='IS (Bienes)')
    ax.plot(x, (1 + lm_shift) + 0.8*x, 'r-', linewidth=3, label='LM (Dinero)')
    
    # Punto de equilibrio dinámico
    x_eq = (7 + is_shift - lm_shift) / 1.5
    if 0 <= x_eq <= 10:
        y_eq = (1 + lm_shift) + 0.8 * x_eq
        ax.plot(x_eq, y_eq, 'ko', markersize=10)
        ax.text(x_eq + 0.2, y_eq + 0.5, 'Equilibrio', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=12)
    return fig_to_image(fig)

def generar_fondo_oa_da(da_shift=0, oa_shift=0):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Producto Real (Y)', 'Nivel de Precios (P)', 'Oferta y Demanda Agregada (Interactivo)')
    x = np.linspace(1, 9, 100)
    ax.plot(x, (9 + da_shift) - 0.8*x, 'b-', linewidth=3, label='Demanda Agregada (DA)')
    ax.plot(x, (1 + oa_shift) + 0.8*x, 'r-', linewidth=3, label='Oferta Agregada (OACP)')
    
    x_eq = (8 + da_shift - oa_shift) / 1.6
    if 0 <= x_eq <= 10:
        y_eq = (1 + oa_shift) + 0.8 * x_eq
        ax.plot(x_eq, y_eq, 'ko', markersize=10)
        ax.text(x_eq + 0.2, y_eq + 0.5, 'Equilibrio', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=12)
    return fig_to_image(fig)

def generar_fondo_phillips(inflacion_esperada=1):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Tasa de Desempleo (u)', 'Tasa de Inflación (π)', 'Curva de Phillips (Interactiva)')
    x = np.linspace(1, 9, 100)
    y = inflacion_esperada + 8 / x
    ax.plot(x, y, 'g-', linewidth=3, label=f'Curva de Phillips (πe={inflacion_esperada})')
    ax.plot(4, inflacion_esperada + 2, 'ko', markersize=10)
    ax.text(4.2, inflacion_esperada + 2.5, 'Punto A', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=12)
    return fig_to_image(fig)

def generar_fondo_fpp(recursos_x=10, recursos_y=10):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Bien X (Ej. Alimentos)', 'Bien Y (Ej. Manufactura)', 'Frontera de Posibilidades de Producción')
    x = np.linspace(0, recursos_x, 100)
    y = recursos_y * np.sqrt(1 - (x/recursos_x)**2)
    ax.plot(x, y, 'purple', linewidth=3, label=f'FPP (Recursos={recursos_x}x{recursos_y})')
    ax.legend(loc='upper right', fontsize=12)
    return fig_to_image(fig)

def generar_fondo_monopolio(demand_shift=0, mc_shift=0):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Cantidad (Q)', 'Precio / Costo (P, C)', 'Monopolio (Interactivo)')
    x = np.linspace(0.1, 9, 100)
    ax.plot(x, (10 + demand_shift) - x, 'b-', linewidth=3, label='Demanda (D)')
    ax.plot(x, (10 + demand_shift) - 2*x, 'b--', linewidth=2, label='Ingreso Marginal (IMg)')
    ax.plot(x, (2 + mc_shift) + 0.5*x, 'r-', linewidth=3, label='Costo Marginal (CMg)')
    
    # Equilibrio dinámico IMg = CMg
    q_eq = (8 + demand_shift - mc_shift) / 2.5
    if 0 <= q_eq <= 10:
        p_eq = (10 + demand_shift) - q_eq
        ax.axvline(q_eq, color='gray', linestyle=':', linewidth=1.5)
        ax.axhline(p_eq, color='gray', linestyle=':', linewidth=1.5)
        ax.plot(q_eq, p_eq, 'ko', markersize=10)
        ax.text(q_eq + 0.2, p_eq + 0.5, 'Eq. Monopólico', fontsize=11, fontweight='bold')
    ax.legend(loc='upper right', fontsize=11)
    return fig_to_image(fig)

def generar_fondo_krugman(cc_shift=0, pp_shift=0):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Escala de Producción (Q)', 'Precio / Costo (P/C)', 'Nueva Teoría Comercio (Krugman)')
    x = np.linspace(1, 9, 100)
    ax.plot(x, (9 + cc_shift)/x + 1, 'g-', linewidth=3, label='Costo Medio (CC)')
    ax.plot(x, (10 + pp_shift) - 0.8*x, 'm-', linewidth=3, label='Precio (PP)')
    ax.plot(3.5, 3.6, 'ko', markersize=10)
    ax.text(3.7, 4.0, 'Equilibrio', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=12)
    return fig_to_image(fig)

def generar_fondo_enfermedad_holandesa(intensidad_auge=1.5):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Tiempo (t)', 'Tipo de Cambio Real (TCR)', 'Enfermedad Holandesa (Interactiva)')
    x = np.linspace(0, 9, 100)
    y1 = 3 + 0.2*x
    y2 = np.where(x < 4, 3 + 0.2*x, 3 + 0.2*4 + intensidad_auge + 0.1*(x-4))
    ax.plot(x, y1, 'b--', linewidth=2, label='Tendencia Inicial')
    ax.plot(x, y2, 'r-', linewidth=3, label=f'Auge Materias Primas (Intensidad={intensidad_auge})')
    ax.axvline(4, color='gray', linestyle=':', linewidth=2)
    ax.text(4.1, 8, 'Boom Precios', fontsize=11, color='red', fontweight='bold')
    ax.legend(loc='upper left', fontsize=12)
    return fig_to_image(fig)

def generar_fondo_blanco():
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    return fig_to_image(fig)

# ==========================================
# INTERFAZ DE USUARIO
# ==========================================
st.title("📊 Pizarra Económica Interactiva")

# 1. Selección de Modelo y Herramientas de Dibujo
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

# 2. Parámetros Interactivos Dinámicos
st.markdown("---")
st.markdown("### 📈 Ajustar Parámetros del Modelo (Mueve las curvas para explicar)")

# Variables por defecto
is_shift = 0; lm_shift = 0; da_shift = 0; oa_shift = 0
inflacion_esp = 1; rec_x = 10; rec_y = 10
dem_shift = 0; mc_shift = 0; cc_shift = 0; pp_shift = 0
intensidad = 1.5

if modelo == "IS-LM (Keynesiano)":
    c1, c2 = st.columns(2)
    with c1: is_shift = st.slider("🔴 Política Fiscal (Desplazar curva IS)", -3.0, 3.0, 0.0, 0.1, help="Subir: Expansión fiscal. Bajar: Contracción fiscal.")
    with c2: lm_shift = st.slider("🔵 Política Monetaria (Desplazar curva LM)", -3.0, 3.0, 0.0, 0.1, help="Subir: Expansión monetaria. Bajar: Contracción monetaria.")

elif modelo == "OA-DA (Agregado)":
    c1, c2 = st.columns(2)
    with c1: da_shift = st.slider("🔴 Choque de Demanda Agregada", -3.0, 3.0, 0.0, 0.1)
    with c2: oa_shift = st.slider("🔵 Choque de Oferta Agregada", -3.0, 3.0, 0.0, 0.1)

elif modelo == "Curva de Phillips":
    inflacion_esp = st.slider("Inflación Esperada (πe)", 0.0, 4.0, 1.0, 0.1, help="Sube la curva completa si la inflación esperada aumenta.")

elif modelo == "Frontera Posibilidades Producción":
    c1, c2 = st.columns(2)
    with c1: rec_x = st.slider("Recursos/Tecnología para Bien X", 2, 12, 10)
    with c2: rec_y = st.slider("Recursos/Tecnología para Bien Y", 2, 12, 10)

elif modelo == "Monopolio":
    c1, c2 = st.columns(2)
    with c1: dem_shift = st.slider("🔴 Cambio en Demanda", -3.0, 3.0, 0.0, 0.1)
    with c2: mc_shift = st.slider("🔵 Cambio en Costos Marginales (Impuestos/Insumos)", -2.0, 4.0, 0.0, 0.1)

elif modelo == "Krugman (Comercio)":
    c1, c2 = st.columns(2)
    with c1: cc_shift = st.slider("Costos Medios (Economías de Escala)", -3.0, 3.0, 0.0, 0.1)
    with c2: pp_shift = st.slider("Precio de Mercado (Competencia)", -3.0, 3.0, 0.0, 0.1)

elif modelo == "Enfermedad Holandesa":
    intensidad = st.slider("Intensidad del Boom de Materias Primas", 0.0, 4.0, 1.5, 0.1)

st.markdown("---")

# ==========================================
# LÓGICA DEL FONDO Y RENDERIZADO
# ==========================================
if modelo == "IS-LM (Keynesiano)": bg_image = generar_fondo_is_lm(is_shift, lm_shift)
elif modelo == "OA-DA (Agregado)": bg_image = generar_fondo_oa_da(da_shift, oa_shift)
elif modelo == "Curva de Phillips": bg_image = generar_fondo_phillips(inflacion_esp)
elif modelo == "Frontera Posibilidades Producción": bg_image = generar_fondo_fpp(rec_x, rec_y)
elif modelo == "Monopolio": bg_image = generar_fondo_monopolio(dem_shift, mc_shift)
elif modelo == "Krugman (Comercio)": bg_image = generar_fondo_krugman(cc_shift, pp_shift)
elif modelo == "Enfermedad Holandesa": bg_image = generar_fondo_enfermedad_holandesa(intensidad)
else: bg_image = generar_fondo_blanco()

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
    return_image_data=True,
)

# Botón de descarga
if canvas_result.image_data is not None and canvas_result.image_data.any():
    st.markdown("---")
    img_array = canvas_result.image_data.astype(np.uint8)
    pil_img = Image.fromarray(img_array)
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    img_bytes = buf.getvalue()
    
    b64 = base64.b64encode(img_bytes).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="pizarra_{modelo.replace(" ", "_")}.png" style="font-size: 18px; padding: 10px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 5px;">📥 Descargar Pizarra en PNG</a>'
    st.markdown(href, unsafe_allow_html=True)
