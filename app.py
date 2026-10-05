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
    /* Ocultar TODOS los elementos nativos de Streamlit (Menú, Footer, Flechas) */
    #MainMenu, footer, header, #stDecoration, [data-testid="stToolbar"], .stDeployButton {
        visibility: hidden !important;
        display: none !important;
    }
    .stButton>button {
        width: 100%;
        height: 40px;
        font-size: 16px;
    }
    .leyenda-pie {
        text-align: center;
        font-size: 11px;
        color: #666;
        margin-top: 20px;
        font-family: sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# FUNCIONES DE GENERACIÓN DE FONDOS
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
# MODELOS INTERACTIVOS
# ==========================================
def generar_fondo_is_lm(is_shift=0, lm_shift=0):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Ingreso / Producto (Y)', 'Tasa de Interés (r)', 'Modelo IS-LM (Interactivo)')
    x = np.linspace(1, 9, 100)
    ax.plot(x, (8 + is_shift) - 0.7*x, 'b-', linewidth=3, label='IS (Bienes)')
    ax.plot(x, (1 + lm_shift) + 0.8*x, 'r-', linewidth=3, label='LM (Dinero)')
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
    q_eq = (8 + demand_shift - mc_shift) / 2.5
    if 0 <= q_eq <= 10:
        p_eq = (10 + demand_shift) - q_eq
        ax.axvline(q_eq, color='gray', linestyle=':', linewidth=1.5)
        ax.axhline(p_eq, color='gray', linestyle=':', linewidth=1.5)
        ax.plot(q_eq, p_eq, 'ko', markersize=10)
        ax.text(q_eq + 0.2, p_eq + 0.5, 'Eq. Monopólico', fontsize=11, fontweight='bold')
    ax.legend(loc='upper right', fontsize=11)
    return fig_to_image(fig)

def generar_fondo_krugman_comercio(cc_shift=0, pp_shift=0):
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
# MODELO: KRUGMAN 4 CUADRANTES
# ==========================================
def generar_fondo_krugman_4q(shock_monetario=0):
    fig, axs = plt.subplots(2, 2, figsize=(12, 6.5))
    fig.suptitle('Modelo de Krugman: Ajuste de Activos y Precios (4 Cuadrantes)', fontsize=16, fontweight='bold', y=0.98)
    
    r_base = 5 - shock_monetario * 1.5
    E_base = 5 + shock_monetario * 1.5
    inflacion = 5 + shock_monetario * 1.5
    saldos_reales = 5 - shock_monetario * 1.5
    
    # Q1
    ax1 = axs[0, 1]
    x1 = np.linspace(1, 10, 100)
    ax1.plot(x1, 10 - 0.8 * x1, 'g-', linewidth=2, label='Rendimiento Esperado')
    ax1.axhline(r_base, color='gray', linestyle='--', linewidth=1)
    ax1.plot(E_base, r_base, 'ko', markersize=8)
    ax1.set_title('Q1: Mercado de Divisas', fontsize=11)
    ax1.set_xlabel('Tipo de Cambio (E) [$ sube ->]', fontsize=9)
    ax1.set_ylabel('Rendim. Moneda Local', fontsize=9)
    
    # Q2
    ax2 = axs[0, 0]
    x2 = np.linspace(1, 10, 100)
    ax2.plot(x2, 10 - 0.8 * x2, 'b-', linewidth=2, label='Demanda de Dinero L(r)')
    ax2.plot([saldos_reales, saldos_reales], [0, 10], 'r-', linewidth=2, label='Oferta de Dinero (M/P)')
    ax2.plot(saldos_reales, r_base, 'ko', markersize=8)
    ax2.set_title('Q2: Mercado Monetario', fontsize=11)
    ax2.set_xlabel('Saldos Reales (M/P)', fontsize=9)
    ax2.set_ylabel('Tasa de Interés (r)', fontsize=9)
    
    # Q3
    ax3 = axs[1, 0]
    x3 = np.linspace(1, 10, 100)
    ax3.plot(x3, 10 - 0.8 * x3, 'm-', linewidth=2, label='Precios vs Saldos Reales')
    ax3.plot(inflacion, 10 - 0.8*inflacion, 'ko', markersize=8)
    ax3.set_title('Q3: Transmisión de Precios', fontsize=11)
    ax3.set_xlabel('Nivel de Precios / Inflación (P)', fontsize=9)
    ax3.set_ylabel('Saldos Reales (M/P)', fontsize=9)
    
    # Q4
    ax4 = axs[1, 1]
    x4 = np.linspace(1, 10, 100)
    ax4.plot(x4, 1 + 8/x4, 'c-', linewidth=2, label='Inflación vs T. Cambio')
    ax4.plot(E_base, 1 + 8/E_base, 'ko', markersize=8)
    ax4.set_title('Q4: Inflación y T. de Cambio', fontsize=11)
    ax4.set_xlabel('Tipo de Cambio (E)', fontsize=9)
    ax4.set_ylabel('Inflación (π)', fontsize=9)
    
    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.legend(loc='upper right', fontsize=8)
        
    color_flecha = 'red' if shock_monetario > 0 else 'blue' if shock_monetario < 0 else 'gray'
    if shock_monetario != 0:
        ax2.annotate('Interés ' + ('Baja' if shock_monetario > 0 else 'Sube'), xy=(saldos_reales, r_base), xytext=(saldos_reales+2, r_base+2),
                     arrowprops=dict(arrowstyle='->', color=color_flecha), fontsize=9, color=color_flecha, fontweight='bold')
        ax1.annotate('Dólar ' + ('Sube' if shock_monetario > 0 else 'Baja'), xy=(E_base, r_base), xytext=(E_base-2, r_base+2),
                     arrowprops=dict(arrowstyle='->', color=color_flecha), fontsize=9, color=color_flecha, fontweight='bold')
        ax3.annotate('Saldos ' + ('Caen' if shock_monetario > 0 else 'Suben'), xy=(inflacion, 10 - 0.8*inflacion), xytext=(inflacion+1, 10 - 0.8*inflacion+2),
                     arrowprops=dict(arrowstyle='->', color=color_flecha), fontsize=9, color=color_flecha, fontweight='bold')
        ax4.annotate('Inflación ' + ('Sube' if shock_monetario > 0 else 'Baja'), xy=(E_base, 1 + 8/E_base), xytext=(E_base-2, 1 + 8/E_base+2),
                     arrowprops=dict(arrowstyle='->', color=color_flecha), fontsize=9, color=color_flecha, fontweight='bold')
        
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    return fig_to_image(fig)

# ==========================================
# INTERFAZ DE USUARIO
# ==========================================
st.title("📊 Pizarra Económica Interactiva")

col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])

with col1:
    modelo = st.selectbox(
        "Modelo Económico:",
        ("Pizarra en Blanco", "IS-LM (Keynesiano)", "OA-DA (Agregado)", "Curva de Phillips", 
         "Frontera Posibilidades Producción", "Monopolio", "Krugman (Comercio)", "Enfermedad Holandesa",
         "Krugman 4 Cuadrantes (T.Cambio/Inflación)")
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

st.markdown("---")
st.markdown("### 📈 Ajustar Parámetros del Modelo (Mueve las curvas para explicar)")

is_shift = 0; lm_shift = 0; da_shift = 0; oa_shift = 0
inflacion_esp = 1; rec_x = 10; rec_y = 10
dem_shift = 0; mc_shift = 0; cc_shift = 0; pp_shift = 0
intensidad = 1.5; shock_mon = 0

if modelo == "IS-LM (Keynesiano)":
    c1, c2 = st.columns(2)
    with c1: is_shift = st.slider("🔴 Política Fiscal (Desplazar curva IS)", -3.0, 3.0, 0.0, 0.1)
    with c2: lm_shift = st.slider("🔵 Política Monetaria (Desplazar curva LM)", -3.0, 3.0, 0.0, 0.1)

elif modelo == "OA-DA (Agregado)":
    c1, c2 = st.columns(2)
    with c1: da_shift = st.slider("🔴 Choque de Demanda Agregada", -3.0, 3.0, 0.0, 0.1)
    with c2: oa_shift = st.slider("🔵 Choque de Oferta Agregada", -3.0, 3.0, 0.0, 0.1)

elif modelo == "Curva de Phillips":
    inflacion_esp = st.slider("Inflación Esperada (πe)", 0.0, 4.0, 1.0, 0.1)

elif modelo == "Frontera Posibilidades Producción":
    c1, c2 = st.columns(2)
    with c1: rec_x = st.slider("Recursos/Tecnología para Bien X", 2, 12, 10)
    with c2: rec_y = st.slider("Recursos/Tecnología para Bien Y", 2, 12, 10)

elif modelo == "Monopolio":
    c1, c2 = st.columns(2)
    with c1: dem_shift = st.slider("🔴 Cambio en Demanda", -3.0, 3.0, 0.0, 0.1)
    with c2: mc_shift = st.slider("🔵 Cambio en Costos Marginales", -2.0, 4.0, 0.0, 0.1)

elif modelo == "Krugman (Comercio)":
    c1, c2 = st.columns(2)
    with c1: cc_shift = st.slider("Costos Medios (Economías de Escala)", -3.0, 3.0, 0.0, 0.1)
    with c2: pp_shift = st.slider("Precio de Mercado (Competencia)", -3.0, 3.0, 0.0, 0.1)

elif modelo == "Enfermedad Holandesa":
    intensidad = st.slider("Intensidad del Boom de Materias Primas", 0.0, 4.0, 1.5, 0.1)

elif modelo == "Krugman 4 Cuadrantes (T.Cambio/Inflación)":
    shock_mon = st.slider("🔴 Política Monetaria (Subir: Expansiva / Bajar: Contractiva)", -3.0, 3.0, 0.0, 0.1)

st.markdown("---")

# ==========================================
# LÓGICA DEL FONDO Y RENDERIZADO
# ==========================================
if modelo == "IS-LM (Keynesiano)": bg_image = generar_fondo_is_lm(is_shift, lm_shift)
elif modelo == "OA-DA (Agregado)": bg_image = generar_fondo_oa_da(da_shift, oa_shift)
elif modelo == "Curva de Phillips": bg_image = generar_fondo_phillips(inflacion_esp)
elif modelo == "Frontera Posibilidades Producción": bg_image = generar_fondo_fpp(rec_x, rec_y)
elif modelo == "Monopolio": bg_image = generar_fondo_monopolio(dem_shift, mc_shift)
elif modelo == "Krugman (Comercio)": bg_image = generar_fondo_krugman_comercio(cc_shift, pp_shift)
elif modelo == "Enfermedad Holandesa": bg_image = generar_fondo_enfermedad_holandesa(intensidad)
elif modelo == "Krugman 4 Cuadrantes (T.Cambio/Inflación)": bg_image = generar_fondo_krugman_4q(shock_mon)
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

st.markdown('<div class="leyenda-pie">Pizarra diseñada por Ing. Hernán Quiroz</div>', unsafe_allow_html=True)
