import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Taller 5 | MakerBox", layout="wide")

st.title("💧 Taller 5: Hidráulica y Efecto Venturi")
st.markdown("**Objetivo:** Validar el Principio de Bernoulli y la Ecuación de Continuidad simulando flujo incompresible (agua) en una cañería con reducción, para analizar las caídas de presión ($\Delta P$).")
st.divider()

# --- SECCIÓN 1: PARÁMETROS, PREVISUALIZACIÓN Y CÁLCULO TEÓRICO ---
st.header("1. Cálculo Analítico (Tubo de Venturi)")
st.write("Configura la geometría de la tubería y la velocidad de entrada. Asumiremos flujo ideal, incompresible y horizontal ($z_1 = z_2$).")

col1, col2, col3 = st.columns([1.2, 1.5, 1.2])

with col1:
    st.subheader("Variables del Sistema")
    
    st.markdown("**Fluido:** Agua a 20°C")
    rho = 998.0 # Densidad del agua en kg/m^3
    
    # Geometría
    D1 = st.slider("Diámetro Entrada D1 (mm)", 50.0, 200.0, 100.0, step=10.0)
    D2 = st.slider("Diámetro Garganta D2 (mm)", 10.0, float(D1 - 10), 50.0, step=5.0)
    
    # Condiciones de Borde
    V1 = st.number_input("Velocidad de Entrada V1 (m/s)", min_value=0.1, max_value=10.0, value=2.0, step=0.5)

with col2:
    st.subheader("Esquema de la Reducción (2D)")
    
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_alpha(0.0)
    ax.set_facecolor('none')
    
    # Dibujar el Tubo de Venturi
    L_total = 300
    L_recto = 80
    L_cono = 70
    
    y1 = D1 / 2
    y2 = D2 / 2
    
    # Puntos del contorno superior
    x_top = [0, L_recto, L_recto + L_cono, L_total - L_recto, L_total]
    y_top = [y1, y1, y2, y2, y1]
    
    # Puntos del contorno inferior
    x_bot = [0, L_recto, L_recto + L_cono, L_total - L_recto, L_total]
    y_bot = [-y1, -y1, -y2, -y2, -y1]
    
    # Dibujar paredes
    ax.plot(x_top, y_top, color='#2d2d2d', lw=3)
    ax.plot(x_bot, y_bot, color='#2d2d2d', lw=3)
    
    # Rellenar con fluido (Cian MakerBox)
    ax.fill_between(x_top, y_bot, y_top, color='#00aeef', alpha=0.3)
    
    # Vectores de velocidad (ilustrativos)
    ax.annotate("", xy=(L_recto/2, 0), xytext=(10, 0), arrowprops=dict(facecolor='#c72979', edgecolor='#c72979', width=2, headwidth=8))
    ax.text(L_recto/2, y1 + 10, f"V1 = {V1} m/s", color='#c72979', fontweight='bold', ha='center')
    
    # Conservación de masa: V2 es mayor que V1
    V2_teorica = V1 * ((D1/D2)**2)
    ax.annotate("", xy=(L_recto + L_cono + 30, 0), xytext=(L_recto + L_cono - 10, 0), arrowprops=dict(facecolor='#46247a', edgecolor='#46247a', width=2, headwidth=8))
    ax.text(L_recto + L_cono + 10, y2 + 10, f"V2 = {V2_teorica:.1f} m/s", color='#46247a', fontweight='bold', ha='center')
    
    ax.autoscale_view()
    ax.axis('equal')
    ax.axis('off')
    st.pyplot(fig, use_container_width=True)

with col3:
    st.subheader("Leyes de Conservación")
    
    # 1. Área
    A1 = np.pi * ((D1/1000) / 2)**2
    A2 = np.pi * ((D2/1000) / 2)**2
    
    # 2. Continuidad (Q1 = Q2) -> V1*A1 = V2*A2
    V2 = V1 * (A1 / A2)
    
    # 3. Bernoulli (z1 = z2). P1 + 0.5*rho*V1^2 = P2 + 0.5*rho*V2^2
    # Caída de presión DeltaP = P1 - P2 = 0.5 * rho * (V2^2 - V1^2)
    DeltaP_Pa = 0.5 * rho * (V2**2 - V1**2)
    DeltaP_kPa = DeltaP_Pa / 1000.0
    
    st.latex(r"A_1 V_1 = A_2 V_2")
    st.latex(r"P_1 + \frac{1}{2}\rho V_1^2 = P_2 + \frac{1}{2}\rho V_2^2")
    st.latex(r"\Delta P = \frac{1}{2}\rho (V_2^2 - V_1^2)")
    
    st.metric("Velocidad en la Garganta (V2)", f"{V2:.2f} m/s")
    st.metric("Caída de Presión Estática ($\Delta P$)", f"{DeltaP_kPa:.2f} kPa")
    
    if V2 > 15.0:
        st.warning("⚠️ Velocidad muy alta. Posible riesgo de cavitación si la presión absoluta cae por debajo de la presión de vapor del agua.")

st.divider()

# --- SECCIÓN 2: VALIDACIÓN DIGITAL (AUTODESK CFD) ---
st.header("2. Simulación de Fluidos en Autodesk CFD")

col4, col5 = st.columns(2)

with col4:
    st.markdown(f"""
    ### Fase A: Geometría y Setup
    1. **Modelado B-Rep:** En Fusion 360, dibuja el perfil 2D que ves arriba (solo la mitad superior) y usa la operación **Revolve** (Revolución) respecto al eje central para crear el volumen sólido que representa el *interior* de la tubería.
    2. Importa el modelo a Autodesk CFD.
    3. **Materials:** Asigna `Water` (Agua) al volumen.
    4. **Boundary Conditions (Condiciones de Contorno):**
        * Selecciona la cara circular de entrada (D1) y asigna una `Velocity` de **{V1} m/s**.
        * Selecciona la cara circular de salida y asigna una `Pressure` de **0 Pa** (Gauge/Manométrica). Esto le da a la simulación una referencia para resolver las ecuaciones de Navier-Stokes.
    """)

with col5:
    st.markdown(f"""
    ### Fase B: Resolución y Extracción de Datos
    1. **Mesh Size:** Aplica un tamaño de malla automático, pero refinado manualmente en la garganta cónica donde el gradiente de velocidad será mayor.
    2. **Solve:** Corre la simulación por unas 100 iteraciones hasta que las gráficas de convergencia se estabilicen.
    3. **Results:**
        * Crea un *Plano de Resultados* a la mitad del tubo.
        * Visualiza el contorno de **Velocity Magnitude**. Verifica si la velocidad máxima coincide con los **{V2:.2f} m/s** teóricos.
        * Cambia a contorno de **Static Pressure**. Mide la presión en la entrada y comprueba si la diferencia ($\Delta P$) es cercana a **{DeltaP_kPa:.2f} kPa**.
    """)
    st.info("💡 **Conexión Final:** Esta caída de presión es el Efecto Venturi. Si en lugar de agua fuera aire, y esta tubería fuera un carenado cilíndrico, esa zona de baja presión 'succionaría' aire adicional hacia la hélice, aumentando drásticamente el empuje total. ¡Ese es su proyecto final!")
