import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Taller 3 | MakerBox", layout="wide")

st.title("🖥️ Taller 3: Simulación FEA y Validación Teórica")
st.markdown("**Objetivo:** Contrastar el cálculo analítico de esfuerzos flexionantes con el Análisis de Elementos Finitos (FEA) usando los criterios de Von Mises, partiendo de una geometría generada por código.")
st.divider()

# --- SECCIÓN 1: PARÁMETROS, PREVISUALIZACIÓN Y CÁLCULO TEÓRICO ---
st.header("1. Parámetros de la Escuadra y Cálculo Analítico")
st.write("Configura las dimensiones de la viga en voladizo. El sistema dibujará el perfil y calculará el esfuerzo teórico máximo asumiendo una sección transversal pura.")

# Layout en 3 columnas para el Dashboard
col1, col2, col3 = st.columns([1.2, 1.5, 1.2])

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
    r_fillet = st.slider("Radio de empalme interior (mm)", 0.0, 30.0, 5.0, step=1.0)

with col2:
    st.subheader("Previsualización del Perfil 2D")
    
    # Creación del gráfico dinámico con Matplotlib
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_alpha(0.0)
    ax.set_facecolor('none')
    
    # Coordenadas base
    y_wall_bottom = -(h_muro - altura) / 2
    y_wall_top = altura + (h_muro - altura) / 2
    
    # Lista de puntos del polígono
    pts = [
        (-t_muro, y_wall_bottom),
        (0, y_wall_bottom),
        (0, 0),
        (L, 0),
        (L, altura)
    ]
    
    # Cálculo de los puntos del arco (Fillet)
    if r_fillet > 0:
        cx, cy = r_fillet, altura + r_fillet # Centro de la circunferencia
        # Ángulos desde 270° (abajo) hasta 180° (izquierda)
        theta = np.linspace(1.5 * np.pi, np.pi, 20)
        for t in theta:
            pts.append((cx + r_fillet * np.cos(t), cy + r_fillet * np.sin(t)))
    else:
        pts.append((0, altura))
        
    pts.extend([
        (0, y_wall_top),
        (-t_muro, y_wall_top)
    ])
    
    # Dibujar la pieza
    polygon = patches.Polygon(pts, closed=True, facecolor='#00aeef', edgecolor='#2d2d2d', alpha=0.6, lw=2)
    ax.add_patch(polygon)
    
    # Dibujar el vector de Fuerza (P)
    ax.annotate("", xy=(L - L*0.05, altura), xytext=(L - L*0.05, altura + h_muro*0.4),
                arrowprops=dict(facecolor='#c72979', edgecolor='#c72979', shrink=0.05, width=2, headwidth=8))
    ax.text(L - L*0.05, altura + h_muro*0.45, f"P = {P} N", color='#c72979', fontweight='bold', ha='center')
    
    # Etiquetas de empotramiento
    ax.plot([-t_muro, -t_muro], [y_wall_bottom, y_wall_top], color='#46247a', lw=4)
    ax.text(-t_muro - 5, altura/2, "EMPOTRAMIENTO", rotation=90, va='center', ha='center', color='#46247a', fontweight='bold', fontsize=8)
    
    ax.autoscale_view()
    ax.axis('equal')
    ax.axis('off')
    st.pyplot(fig, use_container_width=True)

with col3:
    st.subheader("Mecánica de Materiales (Teoría)")
    
    M = P * L
    I = (base * (altura**3)) / 12.0
    c = altura / 2.0
    sigma_max = (M * c) / I
    factor_seguridad = Sy / sigma_max if sigma_max > 0 else 99.9

    st.latex(r"\sigma_{max} = \frac{M_{max} \cdot c}{I}")
    st.latex(r"\eta = \frac{S_y}{\sigma_{max}}")
    
    st.metric("Momento Máx.", f"{M/1000:.2f} N·m")
    st.metric("Esfuerzo Máx. ($\sigma$)", f"{sigma_max:.2f} MPa")
    
    if factor_seguridad < 1.0:
        st.metric("Factor Seg. ($\eta$)", f"{factor_seguridad:.2f}", "Falla", delta_color="inverse")
    elif factor_seguridad < 2.0:
        st.metric("Factor Seg. ($\eta$)", f"{factor_seguridad:.2f}", "Margen Crítico", delta_color="off")
    else:
        st.metric("Factor Seg. ($\eta$)", f"{factor_seguridad:.2f}", "Seguro")

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

col4, col5 = st.columns(2)

with col4:
    st.markdown(f"""
    ### Configuración FEA
    1. Importa el archivo `.stl` generado en OpenSCAD a Fusion 360.
    2. Convierte la malla a cuerpo sólido (Mesh to BRep).
    3. Pasa al espacio de trabajo **Simulation** y elige *Static Stress*.
    4. **Material:** Aplica `Steel, A36`.
    5. **Empotramiento:** Fija la cara posterior de la placa vertical.
    6. **Carga:** Aplica una fuerza de **{P} N** apuntando hacia abajo en la arista/cara final del brazo libre.
    """)

with col5:
    st.markdown(f"""
    ### Análisis Crítico
    * Refina la malla en la zona del empalme (fillet).
    * Ejecuta la simulación (Solve).
    * Compara el **Esfuerzo de Von Mises Máximo** con el $\sigma_{{max}}$ teórico ({sigma_max:.2f} MPa).
    """)
    
    st.info("💡 **Reto Maker:** Juega con el deslizador del 'Radio de empalme' (dejándolo en 0 mm vs 15 mm), regenera el STL y simula de nuevo. Verás matemáticamente por qué las esquinas de 90° exactos son el enemigo mortal de la resistencia de materiales.")
