# ============================================================
# PRÁCTICA: Segmentación de Aficionados con K-Means
# Módulo 4 - Tema 5: Experiencia del Aficionado y Compromiso
# ============================================================

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("=" * 65)
print("  SEGMENTACIÓN DE AFICIONADOS CON K-MEANS")
print("=" * 65)

# -------------------------------------------------
# 1. DATOS SIMULADOS DE COMPORTAMIENTO DE FANS
# -------------------------------------------------
# Cada fila representa un aficionado.
# Las columnas representan su comportamiento a lo largo de la temporada.

np.random.seed(42)
n = 300

datos = pd.DataFrame({
    'fan_id': range(1, n + 1),
    
    # Partidos a los que ha asistido en el estadio esta temporada
    'partidos_estadio': np.concatenate([
        np.random.randint(0, 4, 100),     # Grupo A: poca asistencia
        np.random.randint(3, 12, 100),    # Grupo B: asistencia media
        np.random.randint(10, 20, 100),   # Grupo C: alta asistencia
    ]),
    
    # Gasto total en merchandising oficial (€/año)
    'gasto_merch_eur': np.concatenate([
        np.random.uniform(0, 40, 100),
        np.random.uniform(30, 130, 100),
        np.random.uniform(100, 450, 100),
    ]),
    
    # Horas por semana usando la app oficial del club
    'uso_app_horas': np.concatenate([
        np.random.uniform(0, 1.5, 100),
        np.random.uniform(1, 6, 100),
        np.random.uniform(5, 15, 100),
    ]),
    
    # Interacciones semanales en redes sociales sobre el club
    'interacciones_rrss': np.concatenate([
        np.random.uniform(0, 4, 100),
        np.random.uniform(3, 12, 100),
        np.random.uniform(10, 35, 100),
    ]),
})

print(f"\n📊 Dataset cargado: {len(datos)} aficionados")
print(f"   Variables analizadas: partidos_estadio, gasto_merch_eur,")
print(f"   uso_app_horas, interacciones_rrss\n")
print("Vista previa del dataset (primeras 6 filas):")
print(datos.head(6).to_string(index=False))

# -------------------------------------------------
# 2. NORMALIZACIÓN
# -------------------------------------------------
print("\n" + "=" * 65)
print("  PASO 1: NORMALIZACIÓN DE DATOS")
print("=" * 65)
print("\n   K-Means usa distancias. Sin normalizar, variables con")
print("   escalas grandes (como € de merch) dominarían el resultado.")
print("   StandardScaler lleva todo a media=0, desviación típica=1.\n")

variables = ['partidos_estadio', 'gasto_merch_eur', 'uso_app_horas', 'interacciones_rrss']
scaler = StandardScaler()
X = scaler.fit_transform(datos[variables])

print("   ✅ Normalización completada.")

# -------------------------------------------------
# 3. K-MEANS
# -------------------------------------------------
print("\n" + "=" * 65)
print("  PASO 2: APLICAR K-MEANS (K=3)")
print("=" * 65)
print("\n   🤖 El algoritmo busca 3 grupos de fans similares entre sí.")
print("   Iterará hasta que los centroides sean estables...\n")

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
datos['cluster'] = kmeans.fit_predict(X)

print("   ✅ Clustering completado. 300 fans clasificados en 3 grupos.\n")

# -------------------------------------------------
# 4. NOMBRAR LOS SEGMENTOS
# -------------------------------------------------
# Identificamos cuál cluster tiene más asistencia y le damos nombre
media_asistencia = datos.groupby('cluster')['partidos_estadio'].mean()
orden = media_asistencia.sort_values().index.tolist()

nombres = {
    orden[0]: 'Fan Casual',
    orden[1]: 'Fan Regular',
    orden[2]: 'Super Fan'
}
datos['segmento'] = datos['cluster'].map(nombres)

# -------------------------------------------------
# 5. PERFIL DE CADA SEGMENTO
# -------------------------------------------------
print("=" * 65)
print("  RESULTADO: PERFIL DE CADA SEGMENTO")
print("=" * 65)

iconos = {'Fan Casual': '🟡', 'Fan Regular': '🔵', 'Super Fan': '🔴'}

for seg in ['Fan Casual', 'Fan Regular', 'Super Fan']:
    g = datos[datos['segmento'] == seg]
    print(f"\n  {iconos[seg]}  {seg.upper()}  ({len(g)} fans)")
    print(f"     Partidos en estadio/temporada : {g['partidos_estadio'].mean():.1f}")
    print(f"     Gasto en merchandising (€/año): {g['gasto_merch_eur'].mean():.0f} €")
    print(f"     Uso de la app (h/semana)       : {g['uso_app_horas'].mean():.1f} h")
    print(f"     Interacciones RRSS/semana      : {g['interacciones_rrss'].mean():.1f}")

# -------------------------------------------------
# 6. VISUALIZACIÓN
# -------------------------------------------------
print("\n" + "=" * 65)
print("  GENERANDO GRÁFICOS...")
print("=" * 65)

colores_seg = {'Fan Casual': '#F4D03F', 'Fan Regular': '#2980B9', 'Super Fan': '#E74C3C'}
color_lista = datos['segmento'].map(colores_seg)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Segmentación de Aficionados con K-Means (Datos Simulados)',
             fontsize=13, fontweight='bold', color='#1C2833')

# Gráfico 1: Scatter – Asistencia vs Gasto
axes[0].scatter(datos['partidos_estadio'], datos['gasto_merch_eur'],
                c=color_lista, alpha=0.65, edgecolors='white', linewidth=0.4, s=60)
axes[0].set_xlabel('Partidos presenciados en estadio / temporada', fontsize=11)
axes[0].set_ylabel('Gasto en Merchandising (€/año)', fontsize=11)
axes[0].set_title('Asistencia vs. Gasto en Merchandising', fontsize=11, fontweight='bold')
axes[0].grid(True, alpha=0.2)

from matplotlib.patches import Patch
leyenda = [Patch(color=c, label=s) for s, c in colores_seg.items()]
axes[0].legend(handles=leyenda, loc='upper left', fontsize=10)

# Gráfico 2: Comparativa normalizada por segmento
medias = datos.groupby('segmento')[variables].mean()
orden_nombres = ['Fan Casual', 'Fan Regular', 'Super Fan']
medias = medias.loc[orden_nombres]

# Normalizar para comparación relativa (máx = 100)
medias_n = medias.copy()
for col in variables:
    medias_n[col] = (medias[col] / medias[col].max()) * 100

x = np.arange(len(orden_nombres))
w = 0.2
etiquetas = ['Partidos/año', 'Merch (€)', 'App (h/sem)', 'RRSS/sem']
paleta = ['#1A5276', '#2980B9', '#85C1E9', '#D6EAF8']

for i, (col, etiq, color) in enumerate(zip(variables, etiquetas, paleta)):
    axes[1].bar(x + i * w, medias_n[col], w, label=etiq, color=color, edgecolor='white')

axes[1].set_xlabel('Segmento de aficionado', fontsize=11)
axes[1].set_ylabel('Valor relativo (% del máximo)', fontsize=11)
axes[1].set_title('Comparativa de Comportamiento por Segmento\n(valores normalizados)', fontsize=11, fontweight='bold')
axes[1].set_xticks(x + w * 1.5)
axes[1].set_xticklabels(orden_nombres, fontsize=10)
axes[1].legend(fontsize=9)
axes[1].grid(True, alpha=0.2, axis='y')

plt.tight_layout()
plt.savefig('segmentacion_fans.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n✅ Gráfico guardado como 'segmentacion_fans.png'")
print("\n" + "=" * 65)
print("  PREGUNTA PARA REFLEXIONAR:")
print("  ¿Qué estrategia diferente diseñarías para cada segmento?")
print("=" * 65)
