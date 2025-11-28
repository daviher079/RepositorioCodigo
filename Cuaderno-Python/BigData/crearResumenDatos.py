import pandas as pd
import os

# ================================
# RUTA AL EXCEL
# ================================
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ficheros")
ruta_excel = os.path.join(BASE, "dato.xlsx")

# ================================
# CARGAR DATOS
# ================================
df = pd.read_excel(ruta_excel)

# ================================
# ESTADÍSTICAS A MANTENER
# ================================
estadisticas_objetivo = [
    "Regates_realizados",
    "Pases_precisos",
    "Oportunidades_creadas",
    "Regateado",
    "Tiros_a_puerta",
    "Pases_en_ultimo_tercio",
    "Faltas_Recibidas",
    "Duelos_Ganados",
    "Duelos_perdidos",
    "Recuperaciones"
]

# ================================
# FILTRAR DATOS BASE
# ================================
df_resumen = df[df["estadistica"].isin(estadisticas_objetivo)].copy()

# ================================
# AÑADIR NUEVA ESTADISTICA: Duelos_Totales
# ================================
df_resumen["valor_num"] = pd.to_numeric(df_resumen["valor"], errors="coerce")

duelos = df_resumen[df_resumen["estadistica"].isin(["Duelos_Ganados", "Duelos_perdidos"])]

pivot = duelos.pivot_table(
    index=["jugador", "rival", "posicion", "tipo"],
    columns="estadistica",
    values="valor_num",
    aggfunc="sum"
).reset_index()

pivot = pivot.fillna(0)

pivot["fraccion"] = pivot["Duelos_Ganados"] / (
    pivot["Duelos_Ganados"] + pivot["Duelos_perdidos"]
)

pivot["valor"] = (
    pivot["Duelos_Ganados"].astype(int).astype(str) + "/" +
    (pivot["Duelos_Ganados"] + pivot["Duelos_perdidos"]).astype(int).astype(str)
)

pivot["estadistica"] = "Duelos_Totales"

duelos_totales_df = pivot[
    ["jugador", "rival", "estadistica", "valor", "tipo", "posicion", "fraccion"]
].rename(columns={"fraccion": "porcentaje"})

df_resumen = pd.concat([df_resumen, duelos_totales_df], ignore_index=True)

# ================================
# ELIMINAR DUELOS GANADOS / PERDIDOS
# ================================
df_resumen = df_resumen[
    ~df_resumen["estadistica"].isin(["Duelos_Ganados", "Duelos_perdidos"])
]

# ================================
# CAMBIAR TIPOS A CENTROCAMPISTA
# ================================
df_resumen.loc[df_resumen["estadistica"] == "Tiros_a_puerta", "tipo"] = "Atacante"
df_resumen.loc[df_resumen["estadistica"] == "Regates_realizados", "tipo"] = "Atacante"
df_resumen.loc[df_resumen["estadistica"] == "Oportunidades_creadas", "tipo"] = "Atacante"
df_resumen.loc[df_resumen["estadistica"] == "Pases_en_ultimo_tercio", "tipo"] = "Centrocampista"
df_resumen.loc[df_resumen["estadistica"] == "Pases_precisos", "tipo"] = "Centrocampista"
df_resumen.loc[df_resumen["estadistica"] == "Faltas_Recibidas", "tipo"] = "Centrocampista"
df_resumen.loc[df_resumen["estadistica"] == "Duelos_Totales", "tipo"] = "Defensa"


# ================================
# GUARDAR RESULTADO
# ================================
ruta_salida = os.path.join(BASE, "dato_resumen_completo.xlsx")
df_resumen.to_excel(ruta_salida, index=False)

print("Archivo generado en:", ruta_salida)
