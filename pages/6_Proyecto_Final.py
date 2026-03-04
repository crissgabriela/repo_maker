import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Proyecto Final | MakerBox", layout="wide")

st.title("🚀 Proyecto Final: Hélice Carenada (Ducted Fan)")
st.markdown("**Objetivo:** Integrar el diseño paramétrico, el análisis de esfuerzos centrífugos y la dinámica de fluidos para validar y manufacturar un sistema de propulsión eficiente.")
st.divider()

# --- SECCIÓN 1: SÍNTESIS DE DISEÑO ---
st.header("1. Parámetros Operativos y Geometría")
st.write("Configura las condiciones de operación de tu sistema. Evalúaremos el esfuerzo en la raíz del aspa y el aumento teórico de empuje gracias al carenado (Efecto Venturi).")

col1, col2, col3 = st.columns([1.2, 1.5, 1.2])

with col1:
    st.subheader("Variables del Rotor")
    
    st.markdown("**Material de Impresión 3D:** PETG")
    Sy_petg = 45.0 # Límite elástico típico del PETG en MPa
    rho_petg = 1270.0 # Densidad kg/m^3
    
    RPM = st.slider("Velocidad de giro (RPM)", 1000, 15000, 5000, step=500)
    R_ext = st.slider("Radio de la hélice (mm)", 30.0, 100.0, 60.0, step=1.0)
    R_int = st.slider("Radio del núcleo (mm)", 10.0, 30.0, 15.0, step=1.0)
    
    st.markdown("**Variables del Carenado (Ducto)**")
    holgura = st.slider("Holgura punta-ducto (Tip Clearance) (mm)", 0.5, 5.0, 1.0, step=0.5)
    
    # Conversiones
    omega = RPM * (2 * np.pi / 60) # rad/s
    R_ext_m = R_ext / 1000.0
    R_int_m = R_int / 1000.0

with col2:
    st.subheader("Esquema del Sistema (Sección)")
    
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_alpha(0.0)
    ax.set_facecolor('none')
    
    # Eje central
    ax.plot([-20, 40], [0, 0], 'k-.', alpha=0.5)
    
    # Dibujar Núcleo (Hub)
    hub = patches.Rectangle((-10, 0), 20, R_int, facecolor='#46247a', edgecolor='black')
    ax.add_patch(hub)
    
    # Dibujar Aspa (Blade)
    blade = patches.Rectangle((-5, R_int), 10, R_ext - R_int, facecolor='#00aeef', edgecolor='black', alpha=0.8)
    ax.add_patch(blade)
    
    # Dibujar Carenado (Duct) - Perfil aerodinámico simplificado
    R_duct_in = R_ext + holgura
    R_duct_out = R_duct_in + 5
    duct_x = [-15, 0, 15, 25]
    duct_y_top = [R_duct_in + 8, R_duct_in + 5, R_duct_in + 2, R_duct_in]
    duct_y_bot = [R_duct_in, R_duct_in, R_duct_in, R_duct_in]
    
    ax.plot(duct_x, duct_y_top, color='#c72979', lw=2)
    ax.plot(duct_x, duct_y_bot, color='#c72979', lw=2)
    ax.fill_between(duct_x, duct_y_bot, duct_y_top, color='#c72979', alpha=0.4)
    
    # Anotaciones
    ax.annotate("", xy=(0, R_ext), xytext=(0, R_duct_in), arrowprops=dict(arrowstyle="<->", color="red"))
    ax.text(2, R_ext + holgura/2, f"Holgura\n{holgura} mm", color="red", fontsize=8)
    
    # Simulación de flujo de aire (Líneas de corriente)
    ax.annotate("", xy=(5, R_ext - 10), xytext=(-20, R_ext - 10), arrowprops=dict(facecolor='gray', alpha=0.5, width=1, headwidth=5))
    ax.annotate("", xy=(25, R_ext + 2), xytext=(-20, R_ext + 5), arrowprops=dict(facecolor='gray', alpha=0.5, width=1, headwidth=5, connectionstyle="arc3,rad=-0.1"))
    
    ax.set_xlim(-25, 45)
    ax.set_ylim(0, R_duct_out + 10)
    ax.set_aspect('equal')
    ax.axis('off')
    st.pyplot(fig, use_container_width=True)

with col3:
    st.subheader("Cálculos Críticos")
    
    # 1. Fuerza Centrífuga Estimada en la raíz del aspa
    # F_c = m * omega^2 * r_cg. Asumimos un volumen simplificado para estimar masa
    volumen_aspa = (10/1000) * (R_ext_m - R_int_m) * (20/1000) # Espesor medio x largo x cuerda media
    masa_aspa = volumen_aspa * rho_petg
    r_cg = R_int_m + (R_ext_m - R_int_m) / 2
    
    Fc = masa_aspa * (omega**2) * r_cg
    
    # 2. Esfuerzo a Tracción en la Raíz
    area_raiz = (10/1000) * (25/1000) # Espesor x cuerda en la raíz
    sigma_raiz = (Fc / area_raiz) / 1e6 # En MPa
    
    factor_seguridad = Sy_petg / sigma_max if 'sigma_max' in locals() else Sy_petg / sigma_raiz
    
    # 3. Velocidad de Punta (Tip Speed)
    v_tip = omega * R_ext_m
    mach = v_tip / 343.0 # Velocidad del sonido
    
    st.latex(r"F_c = m \cdot \omega^2 \cdot r_{cg}")
    st.latex(r"\sigma_{raíz} = \frac{F_c}{A_{raíz}}")
    
    st.metric("Fuerza Centrífuga por Aspa", f"{Fc:.1f} N")
    st.metric("Esfuerzo en la Raíz ($\sigma$)", f"{sigma_raiz:.2f} MPa")
    
    if factor_seguridad < 1.0:
        st.metric("Factor Seg. ($\eta$) - PETG", f"{factor_seguridad:.2f}", "Riesgo de Ruptura", delta_color="inverse")
    elif factor_seguridad < 2.0:
        st.metric("Factor Seg. ($\eta$) - PETG", f"{factor_seguridad:.2f}", "Margen Crítico", delta_color="off")
    else:
        st.metric("Factor Seg. ($\eta$) - PETG", f"{factor_seguridad:.2f}", "Seguro")
        
    st.divider()
    st.metric("Velocidad de Punta (Mach)", f"{mach:.2f}")
    if mach > 0.6:
        st.warning("⚠️ Velocidad de punta alta. Peligro de ondas de choque y pérdida severa de eficiencia.")

st.divider()

# --- SECCIÓN 2: INTEGRACIÓN 4.0 (EL FLUJO FINAL) ---
st.header("2. Ruta de Manufactura y Validación")

col4, col5 = st.columns(2)

with col4:
    st.markdown("""
    ### 🛠️ 1. Generación de Geometría (Herramienta Web)
    Ahora que has validado los esfuerzos centrífugos, es hora de modelar la malla.
    * Abre el **Generador de Hélices UTalca** (Nuestra herramienta basada en React/Three.js).
    * Introduce el Perfil NACA que probaste en el **Taller 4**.
    * Configura el radio, la cuerda y la torsión aerodinámica.
    * Habilita la opción de **"Anillo Protector"** (Carenado) ajustando la holgura al mínimo posible validado por tu impresora.
    * Descarga el archivo `.stl`.
    """)
    # Aquí puedes poner el enlace a tu HTML alojado en GitHub Pages
    st.info("👉 **[Abrir Generador de Hélices MakerBox](https://tu-usuario.github.io/tu-repo/generador.html)**")

with col5:
    st.markdown("""
    ### 💻 2. Validación FEA y CFD (Fase de Cierre)
    Lleva el archivo `.stl` a **Autodesk Fusion 360** para la validación definitiva:
    
    1. **Simulación Estructural (FEA - Taller 3):** Aplica una carga de rotación (*Rotational Load*) igual a los RPM calculados. Verifica si los esfuerzos de Von Mises en la raíz del aspa coinciden con nuestro cálculo teórico analítico.
    2. **Túnel de Viento (CFD - Taller 4 y 5):** Configura un dominio de aire fluido. Comprueba cómo el carenado reduce los vórtices de punta (Tip Vortices) y cómo el Efecto Venturi disminuye la presión estática frente al rotor, "chupando" más flujo másico y generando un **aumento del empuje total**.
    3. **Manufactura (Taller 1):** Exporta a Bambu Studio, lamina tu diseño en PETG asegurando que la orientación de capa maximice la resistencia a la tracción centrífuga (impresión plana, no vertical).
    """)
