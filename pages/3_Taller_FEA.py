import streamlit as st
import math

st.set_page_config(page_title="Taller 3 | MakerBox", layout="wide")

st.title("🖥️ Taller 3: Simulación FEA y Validación Teórica")
st.markdown("**Objetivo:** Contrastar el cálculo analítico de esfuerzos flexionantes con el Análisis de Elementos Finitos (FEA) usando los criterios de Von Mises.")
st.divider()

# --- SECCIÓN 1: CÁLCULO TEÓRICO (ENFOQUE HIBBELER) ---
st.header("1. Cálculo Analítico Preliminar (Modelo de Viga en Voladizo)")
st.write("Antes de simular la escuadra en Fusion 360, calcularemos el esfuerzo teórico en el empotramiento asumiendo una sección transversal rectangular pura.")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Parámetros del Problema")
    
    # Material
    st.markdown("**Material:** Acero Estructural A36")
    Sy = 250.0 # Límite elástico en MPa
    st.info(f"Límite de Fluencia ($S_y$): {Sy} MPa")
    
    # Cargas y Geometría
    P = st.number_input("Carga Aplicada P (N)", min_value=100.0, max_value=5000.0, value=500.0, step=100.0)
    L = st.slider("Longitud del brazo L (mm)", 50.0, 300.0, 150.0, step=10.0)
    base = st.slider("Base de la sección b (mm)", 5.0, 50.0, 10.0, step=1.0)
    altura = st.slider("Altura de la sección h (mm)", 10.0, 100.0, 30.0, step=2.0)

with col2:
    st.subheader("Ecuaciones de la Mecánica de Materiales")
    
    # Cálculos teóricos
    # 1. Momento Flector (N*mm)
    M = P * L
    # 2. Inercia (mm^4)
    I = (base * (altura**3)) / 12.0
    # 3. Distancia a la fibra más alejada (mm)
    c = altura / 2.0
    # 4. Esfuerzo Máximo (MPa = N/mm^2)
    sigma_max = (M * c) / I
    # 5. Factor de Seguridad
    factor_seguridad = Sy / sigma_max if sigma_max > 0 else 99.9

    st.latex(r"M_{max} = P \cdot L")
    st.latex(r"I = \frac{b \cdot h^3}{12}")
    st.latex(r"\sigma_{max} = \frac{M_{max} \cdot c}{I}")
    st.latex(r"\eta = \frac{S_y}{\sigma_{max}}")
    
    st.markdown("### Resultados Analíticos")
    c1, c2, c3 = st.columns(3)
    c1.metric("Momento Máximo", f"{M/1000:.2f} N·m")
    c2.metric("Esfuerzo Máximo ($\sigma$)", f"{sigma_max:.2f} MPa")
    
    # Alerta visual según el Factor de Seguridad
    if factor_seguridad < 1.0:
        c3.metric("Factor de Seg. ($\eta$)", f"{factor_seguridad:.2f}", "Falla Plástica", delta_color="inverse")
        st.error("⚠️ El diseño falla. El esfuerzo máximo supera el límite de fluencia del Acero A36.")
    elif factor_seguridad < 2.0:
        c3.metric("Factor de Seg. ($\eta$)", f"{factor_seguridad:.2f}", "Margen Crítico", delta_color="off")
        st.warning("⚡ El diseño es seguro, pero el factor de seguridad es bajo para aplicaciones dinámicas.")
    else:
        c3.metric("Factor de Seg. ($\eta$)", f"{factor_seguridad:.2f}", "Diseño Seguro")
        st.success("✅ Diseño estructuralmente seguro.")

st.divider()

# --- SECCIÓN 2: VALIDACIÓN DIGITAL (FUSION SIMULATION) ---
st.header("2. Validación Computacional en Fusion 360")
st.write("Ahora que conocemos el valor teórico esperado, llevaremos el modelo B-Rep al entorno de simulación para analizar la distribución real de esfuerzos de Von Mises, la cual incluye concentradores de esfuerzos (radios de acuerdo) que la teoría simple de vigas ignora.")

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    ### Configuración del Estudio Estático
    Sigue estrictamente este flujo de trabajo en el espacio **Simulation**:
    
    1. **Study:** Selecciona *Static Stress*.
    2. **Materials:** Asigna `Steel, A36` al cuerpo de la escuadra.
    3. **Constraints (Empotramiento):** Aplica una restricción *Fixed* en la cara posterior (la que iría unida a la pared o brida).
    4. **Loads (Cargas):** Aplica una fuerza de magnitud `P` (ej. 500 N) en la perforación del extremo libre. Asegúrate de que el vector de fuerza apunte hacia abajo (eje Y o Z negativo, según tu sistema de coordenadas).
    5. **Contacts:** Si tienes más de un cuerpo, usa *Automatic Contacts*. En este caso, al ser una sola pieza sólida, sáltate este paso.
    """)

with col4:
    st.markdown("""
    ### Solución y Análisis de Resultados
    Antes de presionar *Solve*, debemos asegurar la calidad de nuestro modelo matemático:
    
    * **Convergencia de Malla (Mesh):** Ve a la configuración de la malla y reduce el tamaño de los elementos en los radios interiores (donde esperamos concentración de esfuerzos).
    * **Solve:** Ejecuta la simulación (puedes usar el solver en la nube o local).
    * **Lectura de Resultados:**
        * Cambia el gráfico a **Esfuerzo de Von Mises**. ¿Cuál es el valor máximo? ¿Se acerca al $\sigma_{max}$ analítico?
        * Cambia el gráfico a **Safety Factor**. Compara el mínimo de la simulación con nuestro $\eta$ calculado arriba.
    """)
    st.info("💡 **Pregunta de Taller:** El esfuerzo simulado suele ser ligeramente mayor al calculado a mano. ¿Por qué ocurre esto? (Pista: Piensa en los concentradores de esfuerzos en las esquinas interiores).")
