import streamlit as st

# Configuración de página
st.set_page_config(page_title="Taller 1 | MakerBox", layout="wide")

st.title("⚙️ Taller 1: Dualidad Digital en Manufactura")
st.markdown("**Objetivo:** Contrastar el modelado por código (CSG) con el modelado visual (B-Rep) para la manufactura de una pieza funcional.")
st.divider()

# --- SECCIÓN 1: TEORÍA Y CONCEPTOS ---
st.header("1. Geometría Constructiva de Sólidos (CSG) - OpenSCAD")
st.write("El enfoque CSG construye geometría compleja a partir de primitivas simples usando operaciones booleanas (Unión, Diferencia, Intersección).")

# Layout de dos columnas
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Parámetros de Diseño")
    st.info("Modifica las variables aquí y observa cómo se reescribe el script CSG en tiempo real.")
    
    # Sliders interactivos para los alumnos
    largo = st.slider("Largo de la Placa (mm)", 50, 120, 80, step=5)
    ancho = st.slider("Ancho de la Placa (mm)", 20, 60, 30, step=2)
    espesor = st.slider("Espesor Base (mm)", 2.0, 5.0, 3.0, step=0.5)
    texto = st.text_input("Texto de Identificación", "MAKERBOX UTALCA")
    
    st.latex(r"Volumen_{aprox} = Largo \times Ancho \times Espesor")
    volumen = largo * ancho * espesor
    st.metric("Volumen estimado de material", f"{volumen/1000:.2f} cm³")

with col2:
    st.subheader("Script CSG Dinámico")
    # Generación dinámica del código OpenSCAD basada en los inputs
    codigo_openscad = f"""// --- PARÁMETROS DE USUARIO ---
largo = {largo};
ancho = {ancho};
espesor_base = {espesor};
radio_esquina = 4;

texto_placa = "{texto}";
tamano_texto = 8;
espesor_texto = 1.5;

diametro_agujero = 5;

// --- GEOMETRÍA PRINCIPAL ---
difference() {{
    union() {{
        hull() {{
            translate([-(largo/2)+radio_esquina, -(ancho/2)+radio_esquina, 0]) cylinder(r=radio_esquina, h=espesor_base, $fn=50);
            translate([(largo/2)-radio_esquina, -(ancho/2)+radio_esquina, 0]) cylinder(r=radio_esquina, h=espesor_base, $fn=50);
            translate([-(largo/2)+radio_esquina, (ancho/2)-radio_esquina, 0]) cylinder(r=radio_esquina, h=espesor_base, $fn=50);
            translate([(largo/2)-radio_esquina, (ancho/2)-radio_esquina, 0]) cylinder(r=radio_esquina, h=espesor_base, $fn=50);
        }}
        translate([5, 0, espesor_base])
            linear_extrude(height = espesor_texto)
                text(texto_placa, size = tamano_texto, font = "Arial:style=Bold", halign = "center", valign = "center");
    }}
    translate([-(largo/2) + 8, 0, -1])
        cylinder(h = espesor_base + espesor_texto + 2, d = diametro_agujero, $fn=50);
}}
"""
    st.code(codigo_openscad, language="openscad")
    st.caption("Copia este código y pégalo en OpenSCAD para compilar la malla (F6) y exportar el STL.")

st.divider()

# --- SECCIÓN 2: FUSION 360 Y MANUFACTURA ---
st.header("2. Representación por Fronteras (B-Rep) - Fusion 360")
st.write("En Fusion 360, llegaremos a la misma topología matemática pero guiados por un flujo de trabajo visual y un historial de operaciones (Timeline).")

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    **Flujo de Trabajo B-Rep:**
    1. **Boceto Base:** Crea un rectángulo por centro en el plano XY de `Largo x Ancho`.
    2. **Empalme:** Aplica un *Fillet* de 4mm en los vértices.
    3. **Extrusión (E):** Levanta el perfil según el `Espesor Base`.
    4. **Operación Join:** Dibuja el texto en la cara superior y extruye 1.5mm.
    5. **Operación Cut:** Boceta un círculo $\phi 5\text{mm}$ y corta a través del cuerpo.
    """)

with col4:
    st.success("**Paso Final: Manufactura en Bambu Studio**")
    st.markdown("""
    Para lograr una placa bicolor sin necesidad de múltiples extrusores, utilizaremos la técnica de pausa condicional:
    * Importa tu archivo `.stl` o `.step`.
    * Lamina la pieza (Slice).
    * En la barra deslizante derecha, identifica la capa exacta donde termina la base plana y comienza el texto.
    * Haz clic derecho y selecciona **Insertar Pausa (M600)** para cambio manual de filamento.
    """)
