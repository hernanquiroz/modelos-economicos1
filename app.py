
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import matplotlib.pyplot as plt
import io
import numpy as np
import base64
from PIL import Image

# --- Configuración de la página ---
st.set_page_config(page_title="Pizarra Económica Interactiva", layout="wide", initial_sidebar_state="collapsed")

# --- CSS Definitivo (Modo Quirófano) ---
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
    
    /* 1. Ocultar TODOS los menús y cabeceras nativos de Streamlit */
    #MainMenu, 
    header, 
    footer, 
    [data-testid="stHeader"], 
    [data-testid="stToolbar"], 
    [data-testid="stStatusWidget"],
    [data-testid="stAppViewBlockContainer"],
    
    /* 2. Ocultar el NUEVO menú principal de Streamlit (ahora abajo a la derecha) */
    [data-testid="stMainMenu"], 
    [data-testid="stMainMenuButton"],
    [data-testid="stMainMenuAvatar"],
    [data-testid="stMainMenuList"],
    [data-testid="stMainMenuOpen"],
    
    /* 3. Ocultar el botón de la nube de Streamlit Cloud */
    [data-testid="stCloudToolbar"],
    .stCloudToolbar,
    #st-cloud-toolbar,
    [data-testid="stAppCloudToolbar"],
    [data-testid="stFloatingActionButton"],
    
    /* 4. Trampa para cualquier botón flotante (por posición CSS) */
    button[style*="position: fixed"],
    div[style*="position: fixed"][style*="bottom"],
    iframe[style*="position: fixed"] {
        visibility: hidden !important;
        display: none !important;
        height: 0 !important;
        width: 0 !important;
        pointer-events: none !important;
        right: -1000px !important; 
        bottom: -1000px !important;
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
        visibility: visible !important;
        display: block !important;
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

def flecha_desplazamiento(ax, x, y_origen, y_destino):
    """Dibuja una flecha negra que muestra el desplazamiento de la curva por el choque."""
    ax.annotate(
        '', xy=(x, y_destino), xytext=(x, y_origen),
        arrowprops=dict(arrowstyle='->', color='black', linewidth=2, linestyle='--')
    )

# ==========================================
# MODELOS INTERACTIVOS CON CHOQUES (Curva Punteada Negra)
# ==========================================
def generar_fondo_is_lm(is_shift=0, lm_shift=0, choque=0, curva_choque="IS (Demanda)"):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Ingreso / Producto (Y)', 'Tasa de Interés (r)', 'Modelo IS-LM (Interactivo)')
    x = np.linspace(1, 9, 100)
    ax.plot(x, (8 + is_shift) - 0.7*x, 'b-', linewidth=3, label='IS (Bienes)')
    ax.plot(x, (1 + lm_shift) + 0.8*x, 'r-', linewidth=3, label='LM (Dinero)')
    
    x_eq = (7 + is_shift - lm_shift) / 1.5
    if 0 <= x_eq <= 10:
        y_eq = (1 + lm_shift) + 0.8 * x_eq
        ax.plot(x_eq, y_eq, 'ko', markersize=10)
        ax.text(x_eq + 0.2, y_eq + 0.5, 'Eq. Original', fontsize=11, fontweight='bold')

    # Simular Choque (Curva Punteada Negra sobre IS o LM, según selección)
    if choque != 0:
        if curva_choque == "IS (Demanda)":
            ax.plot(x, (8 + is_shift + choque) - 0.7*x, 'k--', linewidth=2.5, label=f'IS con Choque ({choque})')
            flecha_desplazamiento(ax, 6, (8 + is_shift) - 0.7*6, (8 + is_shift + choque) - 0.7*6)
            x_eq_c = (7 + is_shift + choque - lm_shift) / 1.5
        else:  # LM (Dinero)
            ax.plot(x, (1 + lm_shift + choque) + 0.8*x, 'k--', linewidth=2.5, label=f'LM con Choque ({choque})')
            flecha_desplazamiento(ax, 6, (1 + lm_shift) + 0.8*6, (1 + lm_shift + choque) + 0.8*6)
            x_eq_c = (7 + is_shift - lm_shift - choque) / 1.5
        if 0 <= x_eq_c <= 10:
            y_eq_c = (1 + lm_shift + (choque if curva_choque != "IS (Demanda)" else 0)) + 0.8 * x_eq_c
            if curva_choque == "IS (Demanda)":
                y_eq_c = (1 + lm_shift) + 0.8 * x_eq_c
            ax.plot(x_eq_c, y_eq_c, 'ko', markersize=8, fillstyle='none')
            ax.text(x_eq_c + 0.2, y_eq_c - 0.8, 'Eq. Choque', fontsize=10, color='black')

    ax.legend(loc='upper right', fontsize=11)
    return fig_to_image(fig)

def generar_fondo_oa_da(da_shift=0, oa_shift=0, choque=0, curva_choque="DA (Demanda Agregada)"):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Producto Real (Y)', 'Nivel de Precios (P)', 'Oferta y Demanda Agregada (Interactivo)')
    x = np.linspace(1, 9, 100)
    ax.plot(x, (9 + da_shift) - 0.8*x, 'b-', linewidth=3, label='Demanda Agregada (DA)')
    ax.plot(x, (1 + oa_shift) + 0.8*x, 'r-', linewidth=3, label='Oferta Agregada (OACP)')
    
    x_eq = (8 + da_shift - oa_shift) / 1.6
    if 0 <= x_eq <= 10:
        y_eq = (1 + oa_shift) + 0.8 * x_eq
        ax.plot(x_eq, y_eq, 'ko', markersize=10)
        ax.text(x_eq + 0.2, y_eq + 0.5, 'Equilibrio', fontsize=11, fontweight='bold')

    # Simular Choque (Curva DA u OA en Punteado Negro)
    if choque != 0:
        if curva_choque == "DA (Demanda Agregada)":
            ax.plot(x, (9 + da_shift + choque) - 0.8*x, 'k--', linewidth=2.5, label=f'DA con Choque ({choque})')
            flecha_desplazamiento(ax, 5, (9 + da_shift) - 0.8*5, (9 + da_shift + choque) - 0.8*5)
            x_eq_c = (8 + da_shift + choque - oa_shift) / 1.6
            y_eq_c = (1 + oa_shift) + 0.8 * x_eq_c
        else:  # OA (Oferta Agregada)
            ax.plot(x, (1 + oa_shift + choque) + 0.8*x, 'k--', linewidth=2.5, label=f'OA con Choque ({choque})')
            flecha_desplazamiento(ax, 5, (1 + oa_shift) + 0.8*5, (1 + oa_shift + choque) + 0.8*5)
            x_eq_c = (8 + da_shift - oa_shift - choque) / 1.6
            y_eq_c = (1 + oa_shift + choque) + 0.8 * x_eq_c
        if 0 <= x_eq_c <= 10:
            ax.plot(x_eq_c, y_eq_c, 'ko', markersize=8, fillstyle='none')
            ax.text(x_eq_c + 0.2, y_eq_c - 0.8, 'Eq. Choque', fontsize=10, color='black')

    ax.legend(loc='upper right', fontsize=11)
    return fig_to_image(fig)

def generar_fondo_phillips(inflacion_esperada=1, choque=0):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Tasa de Desempleo (u)', 'Tasa de Inflación (π)', 'Curva de Phillips (Interactiva)')
    x = np.linspace(1, 9, 100)
    y = inflacion_esperada + 8 / x
    ax.plot(x, y, 'g-', linewidth=3, label=f'Curva de Phillips (πe={inflacion_esperada})')
    ax.plot(4, inflacion_esperada + 2, 'ko', markersize=10)
    ax.text(4.2, inflacion_esperada + 2.5, 'Eq. Original', fontsize=11, fontweight='bold')

    # Simular Choque (Curva Punteada Negra)
    if choque != 0:
        y_choque = (inflacion_esperada + choque) + 8 / x
        ax.plot(x, y_choque, 'k--', linewidth=2.5, label=f'Curva con Choque ({choque:+.1f})')
        flecha_desplazamiento(ax, 4, inflacion_esperada + 2, (inflacion_esperada + choque) + 2)
        ax.plot(4, (inflacion_esperada + choque) + 2, 'ko', markersize=8, fillstyle='none')
        ax.text(4.2, (inflacion_esperada + choque) + 1.5, 'Eq. Choque', fontsize=10, color='black')

    ax.legend(loc='upper right', fontsize=11)
    return fig_to_image(fig)

def generar_fondo_fpp(recursos_x=10, recursos_y=10, choque=0):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Bien X (Ej. Alimentos)', 'Bien Y (Ej. Manufactura)', 'Frontera de Posibilidades de Producción')
    x = np.linspace(0, recursos_x, 100)
    y = recursos_y * np.sqrt(1 - (x/recursos_x)**2)
    ax.plot(x, y, 'purple', linewidth=3, label=f'FPP (Recursos={recursos_x}x{recursos_y})')

    # Simular Choque Tecnológico (FPP Punteada Negra)
    if choque != 0:
        new_x = recursos_x + choque
        new_y = recursos_y + choque
        if new_x > 0 and new_y > 0:
            x_c = np.linspace(0, new_x, 100)
            y_c = new_y * np.sqrt(1 - (x_c/new_x)**2)
            ax.plot(x_c, y_c, 'k--', linewidth=2.5, label=f'FPP con Choque ({choque:+.1f})')
            # Flecha de expansión desde la frontera original
            flecha_desplazamiento(ax, recursos_x*0.7, recursos_y*np.sqrt(1-0.49), new_y*np.sqrt(1-0.49))
    
    ax.legend(loc='upper right', fontsize=11)
    return fig_to_image(fig)

def generar_fondo_monopolio(demand_shift=0, mc_shift=0, choque=0, curva_choque="Demanda (D)"):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Cantidad (Q)', 'Precio / Costo (P, C)', 'Monopolio (Interactivo)')
    x = np.linspace(0.1, 9, 100)
    ax.plot(x, (10 + demand_shift) - x, 'b-', linewidth=3, label='Demanda (D)')
    ax.plot(x, (10 + demand_shift) - 2*x, 'b--', linewidth=2, label='Ingreso Marginal (IMg)')
    ax.plot(x, (2 + mc_shift) + 0.5*x, 'r-', linewidth=3, label='Costo Marginal (CMg)')
    
    q_eq = (8 + demand_shift - mc_shift) / 2.5
    if 0 <= q_eq <= 10:
        p_eq = (10 + demand_shift) - q_eq
        ax.plot(q_eq, p_eq, 'ko', markersize=10)
        ax.text(q_eq + 0.2, p_eq + 0.5, 'Eq. Original', fontsize=11, fontweight='bold')

    # Simular Choque (Curva Punteada Negra sobre D/IMg o CMg)
    if choque != 0:
        if curva_choque == "Demanda (D)":
            ax.plot(x, (10 + demand_shift + choque) - x, 'k--', linewidth=2.5, label=f'Demanda Choque ({choque})')
            ax.plot(x, (10 + demand_shift + choque) - 2*x, 'k:', linewidth=2.5, label='IMg Choque')
            flecha_desplazamiento(ax, 4, (10 + demand_shift) - 4, (10 + demand_shift + choque) - 4)
            q_eq_c = (8 + demand_shift + choque - mc_shift) / 2.5
            p_eq_c = (10 + demand_shift + choque) - q_eq_c
        else:  # Costos (CMg)
            ax.plot(x, (2 + mc_shift + choque) + 0.5*x, 'k--', linewidth=2.5, label=f'CMg Choque ({choque})')
            flecha_desplazamiento(ax, 6, (2 + mc_shift) + 0.5*6, (2 + mc_shift + choque) + 0.5*6)
            q_eq_c = (8 + demand_shift - mc_shift - choque) / 2.5
            p_eq_c = (10 + demand_shift) - q_eq_c
        if 0 <= q_eq_c <= 10:
            ax.plot(q_eq_c, p_eq_c, 'ko', markersize=8, fillstyle='none')
            ax.text(q_eq_c + 0.2, p_eq_c - 0.8, 'Eq. Choque', fontsize=10, color='black')

    ax.legend(loc='upper right', fontsize=10)
    return fig_to_image(fig)

def generar_fondo_krugman_comercio(cc_shift=0, pp_shift=0, choque=0, curva_choque="Costo Medio (CC)"):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Escala de Producción (Q)', 'Precio / Costo (P/C)', 'Nueva Teoría Comercio (Krugman)')
    x = np.linspace(1, 9, 100)
    ax.plot(x, (9 + cc_shift)/x + 1, 'g-', linewidth=3, label='Costo Medio (CC)')
    ax.plot(x, (10 + pp_shift) - 0.8*x, 'm-', linewidth=3, label='Precio (PP)')
    ax.plot(3.5, 3.6, 'ko', markersize=10)
    ax.text(3.7, 4.0, 'Eq. Original', fontsize=11, fontweight='bold')

    # Simular Choque (Curva Punteada Negra sobre CC o PP)
    if choque != 0:
        if curva_choque == "Costo Medio (CC)":
            ax.plot(x, (9 + cc_shift + choque)/x + 1, 'k--', linewidth=2.5, label=f'CC Choque ({choque})')
            flecha_desplazamiento(ax, 3, (9 + cc_shift)/3 + 1, (9 + cc_shift + choque)/3 + 1)
        else:  # Precio (PP)
            ax.plot(x, (10 + pp_shift + choque) - 0.8*x, 'k--', linewidth=2.5, label=f'PP Choque ({choque})')
            flecha_desplazamiento(ax, 3, (10 + pp_shift) - 0.8*3, (10 + pp_shift + choque) - 0.8*3)
        ax.plot(3.5 + choque*0.2, 3.6 - choque*0.2, 'ko', markersize=8, fillstyle='none')
        ax.text(3.7 + choque*0.2, 3.4 - choque*0.2, 'Eq. Choque', fontsize=10, color='black')

    ax.legend(loc='upper right', fontsize=11)
    return fig_to_image(fig)

def generar_fondo_enfermedad_holandesa(intensidad_auge=1.5, choque=0):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    configurar_ejes(ax, 'Tiempo (t)', 'Tipo de Cambio Real (TCR)', 'Enfermedad Holandesa (Interactiva)')
    x = np.linspace(0, 9, 100)
    y1 = 3 + 0.2*x
    y2 = np.where(x < 4, 3 + 0.2*x, 3 + 0.2*4 + intensidad_auge + 0.1*(x-4))
    ax.plot(x, y1, 'b--', linewidth=2, label='Tendencia Inicial')
    ax.plot(x, y2, 'r-', linewidth=3, label=f'Auge Materias Primas (Intensidad={intensidad_auge})')

    # Simular Choque de Boom (Línea Punteada Negra)
    if choque != 0:
        y3 = np.where(x < 4, 3 + 0.2*x, 3 + 0.2*4 + (intensidad_auge + choque) + 0.1*(x-4))
        ax.plot(x, y3, 'k--', linewidth=2.5, label=f'Auge con Choque Extra ({choque:+.1f})')
        flecha_desplazamiento(ax, 6, 3 + 0.2*4 + intensidad_auge + 0.1*2, 3 + 0.2*4 + (intensidad_auge + choque) + 0.1*2)

    ax.axvline(4, color='gray', linestyle=':', linewidth=2)
    ax.text(4.1, 8, 'Boom Precios', fontsize=11, color='red', fontweight='bold')
    ax.legend(loc='upper left', fontsize=11)
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
def generar_fondo_krugman_4q(shock_monetario=0, choque=0):
    fig, axs = plt.subplots(2, 2, figsize=(12, 6.5))
    fig.suptitle('Modelo de Krugman: Ajuste de Activos y Precios (4 Cuadrantes)', fontsize=16, fontweight='bold', y=0.98)
    
    r_base = 5 - shock_monetario * 1.5
    E_base = 5 + shock_monetario * 1.5
    inflacion = 5 + shock_monetario * 1.5
    saldos_reales = 5 - shock_monetario * 1.5
    
    # Variables con Choque
    r_choque = 5 - (shock_monetario + choque) * 1.5
    E_choque = 5 + (shock_monetario + choque) * 1.5
    inflacion_choque = 5 + (shock_monetario + choque) * 1.5
    saldos_choque = 5 - (shock_monetario + choque) * 1.5
    
    # Q1
    ax1 = axs[0, 1]
    x1 = np.linspace(1, 10, 100)
    ax1.plot(x1, 10 - 0.8 * x1, 'g-', linewidth=2, label='Rendimiento Esperado')
    ax1.plot(E_base, r_base, 'ko', markersize=8)
    if choque != 0:
        # Curva de choque punteada negra (desplazamiento del rendimiento esperado)
        ax1.plot(x1, (10 + choque) - 0.8 * x1, 'k--', linewidth=2, label='Rend. con Choque')
        ax1.plot(E_choque, r_choque, 'ko', markersize=6, fillstyle='none')
    ax1.set_title('Q1: Mercado de Divisas', fontsize=11)
    ax1.set_xlabel('Tipo de Cambio (E) [$ sube ->]', fontsize=9)
    ax1.set_ylabel('Rendim. Moneda Local', fontsize=9)
    
    # Q2
    ax2 = axs[0, 0]
    x2 = np.linspace(1, 10, 100)
    ax2.plot(x2, 10 - 0.8 * x2, 'b-', linewidth=2, label='Demanda de Dinero L(r)')
    ax2.plot([saldos_reales, saldos_reales], [0, 10], 'r-', linewidth=2, label='Oferta de Dinero (M/P)')
    ax2.plot(saldos_reales, r_base, 'ko', markersize=8)
    if choque != 0:
        ax2.plot([saldos_choque, saldos_choque], [0, 10], 'k--', linewidth=2, label='Oferta con Choque')
        ax2.plot(saldos_choque, r_choque, 'ko', markersize=6, fillstyle='none')
    ax2.set_title('Q2: Mercado Monetario', fontsize=11)
    ax2.set_xlabel('Saldos Reales (M/P)', fontsize=9)
    ax2.set_ylabel('Tasa de Interés (r)', fontsize=9)
    
    # Q3
    ax3 = axs[1, 0]
    x3 = np.linspace(1, 10, 100)
    ax3.plot(x3, 10 - 0.8 * x3, 'm-', linewidth=2, label='Precios vs Saldos Reales')
    ax3.plot(inflacion, 10 - 0.8*inflacion, 'ko', markersize=8)
    if choque != 0:
        # Curva de choque punteada negra (desplazamiento por inflación)
        ax3.plot(x3, (10 + choque) - 0.8 * x3, 'k--', linewidth=2, label='Precios con Choque')
        ax3.plot(inflacion_choque, 10 - 0.8*inflacion_choque, 'ko', markersize=6, fillstyle='none')
    ax3.set_title('Q3: Transmisión de Precios', fontsize=11)
    ax3.set_xlabel('Nivel de Precios / Inflación (P)', fontsize=9)
    ax3.set_ylabel('Saldos Reales (M/P)', fontsize=9)
    
    # Q4
    ax4 = axs[1, 1]
    x4 = np.linspace(1, 10, 100)
    ax4.plot(x4, 1 + 8/x4, 'c-', linewidth=2, label='Inflación vs T. Cambio')
    ax4.plot(E_base, 1 + 8/E_base, 'ko', markersize=8)
    if choque != 0:
        # Curva de choque punteada negra (desplazamiento inflacionario)
        ax4.plot(x4, (1 + choque) + 8/x4, 'k--', linewidth=2, label='Inflación con Choque')
        ax4.plot(E_choque, 1 + 8/E_choque, 'ko', markersize=6, fillstyle='none')
    ax4.set_title('Q4: Inflación y T. de Cambio', fontsize=11)
    ax4.set_xlabel('Tipo de Cambio (E)', fontsize=9)
    ax4.set_ylabel('Inflación (π)', fontsize=9)
    
    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.legend(loc='upper right', fontsize=8)
        
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
    stroke_width = st.slider("Grosor:", 1, 40, 5, help="Controla el grosor del lápiz y el tamaño del borrador.")

with col4:
    herramienta_opcion = st.selectbox("Herramienta:", ("✏️ Lápiz (Dibujar)", "🧽 Borrador", "↔️ Mover Trazos"))
    modo_map = {
        "✏️ Lápiz (Dibujar)": "freedraw",
        "🧽 Borrador": "eraser",
        "↔️ Mover Trazos": "transform"
    }
    drawing_mode = modo_map[herramienta_opcion]

with col5:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("️ Limpiar Pizarra", type="primary"):
        st.session_state["canvas_key"] = st.session_state.get("canvas_key", 0) + 1

st.markdown("---")
st.markdown("### 📈 Ajustar Parámetros del Modelo (Mueve las curvas para explicar)")

is_shift = 0; lm_shift = 0; da_shift = 0; oa_shift = 0
inflacion_esp = 1; rec_x = 10; rec_y = 10
dem_shift = 0; mc_shift = 0; cc_shift = 0; pp_shift = 0
intensidad = 1.5; shock_mon = 0; choque = 0
curva_choque = ""

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

# NUEVO CONTROL UNIFICADO PARA SIMULAR CHOQUES
if modelo != "Pizarra en Blanco":
    st.markdown("### ⚡ Simular Choque Exógeno (Curva Punteada Negra)")
    cc1, cc2 = st.columns([2, 3])
    with cc1:
        # Elegir a qué curva se le aplica el choque punteado negro
        opciones_curva = {
            "IS-LM (Keynesiano)": ("IS (Demanda)", "LM (Dinero)"),
            "OA-DA (Agregado)": ("DA (Demanda Agregada)", "OA (Oferta Agregada)"),
            "Monopolio": ("Demanda (D)", "Costos (CMg)"),
            "Krugman (Comercio)": ("Costo Medio (CC)", "Precio (PP)"),
        }
        if modelo in opciones_curva:
            curva_choque = st.radio("Curva que recibe el choque:", opciones_curva[modelo])
        else:
            curva_choque = ""
    with cc2:
        st.markdown("<br>", unsafe_allow_html=True)
        choque = st.slider("Intensidad del Choque (Desplazamiento Extra)", -3.0, 3.0, 0.0, 0.1, help="Mueve este control para dibujar una curva negra punteada que simule un desplazamiento adicional en el modelo.")

st.markdown("---")

# ==========================================
# LÓGICA DEL FONDO Y RENDERIZADO
# ==========================================
if modelo == "IS-LM (Keynesiano)": bg_image = generar_fondo_is_lm(is_shift, lm_shift, choque, curva_choque)
elif modelo == "OA-DA (Agregado)": bg_image = generar_fondo_oa_da(da_shift, oa_shift, choque, curva_choque)
elif modelo == "Curva de Phillips": bg_image = generar_fondo_phillips(inflacion_esp, choque)
elif modelo == "Frontera Posibilidades Producción": bg_image = generar_fondo_fpp(rec_x, rec_y, choque)
elif modelo == "Monopolio": bg_image = generar_fondo_monopolio(dem_shift, mc_shift, choque, curva_choque)
elif modelo == "Krugman (Comercio)": bg_image = generar_fondo_krugman_comercio(cc_shift, pp_shift, choque, curva_choque)
elif modelo == "Enfermedad Holandesa": bg_image = generar_fondo_enfermedad_holandesa(intensidad, choque)
elif modelo == "Krugman 4 Cuadrantes (T.Cambio/Inflación)": bg_image = generar_fondo_krugman_4q(shock_mon, choque)
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
