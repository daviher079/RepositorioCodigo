# ============================================================
# PRÁCTICA: Gestión Inteligente con IA
# Módulo 4 · Tema 6 · Gestión y Organización Deportiva
# Máster en Big Data e IA en el Deporte - Unisport
# ============================================================
# Este script demuestra dos aplicaciones reales de IA en gestión:
#   1. Predicción de asistencia con Machine Learning
#   2. Simulación de Dynamic Pricing basada en el modelo

# Librerías necesarias (todas incluidas en Anaconda estándar):
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# Fijamos semilla para que todos obtengamos los mismos resultados
np.random.seed(42)

# ============================================================
# PASO 0: Crear el dataset de partidos
# ============================================================
# Simulamos 150 partidos con las variables que maneja un gestor deportivo real

n_partidos = 150

rival_ranking  = np.random.randint(1, 21, n_partidos)      # 1=mejor rival, 20=peor
dia_semana     = np.random.randint(0, 7, n_partidos)        # 0=Lunes ... 6=Domingo
temperatura    = np.random.uniform(8, 36, n_partidos)       # ºC en el momento del partido
precio_entrada = np.random.uniform(25, 85, n_partidos)      # € precio medio de entrada
forma_local    = np.random.randint(0, 16, n_partidos)       # Puntos en últimos 5 partidos
tipo_partido   = np.random.choice([1,2,3], n_partidos, p=[0.65,0.20,0.15])
# tipo: 1=Liga, 2=Copa/Continental, 3=Derby o Final

# Calculamos la asistencia con una fórmula realista + ruido
asistencia = (
    55                                    # Base: 55% de ocupación
    - rival_ranking * 1.2                 # Rival peor  → menos aficionados
    + (6 - dia_semana) * 1.8             # Fin de semana → más aficionados
    - (temperatura - 20)**2 * 0.08        # Temperatura extrema → menos asistencia
    - (precio_entrada - 40) * 0.35        # Precio alto → menos asistencia
    + forma_local * 1.5                   # Buen momento → más aficionados
    + (tipo_partido == 2) * 8             # Copa/Continental: +8%
    + (tipo_partido == 3) * 20            # Derby/Final: +20%
    + np.random.normal(0, 5, n_partidos)  # Variabilidad aleatoria
)
asistencia = np.clip(asistencia, 30, 99)  # Entre 30% y 99%

df_partidos = pd.DataFrame({
    'rival_ranking':  rival_ranking,
    'dia_semana':     dia_semana,
    'temperatura_c':  np.round(temperatura, 1),
    'precio_entrada': np.round(precio_entrada, 0).astype(int),
    'forma_local':    forma_local,
    'tipo_partido':   tipo_partido,
    'asistencia_pct': np.round(asistencia, 1)
})

print("=" * 65)
print("  GESTIÓN INTELIGENTE: De los Datos a las Decisiones")
print("=" * 65)
print(f"\n✅ Dataset creado: {len(df_partidos)} partidos con {len(df_partidos.columns)} variables")
print(f"\nPrimeras filas del dataset:")
print(df_partidos.head(8).to_string(index=False))
print(f"\nAsistencia → Media: {df_partidos['asistencia_pct'].mean():.1f}%  "
      f"| Min: {df_partidos['asistencia_pct'].min():.1f}%  "
      f"| Max: {df_partidos['asistencia_pct'].max():.1f}%")


# ============================================================
# EJERCICIO 1: Modelo de Predicción de Asistencia
# ============================================================
print("\n" + "=" * 65)
print("  EJERCICIO 1: Predicción de Asistencia con Random Forest")
print("=" * 65)

# Las 6 variables que usará el modelo
features = ['rival_ranking', 'dia_semana', 'temperatura_c',
            'precio_entrada', 'forma_local', 'tipo_partido']
X = df_partidos[features]
y = df_partidos['asistencia_pct']

# Dividimos en datos de entrenamiento (80%) y prueba (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"\n🔀 Entrenamiento: {len(X_train)} partidos | Prueba: {len(X_test)} partidos")

# Entrenamos el modelo
print("🤖 Entrenando Random Forest (100 árboles de decisión)...")
modelo = RandomForestRegressor(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# Evaluamos qué tal predice en datos nuevos
y_pred = modelo.predict(X_test)
mae  = mean_absolute_error(y_test, y_pred)
r2   = r2_score(y_test, y_pred)

print(f"\n📊 Rendimiento del modelo:")
print(f"   Error medio absoluto (MAE):  {mae:.1f}%  (el modelo se equivoca ±{mae:.1f}%)")
print(f"   Coeficiente R²:              {r2:.3f}   (1.00 = predicción perfecta)")

# --- Gráfico 1: Real vs. Predicho + Importancia de Variables ---
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Ejercicio 1: Modelo de Predicción de Asistencia', fontsize=14, fontweight='bold')

# Panel izquierdo: Real vs Predicho
axes[0].scatter(y_test, y_pred, color='steelblue', alpha=0.65, edgecolors='white', s=90)
axes[0].plot([30, 100], [30, 100], 'r--', linewidth=2, label='Predicción perfecta')
axes[0].set_xlabel('Asistencia Real (%)', fontsize=12)
axes[0].set_ylabel('Asistencia Predicha (%)', fontsize=12)
axes[0].set_title('Real vs. Predicho', fontsize=13, fontweight='bold')
axes[0].legend(fontsize=11)
axes[0].grid(True, alpha=0.3)
axes[0].text(32, 93,
    f'R² = {r2:.3f}\nError medio = {mae:.1f}%',
    fontsize=11, bbox=dict(boxstyle='round', facecolor='#fff9c4', alpha=0.9))

# Panel derecho: Importancia de variables
nombres_es = ['Ranking Rival', 'Día Semana', 'Temperatura',
              'Precio Entrada', 'Forma Local', 'Tipo Partido']
importancias = modelo.feature_importances_
indices      = np.argsort(importancias)          # de menor a mayor para barh

colores_barras = ['#e74c3c' if importancias[i] == max(importancias) else '#3498db'
                  for i in indices]

axes[1].barh([nombres_es[i] for i in indices], importancias[indices],
             color=colores_barras, edgecolor='white')
axes[1].set_xlabel('Importancia relativa', fontsize=12)
axes[1].set_title('¿Qué variables influyen\nmás en la asistencia?', fontsize=13, fontweight='bold')
axes[1].grid(True, alpha=0.3, axis='x')

# Etiqueta en la barra más importante
max_idx = np.argmax(importancias)
axes[1].annotate('← Más importante',
    xy=(importancias[max_idx], nombres_es.index(nombres_es[max_idx])),
    fontsize=9, color='#c0392b', style='italic')

plt.tight_layout()
plt.show()


# ============================================================
# EJERCICIO 2: Análisis de Factores Clave
# ============================================================
print("\n" + "=" * 65)
print("  EJERCICIO 2: ¿Qué factores determinan la asistencia?")
print("=" * 65)

# Importancia en formato texto
print("\n📈 Importancia de cada variable en el modelo:")
for i in np.argsort(importancias)[::-1]:
    barra = '█' * int(importancias[i] * 50)
    print(f"  {nombres_es[i]:<18}: {barra:.<30} {importancias[i]*100:5.1f}%")

# Estadísticas por tipo de partido
print("\n\n🏆 Asistencia media según el tipo de partido:")
for tipo, nombre in [(1,'Liga'), (2,'Copa/Continental'), (3,'Derby / Final')]:
    media = df_partidos[df_partidos['tipo_partido'] == tipo]['asistencia_pct'].mean()
    barra = '▓' * int(media / 3)
    print(f"  {nombre:<22}: {barra} {media:.1f}%")

# --- Gráfico 2: Precio vs. Asistencia y Boxplot por tipo ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Ejercicio 2: Análisis de Variables Clave', fontsize=14, fontweight='bold')

color_map = {1: '#3498db', 2: '#2ecc71', 3: '#e74c3c'}
colores   = df_partidos['tipo_partido'].map(color_map)

axes[0].scatter(df_partidos['precio_entrada'], df_partidos['asistencia_pct'],
                c=colores, alpha=0.65, s=65, edgecolors='white')
axes[0].set_xlabel('Precio de Entrada (€)', fontsize=12)
axes[0].set_ylabel('Asistencia (%)', fontsize=12)
axes[0].set_title('Precio vs. Asistencia', fontsize=13, fontweight='bold')
parches = [mpatches.Patch(color=color_map[t], label=n)
           for t, n in [(1,'Liga'), (2,'Copa/Continental'), (3,'Derby/Final')]]
axes[0].legend(handles=parches, fontsize=10)
axes[0].grid(True, alpha=0.3)

data_box = [df_partidos[df_partidos['tipo_partido'] == t]['asistencia_pct'].values for t in [1,2,3]]
bp = axes[1].boxplot(data_box, labels=['Liga', 'Copa/Continental', 'Derby/Final'],
                     patch_artist=True)
for patch, c in zip(bp['boxes'], ['#3498db','#2ecc71','#e74c3c']):
    patch.set_facecolor(c)
    patch.set_alpha(0.75)
axes[1].set_ylabel('Asistencia (%)', fontsize=12)
axes[1].set_title('Distribución de Asistencia\npor Tipo de Partido', fontsize=13, fontweight='bold')
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.show()


# ============================================================
# EJERCICIO 3: Simulador de Dynamic Pricing
# ============================================================
print("\n" + "=" * 65)
print("  EJERCICIO 3: Simulador de Dynamic Pricing")
print("=" * 65)

CAPACIDAD = 50_000   # Aforo del estadio (modificable)

print("\n🏟️  Partido que vamos a analizar:")
print("   Rival:         Real Madrid (ranking 1 — rival top)")
print("   Día:           Sábado (día 5)")
print("   Temperatura:   18°C  (ideal)")
print("   Forma local:   10 pts en últimos 5 partidos  (buena forma)")
print("   Tipo:          Liga  (partido importante de liga)")
print(f"   Estadio:       {CAPACIDAD:,} espectadores de aforo")

partido_base = {
    'rival_ranking':  1,
    'dia_semana':     5,
    'temperatura_c':  18.0,
    'forma_local':    10,
    'tipo_partido':   1
}

# Simulamos precios de 20€ a 100€ en pasos de 5€
precios = np.arange(20, 101, 5)
resultados = []

for precio in precios:
    p = dict(partido_base)
    p['precio_entrada'] = precio
    df_p    = pd.DataFrame([p])
    asist   = float(np.clip(modelo.predict(df_p[features])[0], 30, 99))
    asist_n = int(asist / 100 * CAPACIDAD)
    ingresos = asist_n * precio
    resultados.append({
        'precio':     precio,
        'asist_pct':  round(asist, 1),
        'asistentes': asist_n,
        'ingresos':   ingresos
    })

df_dp = pd.DataFrame(resultados)
fila_optima = df_dp.loc[df_dp['ingresos'].idxmax()]

print(f"\n{'Precio':>7} | {'Asistencia':>10} | {'Asistentes':>11} | {'Ingresos':>14}")
print("-" * 52)
for _, r in df_dp.iterrows():
    marca = "  ◄ PRECIO ÓPTIMO" if r['precio'] == fila_optima['precio'] else ""
    print(f"  {r['precio']:>4}€ | {r['asist_pct']:>9.1f}% | {int(r['asistentes']):>11,} | "
          f"{int(r['ingresos']):>12,}€{marca}")

print(f"\n💡 Conclusión del simulador:")
print(f"   Precio que maximiza ingresos:  {fila_optima['precio']:.0f}€")
print(f"   Asistencia esperada:           {fila_optima['asist_pct']:.1f}%  "
      f"({int(fila_optima['asistentes']):,} personas)")
print(f"   Ingresos máximos proyectados:  {int(fila_optima['ingresos']):,}€")

# --- Gráfico 3: Triple panel de Dynamic Pricing ---
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Ejercicio 3: Simulador de Dynamic Pricing', fontsize=14, fontweight='bold')

# Curva de demanda
axes[0].plot(df_dp['precio'], df_dp['asist_pct'], 'o-', color='steelblue', lw=2, ms=7)
axes[0].axvline(fila_optima['precio'], color='red', ls='--', alpha=0.75,
                label=f"Precio óptimo: {fila_optima['precio']:.0f}€")
axes[0].set_xlabel('Precio (€)', fontsize=12)
axes[0].set_ylabel('Asistencia Predicha (%)', fontsize=12)
axes[0].set_title('Curva de Demanda', fontsize=12, fontweight='bold')
axes[0].legend(fontsize=10)
axes[0].grid(True, alpha=0.3)

# Asistentes
axes[1].plot(df_dp['precio'], df_dp['asistentes'], 's-', color='darkorange', lw=2, ms=7)
axes[1].axvline(fila_optima['precio'], color='red', ls='--', alpha=0.75)
axes[1].set_xlabel('Precio (€)', fontsize=12)
axes[1].set_ylabel('Número de Asistentes', fontsize=12)
axes[1].set_title('Precio vs. Asistentes', fontsize=12, fontweight='bold')
axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
axes[1].grid(True, alpha=0.3)

# Curva de ingresos
axes[2].fill_between(df_dp['precio'], df_dp['ingresos']/1000, alpha=0.25, color='green')
axes[2].plot(df_dp['precio'], df_dp['ingresos']/1000, 'D-', color='green', lw=2.5, ms=8)
axes[2].scatter([fila_optima['precio']], [fila_optima['ingresos']/1000],
                color='red', s=220, zorder=5,
                label=f"Máximo: {int(fila_optima['ingresos']):,}€")
axes[2].axvline(fila_optima['precio'], color='red', ls='--', alpha=0.75)
axes[2].set_xlabel('Precio (€)', fontsize=12)
axes[2].set_ylabel('Ingresos (miles €)', fontsize=12)
axes[2].set_title('¿Qué precio maximiza\nlos ingresos?', fontsize=12, fontweight='bold')
axes[2].legend(fontsize=10)
axes[2].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}k'))
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("\n" + "=" * 65)
print("  ✅ ¡Práctica completada!")
print("  Hemos aprendido a:")
print("    1. Crear un dataset de gestión deportiva realista")
print("    2. Entrenar un modelo Random Forest para predecir asistencia")
print("    3. Interpretar qué variables más influyen en el modelo")
print("    4. Simular estrategias de Dynamic Pricing para maximizar ingresos")
print("=" * 65)
