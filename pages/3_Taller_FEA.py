import streamlit as st

st.set_page_config(page_title="Taller 3 | MakerBox", layout="wide")

st.title("🖥️ Taller 3: Simulación FEA y Validación Teórica")
st.markdown("**Objetivo:** Contrastar el cálculo analítico de esfuerzos flexionantes con el Análisis de Elementos Finitos (FEA) usando los criterios de Von Mises, partiendo de una geometría generada por código.")
st.divider()

# --- SECCIÓN 1: PARÁMETROS Y CÁLCULO TEÓRICO ---
st.header("1. Parámetros de la Escuadra y Cálculo Analítico")
st.write("Configura las dimensiones de la viga en voladizo (escuadra). El sistema calculará el esfuerzo teórico máximo asumiendo una sección transversal pura.")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Variables de Diseño")
    
    st.markdown("**Material:** Acero Estructural A36")
    Sy = 250.0 
    
    P = st.number_input("Carga Aplicada P (N)", min_value=100.0, max_value=5000.0, value=500.0, step=100.0)
    L = st.slider("Longitud del brazo libre L (mm)", 50.0, 300.0, 150.0, step=10.0)
    base = st.slider("Ancho de la sección b (mm)", 5.0, 50.0, 10.0, step=1.0)
    altura = st.slider("Altura de la sección h (mm)", 10.0, 100.0, 30.0, step=2.0)
    
    st.markdown("**Parámetros de Manufactura**")
    t_muro = st.slider("Espesor placa fijación (mm)", 5.0, 30.0, 15.0, step=1.0)
    h_muro = st.slider("Altura placa fijación (mm)", 50.0, 150.0, 80.0, step=5.0)
    r_fillet = st.slider("Radio de empalme interior (mm)", 0.0, 15.0, 5.0, step=1.0)

with col2:
    st.subheader("Mecánica de Materiales (Teoría)")
    
    M = P * L
    I = (base * (altura**3)) / 12.0
    c = altura / 2.0
    sigma_max = (M * c) / I
    factor_seguridad = Sy / sigma_max if sigma_max > 0 else 99.9

    st.latex(r"\sigma_{max} = \frac{M_{max} \cdot c}{I} \quad \rightarrow \quad \eta = \frac{S_y}{\sigma_{max}}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Momento Máx.", f"{M/1000:.2f} N·m")
    c2.metric("Esfuerzo Máx. ($\sigma$)", f"{sigma_max:.2f} MPa")
    
    if factor_seguridad < 1.0:
        c3.metric("Factor Seg. ($\eta$)", f"{factor_seguridad:.2f}", "Falla", delta_color="inverse")
    elif factor_seguridad < 2.0:
        c3.metric("Factor Seg. ($\eta$)", f"{factor_seguridad:.2f}", "Margen Crítico", delta_color="off")
    else:
        c3.metric("Factor Seg. ($\eta$)", f"{factor_seguridad:.2f}", "Seguro")

st.divider()

# --- SECCIÓN 2: GENERACIÓN DE GEOMETRÍA CSG ---
st.header("2. Generación de Geometría CSG (OpenSCAD)")
st.write("Copia este script dinámico en OpenSCAD. Usaremos un perfil 2D extruido linealmente para crear la escuadra. Nota cómo integramos el empalme (fillet) restando un círculo a un cuadrado para evitar la singularidad de esfuerzos en la esquina interior.")

codigo_openscad = f"""// --- PARÁMETROS GEOMÉTRICOS ---
L = {L};          // Longitud del brazo libre
b = {base};           // Ancho de la sección (extrusión)
h = {altura};          // Altura de la sección del brazo
t_muro = {t_muro};     // Espesor de la placa de fijación
h_muro = {h_muro};     // Altura de la placa de fijación
r_fillet = {r_fillet};   // Radio de empalme interior

// --- GENERACIÓN DEL SÓLIDO ---
// Extruimos el perfil 2D para generar el sólido 3D
linear_extrude(height = b) {{
    union() {{
        // Brazo horizontal
        translate([0, 0]) square([L, h]);
        
        // Placa de fijación vertical
        translate([-t_muro, -(h_muro-h)/2]) square([t_muro, h_muro]);
        
        // Empalme (Fillet) interior para disipar esfuerzos
        if (r_fillet > 0) {{
            translate([0, h]) difference() {{
                square([r_fillet, r_fillet]);
                translate([r_fillet, r_fillet]) circle(r=r_fillet, $fn=50);
            }}
        }}
    }}
}}
"""
st.code(codigo_openscad, language="openscad")
st.caption("Instrucciones: Pega en OpenSCAD -> Presiona F6 (Renderizar) -> Presiona F7 (Exportar STL).")

st.divider()

# --- SECCIÓN 3: VALIDACIÓN DIGITAL (FUSION SIMULATION) ---
st.header("3. Validación Computacional en Fusion 360")

col3, col4 = st.columns(2)

with col3:
    # Usamos f-string (f"") en lugar de .format()
    st.markdown(f"""
    ### Configuración FEA
    1. Importa el archivo `.stl` generado en OpenSCAD a Fusion 360.
    2. Convierte la malla a cuerpo sólido (Mesh to BRep).
    3. Pasa al espacio de trabajo **Simulation** y elige *Static Stress*.
    4. **Material:** Aplica `Steel, A36`.
    5. **Empotramiento:** Fija la cara posterior de la placa vertical.
    6. **Carga:** Aplica una fuerza de **{P} N** apuntando hacia abajo en la arista/cara final del brazo libre.
    """)

with col4:
    # Doble llave {{max}} para que Python no lo confunda con una variable
    st.markdown(f"""
    ### Análisis Crítico
    * Refina la malla en la zona del empalme (fillet).
    * Ejecuta la simulación (Solve).
    * Compara el **Esfuerzo de Von Mises Máximo** con el $\sigma_{{max}}$ teórico ({sigma_max:.2f} MPa).
    """)
    
    st.info("💡 **Reto Maker:** Juega con el deslizador del 'Radio de empalme' (dejándolo en 0 mm vs 15 mm), regenera el STL y simula de nuevo. Verás matemáticamente por qué las esquinas de 90° exactos son el enemigo mortal de la resistencia de materiales.")
