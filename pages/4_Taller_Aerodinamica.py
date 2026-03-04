import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Taller 4 | MakerBox", layout="wide")

st.title("🌪️ Taller 4: Aerodinámica y Túnel de Viento CFD")
st.markdown("**Objetivo:** Generar superficies aerodinámicas mediante ecuaciones paramétricas (NACA 4-dígitos) y automatizar su importación a Fusion 360 para simulación de fluidos.")
st.divider()

# --- SECCIÓN 1: GENERADOR DE COORDENADAS NACA ---
st.header("1. Generación Matemática del Perfil Alar")
st.write("Ingresa los 4 dígitos del perfil NACA. El sistema resolverá las ecuaciones de curvatura y espesor para generar la nube de puntos exacta.")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Parámetros del Perfil")
    naca_input = st.text_input("Perfil NACA (4 dígitos)", "2412", max_chars=4)
    cuerda = st.slider("Cuerda del perfil (mm)", 50.0, 500.0, 100.0, step=10.0)
    puntos = st.slider("Resolución (N° de puntos)", 30, 200, 100, step=10)
    
    # Lógica matemática NACA
    if len(naca_input) == 4 and naca_input.isdigit():
        m = int(naca_input[0]) / 100.0   # Curvatura máxima
        p = int(naca_input[1]) / 10.0    # Posición de curvatura máxima
        t = int(naca_input[2:4]) / 100.0 # Espesor máximo
        
        # Distribución de puntos (Cosoidal para mayor densidad en bordes de ataque/fuga)
        beta = np.linspace(0, np.pi, puntos)
        x = (1 - np.cos(beta)) / 2
        
        # Ecuación de espesor
        yt = 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)
        
        # Ecuación de línea de curvatura media
        yc = np.zeros_like(x)
        dyc_dx = np.zeros_like(x)
        
        if p > 0:
            mask1 = x <= p
            mask2 = x > p
            
            yc[mask1] = (m / p**2) * (2 * p * x[mask1] - x[mask1]**2)
            dyc_dx[mask1] = (2 * m / p**2) * (p - x[mask1])
            
            yc[mask2] = (m / (1 - p)**2) * ((1 - 2 * p) + 2 * p * x[mask2] - x[mask2]**2)
            dyc_dx[mask2] = (2 * m / (1 - p)**2) * (p - x[mask2])
            
        theta = np.arctan(dyc_dx)
        
        # Superficie Superior (Extradós)
        xu = x - yt * np.sin(theta)
        yu = yc + yt * np.cos(theta)
        
        # Superficie Inferior (Intradós)
        xl = x + yt * np.sin(theta)
        yl = yc - yt * np.cos(theta)
        
        # Escalar por la cuerda
        xu *= cuerda
        yu *= cuerda
        xl *= cuerda
        yl *= cuerda
        
        # Generar DataFrame para CSV (Fusion 360 lee X, Y, Z)
        # Ordenamos: desde el borde de fuga por abajo, hasta el borde de ataque, y vuelta por arriba
        x_csv = np.concatenate([xl[::-1], xu[1:]])
        y_csv = np.concatenate([yl[::-1], yu[1:]])
        z_csv = np.zeros_like(x_csv)
        
        df_naca = pd.DataFrame({'X': x_csv, 'Y': y_csv, 'Z': z_csv})
        csv_data = df_naca.to_csv(index=False, header=False)
        
        st.success("✅ Coordenadas calculadas exitosamente.")
        st.download_button(
            label=f"📥 Descargar NACA_{naca_input}.csv",
            data=csv_data,
            file_name=f"NACA_{naca_input}.csv",
            mime="text/csv",
            type="primary"
        )
    else:
        st.error("Por favor ingresa exactamente 4 números enteros.")

with col2:
    st.subheader("Perfil Aerodinámico (2D)")
    if len(naca_input) == 4 and naca_input.isdigit():
        fig, ax = plt.subplots(figsize=(8, 3))
        fig.patch.set_alpha(0.0)
        ax.set_facecolor('none')
        
        # Dibujar cuerda y línea de curvatura
        ax.plot([0, cuerda], [0, 0], 'k--', lw=1, alpha=0.5, label="Cuerda")
        ax.plot(x * cuerda, yc * cuerda, color='#c72979', ls='-.', lw=1.5, label="Línea de Curvatura")
        
        # Dibujar perfil
        ax.plot(xu, yu, color='#00aeef', lw=2)
        ax.plot(xl, yl, color='#00aeef', lw=2)
        ax.fill_between(x_csv, y_csv, 0, color='#00aeef', alpha=0.2)
        
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlabel("Posición X (mm)")
        ax.set_ylabel("Posición Y (mm)")
        ax.legend()
        ax.grid(True, linestyle=':', alpha=0.6)
        st.pyplot(fig)

st.divider()

# --- SECCIÓN 2: AUTOMATIZACIÓN EN FUSION 360 Y CFD ---
st.header("2. De la Nube de Puntos al Túnel de Viento")

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    ### Fase A: Automatización (ImportSplineCSV)
    En Fusion 360, no uniremos los puntos a mano. Usaremos un *Script* integrado para automatizar la topología:
    
    1. Ve a la pestaña **Utilities** (Utilidades) > **ADD-INS** > **Scripts and Add-Ins** (o presiona Shift+S).
    2. En la lista de *Sample Scripts*, busca uno llamado **ImportSplineCSV** (en Python).
    3. Haz clic en **Run**. 
    4. Selecciona el archivo `.csv` que descargaste desde esta web.
    5. ¡Magia! Fusion 360 dibujará el perfil aerodinámico perfecto. Cierra el *spline* dibujando una línea en el borde de fuga y extruye (E) el ala unos $150 \text{ mm}$.
    """)

with col4:
    st.markdown("""
    ### Fase B: Autodesk CFD (Setup del Dominio)
    Para simular cómo interactúa el aire con el perfil, necesitamos definir un "Volumen de Control" (el túnel de viento virtual):
    
    * **Dominio Fluido:** Crea una caja alrededor del ala. Regla de oro: 5 veces la cuerda hacia arriba, abajo y adelante; 10 veces la cuerda hacia atrás (para capturar la estela).
    * **Material:** Asigna *Air* (Aire) al volumen exterior y *Solid* (o suprime) al ala interior.
    * **Condiciones de Contorno (Boundary Conditions):**
        * Cara Frontal: Velocidad de entrada (ej. $20 \text{ m/s}$).
        * Cara Trasera: Presión estática $= 0 \text{ Pa}$.
        * Caras Laterales/Superior/Inferior: *Slip/Symmetry* (Deslizamiento).
    """)
    st.info("💡 **Objetivo CFD:** Ubica el punto de estancamiento en el borde de ataque (máxima presión) e identifica dónde ocurre la separación de la capa límite al aumentar el Ángulo de Ataque (AoA).")
