import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), "participacion_limpio.xlsx")

df = pd.read_excel(BASE, sheet_name=0)


columnasEnteros = ['Minutos', 'Toques en area rival', 'Perdidas', 
                'Oportunidades creadas', 'Regates Realizados con éxito']
columnasDecimales = ['Porcentaje de pases completados', 'Porcentaje de regates realizados']

columnasCompletas = columnasEnteros + columnasDecimales

estadisticas = df[columnasCompletas]

estadisticasCalculadas = pd.DataFrame({
    'Media':    estadisticas.mean(),
    'Mediana':  estadisticas.median(),
    'Mínimo':   estadisticas.min(),
    'Máximo':   estadisticas.max()
})

estadisticasCalculadas.loc[columnasEnteros, 'Media'] = (
    estadisticasCalculadas.loc[columnasEnteros, 'Media']
    .round(0)
    .astype('Int64') 
)

estadisticasCalculadas.loc[columnasDecimales, 'Media'] = (
    estadisticasCalculadas.loc[columnasDecimales, 'Media']
    .round(2)
)

print(estadisticasCalculadas)