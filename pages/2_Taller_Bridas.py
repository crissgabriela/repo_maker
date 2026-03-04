import streamlit as st
import pandas as pd

st.set_page_config(page_title="Taller 2 | MakerBox", layout="wide")

st.title("🔩 Taller 2: Bridas Paramétricas y Ensambles")
st.markdown("**Objetivo:** Controlar geometría en Fusion 360 mediante archivos CSV y utilizar bibliotecas estándar para el análisis de interferencias.")
st.divider()

# --- SECCIÓN 1: GENERADOR DE PARÁMETROS CSV ---
st.header("1. Generador de Parámetros (Norma Simplificada)")
st.write("Selecciona el Diámetro Nominal (DN) de la tubería. El sistema calculará las dimensiones de la brida y generará el archivo CSV compatible con Fusion 360.")

# Base de datos simplificada de bridas (Valores en mm)
datos_bridas = {
    "DN 25 (1\")": {"d_interno": 33.4, "d_externo": 115.0, "espesor": 14.0, "pcd": 85.0, "n_pernos": 4, "d_agujero": 14.0},
    "DN 50 (2\")": {"d_interno": 60.3, "d_externo": 165.0, "espesor": 16.0, "pcd": 125.0, "n_pernos": 4, "d_agujero": 18.0},
    "DN 100 (4\")": {"d_interno": 114.3, "d_externo": 220.0, "espesor": 22.0, "pcd": 180.0, "n_pernos": 8, "d_agujero": 18.0},
    "DN 150 (6\")": {"d_interno": 168.3, "d_externo": 285.0, "espesor": 24.0, "pcd": 240.0, "n_pernos": 8, "d_agujero": 22.0}
}

col1, col2 = st.columns([1, 1])

with col1:
    seleccion = st.selectbox("Selecciona el tamaño de la brida:", list(datos_bridas.keys()))
    parametros = datos_bridas[seleccion]
    
    st.markdown("### Dimensiones Calculadas")
    st.write(f"- **Diámetro Interno:** {parametros['d_interno']} mm")
    st.write(f"- **Diámetro Externo:** {parametros['d_externo']} mm")
    st.write(f"- **Espesor:** {parametros['espesor']} mm")
    st.write(f"- **Círculo de Pernos (PCD):** {parametros['pcd']} mm")
    st.write(f"- **Cantidad de Pernos:** {parametros['n_pernos']} unidades")
    st.write(f"- **Diámetro del Agujero:** {parametros['d_agujero']} mm")

with col2:
    st.markdown("### Exportar a Fusion 360")
    st.info("Fusion 360 requiere un formato CSV estricto: `ParameterName,Unit,Value,Comment`")
    
    # Creación del DataFrame con el formato exacto para Fusion 360
    df_csv = pd.DataFrame({
        "ParameterName": ["d_interno", "d_externo", "espesor", "pcd", "n_pernos", "d_agujero"],
        "Unit": ["mm", "mm", "mm", "mm", "", "mm"], # n_pernos no tiene unidad
        "Value": [parametros['d_interno'], parametros['d_externo'], parametros['espesor'], parametros['pcd'], parametros['n_pernos'], parametros['d_agujero']],
        "Comment": ["Diámetro interior", "Diámetro exterior", "Grosor de la brida", "Pitch Circle Diameter", "Cantidad de perforaciones", "Holgura del perno"]
    })
    
    csv_data = df_csv.to_csv(index=False, header=False) # Fusion no lee la fila de cabecera
    
    st.download_button(
        label="📥 Descargar parametros_brida.csv",
        data=csv_data,
        file_name="parametros_brida.csv",
        mime="text/csv",
        type="primary"
    )

st.divider()

# --- SECCIÓN 2: FLUJO DE TRABAJO EN FUSION 360 ---
st.header("2. Flujo de Trabajo en el Taller (B-Rep Avanzado)")

st.markdown("""
### Fase A: Parametrización
1. En Fusion 360, ve a **Modify > Change Parameters**.
2. Haz clic en el ícono de **Import** y selecciona el archivo `parametros_brida.csv` que acabas de descargar.
3. Inicia un boceto. Dibuja dos círculos concéntricos y, en lugar de escribir números, escribe `d_externo` y `d_interno`.
4. Extruye usando la variable `espesor`.

### Fase B: Patrón Paramétrico
1. Crea un nuevo boceto sobre la cara de la brida.
2. Dibuja un círculo de construcción usando la variable `pcd` (Pitch Circle Diameter).
3. Dibuja el primer agujero usando `d_agujero` sobre el PCD y córtalo (Extrude Cut).
4. Aplica un **Circular Pattern** a la operación de corte. En la cantidad (Quantity), escribe la variable `n_pernos`.

### Fase C: Ensamblaje y Validación (McMaster-Carr)
1. Ve a **Insert > Insert McMaster-Carr Component**.
2. Busca un perno hexagonal métrico (ej. M16) y una tuerca que calcen con tu `d_agujero`. Descarga el modelo en formato `3D STEP`.
3. Usa la herramienta **Joint (J)** para ensamblar el perno en el primer agujero.
4. Aplica un **Circular Pattern** al componente del perno, guiado nuevamente por la variable `n_pernos`.
5. **Análisis de Ingeniería:** Ve a **Inspect > Interference** y selecciona todos los cuerpos. Verifica que no haya colisiones entre los hilos del perno y la pared del agujero.
""")
