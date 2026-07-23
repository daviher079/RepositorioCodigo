import pandas as pd
import os
import matplotlib.pyplot as plt

BASE = os.path.join(os.path.dirname(__file__), "redes_sociales_unisport_limpio.xlsx")

df_metricas_rrss = pd.read_excel(BASE, sheet_name=1)

plataformas = df_metricas_rrss['plataforma'].value_counts()

etiquetas = plataformas.index.tolist()
valores = plataformas.values.tolist()

jugadores_max_comen_pos = df_metricas_rrss.loc[
    (df_metricas_rrss['jugador_mencionado']!='Equipo') & 
    (df_metricas_rrss['sentimiento']=='positivo'), 
    'jugador_mencionado'].value_counts()

print(jugadores_max_comen_pos)

engagement_por_partido = (
    df_metricas_rrss
    .assign(engagement_total=lambda df: df['likes'] + df['comentarios'] + df['compartidos'])
    .groupby('partido_id')['engagement_total']
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
print(engagement_por_partido)

top10 = engagement_por_partido.nlargest(10, 'engagement_total')

fig, ax = plt.subplots(figsize=(8, 6))
bars = ax.barh(top10['partido_id'], top10['engagement_total'])
ax.set_xlabel('Engagement total')
ax.set_title('Top 10 partidos con más engagement')
plt.tight_layout()
plt.savefig(os.path.join(os.path.dirname(__file__), 'barras_partidos.png'), dpi=150, bbox_inches='tight')

#fig, ax = plt.subplots(figsize=(8, 5))
#bars = ax.barh(jugadores_max_comen_pos.index, jugadores_max_comen_pos.values)
#ax.set_xlabel('Comentarios positivos')
#ax.set_title('Jugadores con más comentarios positivos')
#plt.tight_layout()
#plt.savefig(os.path.join(os.path.dirname(__file__), 'barras_jugadores.png'), dpi=150, bbox_inches='tight')


#fig, ax = plt.subplots(figsize=(6, 6))
#ax.pie(valores, labels=etiquetas, autopct='%1.1f%%')
#ax.set_title('Distribución por plataforma')
#plt.tight_layout()
#plt.savefig(os.path.join(os.path.dirname(__file__), "pie_plataformas.png"))