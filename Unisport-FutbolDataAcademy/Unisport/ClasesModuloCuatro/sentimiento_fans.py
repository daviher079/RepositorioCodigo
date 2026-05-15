# ============================================================
# PRÁCTICA: Análisis de Sentimiento del Aficionado
# Módulo 4 - Tema 5: Experiencia del Aficionado y Compromiso
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

print("=" * 65)
print("  ANÁLISIS DE SENTIMIENTO DEL AFICIONADO")
print("  Fan Pulse Analysis")
print("=" * 65)

# -------------------------------------------------
# 1. DATOS: COMENTARIOS SIMULADOS DE UN PARTIDO
# -------------------------------------------------
# Simulamos el flujo de comentarios en redes y app durante el partido.
# Minuto negativo = antes del partido.

comentarios = [
    # Previo al partido
    {"texto": "Qué ganas de que empiece, el equipo está en un momento increíble", "minuto": -10, "canal": "twitter"},
    {"texto": "Hoy ganamos seguro, confío totalmente en el equipo", "minuto": -5, "canal": "app"},
    {"texto": "Mal tiempo para venir, esperemos que el partido compense", "minuto": 0, "canal": "instagram"},

    # Primera parte – buena
    {"texto": "Qué buen inicio de partido, estamos dominando el juego", "minuto": 10, "canal": "app"},
    {"texto": "GOL GOL GOL!!! Jugada espectacular, esto es fútbol de verdad!", "minuto": 23, "canal": "twitter"},
    {"texto": "Golazo! El mejor gol de la temporada sin ninguna duda", "minuto": 23, "canal": "instagram"},
    {"texto": "Fantástico, estamos jugando de maravilla, lo merecemos", "minuto": 24, "canal": "app"},

    # Primera parte – giro negativo
    {"texto": "El árbitro está siendo completamente injusto con nosotros", "minuto": 35, "canal": "twitter"},
    {"texto": "No me gusta cómo estamos defendiendo, estamos muy mal atrás", "minuto": 40, "canal": "app"},
    {"texto": "Penalti en contra... esto es un robo vergonzoso, no puede ser", "minuto": 44, "canal": "twitter"},
    {"texto": "Inexplicable ese penalti, el árbitro perjudica siempre al equipo", "minuto": 44, "canal": "instagram"},
    {"texto": "Empate al descanso, decepcionante, hay que mejorar mucho", "minuto": 45, "canal": "app"},

    # Segunda parte – neutral y baja
    {"texto": "Vamos, en la segunda parte lo revertimos, hay que creer", "minuto": 46, "canal": "twitter"},
    {"texto": "Qué ocasión fallada, era un gol cantado, qué pena", "minuto": 58, "canal": "app"},
    {"texto": "El entrenador debería hacer cambios ya, esto no está funcionando", "minuto": 65, "canal": "twitter"},
    {"texto": "Qué mal estamos jugando, no reconozco a este equipo para nada", "minuto": 70, "canal": "instagram"},

    # Remontada final – explosión positiva
    {"texto": "GOL!!! La remontada!!! Increíble!!! Este equipo nunca se rinde!!!", "minuto": 78, "canal": "twitter"},
    {"texto": "Increíble gol! Nunca pierdo la fe en ellos! Qué corazón!", "minuto": 78, "canal": "app"},
    {"texto": "Campeones! Merecidísimo! Qué partido más espectacular y emotivo!", "minuto": 78, "canal": "instagram"},
    {"texto": "Hasta el final siempre creo en ellos, esto es pasión de verdad", "minuto": 82, "canal": "app"},
    {"texto": "Los mejores aficionados y el mejor equipo, esto es fantástico", "minuto": 85, "canal": "twitter"},
    {"texto": "La victoria más emocionante que he vivido en toda mi vida", "minuto": 90, "canal": "app"},
    {"texto": "Victoria merecidísima, jugamos un fútbol increíble al final", "minuto": 92, "canal": "instagram"},
    {"texto": "Gracias jugadores, nos hacéis felices e increíblemente orgullosos", "minuto": 95, "canal": "app"},
]

# -------------------------------------------------
# 2. ANALIZADOR DE SENTIMIENTO (LÉXICO DEPORTIVO)
# -------------------------------------------------
# Un sistema real usaría modelos de lenguaje (BERT, RoBERTa...).
# Aquí construimos uno basado en léxico específico del deporte.
# Es transparente, fácil de auditar y de ampliar.

print("\n⚙️  Iniciando análisis con léxico deportivo en español...\n")

palabras_positivas = [
    'gol', 'golazo', 'victoria', 'increíble', 'fantástico', 'espectacular',
    'impresionante', 'campeones', 'ganamos', 'merecido', 'remontada',
    'felices', 'emocionante', 'pasión', 'gracias', 'fe', 'orgullosos',
    'bravo', 'excelente', 'ganas', 'dominando', 'maravilla', 'confiío',
    'confío', 'creo', 'corazón', 'emotivo', 'alegría', 'mejor'
]

palabras_negativas = [
    'mal', 'robo', 'vergonzoso', 'injusto', 'inexplicable', 'fallada',
    'pésimo', 'horrible', 'decepcionante', 'árbitro', 'penalti',
    'perjudica', 'no puede', 'no reconozco', 'no está', 'no funciona',
    'pena', 'hay que mejorar', 'debería', 'débil', 'poca', 'mal tiempo'
]

def analizar_sentimiento(texto):
    """
    Clasifica el sentimiento de un texto deportivo en español.
    Retorna: (score, etiqueta)
    score > 0 → positivo | score < 0 → negativo | 0 → neutro
    """
    texto_lower = texto.lower()
    score_pos = sum(1 for p in palabras_positivas if p in texto_lower)
    score_neg = sum(1 for p in palabras_negativas if p in texto_lower)
    score = score_pos - score_neg

    if score > 0:
        etiqueta = 'Positivo'
    elif score < 0:
        etiqueta = 'Negativo'
    else:
        etiqueta = 'Neutro'
    return score, etiqueta

# Aplicar a todos los comentarios
df = pd.DataFrame(comentarios)
df[['score', 'sentimiento']] = df['texto'].apply(
    lambda t: pd.Series(analizar_sentimiento(t))
)

# -------------------------------------------------
# 3. RESULTADOS POR COMENTARIO
# -------------------------------------------------
print("ANÁLISIS DE CADA COMENTARIO:")
print("-" * 65)
print(f"{'Minuto':<8} | {'Sentimiento':<12} | Texto")
print("-" * 65)

for _, row in df.iterrows():
    icono = {'Positivo': '✅', 'Negativo': '❌', 'Neutro': '⬜'}[row['sentimiento']]
    min_str = f"min {row['minuto']:>3}" if row['minuto'] >= 0 else "  previo"
    texto_corto = row['texto'][:52] + "..." if len(row['texto']) > 52 else row['texto']
    print(f"{min_str}  | {icono} {row['sentimiento']:<10} | {texto_corto}")

# -------------------------------------------------
# 4. ESTADÍSTICAS GLOBALES
# -------------------------------------------------
print("\n" + "=" * 65)
print("  RESUMEN ESTADÍSTICO DEL PARTIDO")
print("=" * 65)

conteo = df['sentimiento'].value_counts()
total = len(df)
for sent, count in conteo.items():
    pct = count / total * 100
    barra = "█" * int(pct / 4)
    print(f"  {sent:<12}: {count:>3} comentarios  ({pct:.0f}%)  {barra}")

min_max_pos = df.loc[df['score'].idxmax(), 'minuto']
min_max_neg = df.loc[df['score'].idxmin(), 'minuto']
print(f"\n  Score medio del partido   : {df['score'].mean():.2f}")
print(f"  Minuto más positivo       : minuto {min_max_pos}")
print(f"  Minuto más negativo       : minuto {min_max_neg}")

# -------------------------------------------------
# 5. VISUALIZACIÓN: FAN PULSE
# -------------------------------------------------
print("\n" + "=" * 65)
print("  GENERANDO FAN PULSE CHART...")
print("=" * 65)

colores_sent = {'Positivo': '#27AE60', 'Negativo': '#E74C3C', 'Neutro': '#95A5A6'}
color_puntos = df['sentimiento'].map(colores_sent)

fig, axes = plt.subplots(2, 1, figsize=(14, 9))
fig.suptitle('Fan Pulse: Sentimiento del Aficionado durante el Partido\n(Datos Simulados)',
             fontsize=13, fontweight='bold', color='#1C2833')

# --- Gráfico 1: Evolución temporal del sentimiento ---
axes[0].scatter(df['minuto'], df['score'], c=color_puntos, s=75, zorder=3, alpha=0.85)
axes[0].axhline(y=0, color='gray', linestyle='--', alpha=0.4, linewidth=1)

for min_linea, etiq in [(0, 'Inicio'), (45, 'Descanso'), (90, 'Final')]:
    axes[0].axvline(x=min_linea, color='#2C3E50', linestyle=':', alpha=0.35, linewidth=1.2)
    axes[0].text(min_linea + 0.5, -2.8, etiq, fontsize=8, color='#5D6D7E')

axes[0].fill_between(df['minuto'], df['score'], 0,
                     where=(df['score'] > 0), alpha=0.12, color='#27AE60')
axes[0].fill_between(df['minuto'], df['score'], 0,
                     where=(df['score'] < 0), alpha=0.12, color='#E74C3C')

axes[0].set_xlabel('Minuto del partido', fontsize=11)
axes[0].set_ylabel('Score de sentimiento', fontsize=11)
axes[0].set_title('Evolución del Sentimiento a lo largo del Partido', fontsize=11, fontweight='bold')
axes[0].set_xlim(-15, 100)
axes[0].grid(True, alpha=0.18)

axes[0].annotate('GOL (min 23)', xy=(23, 2), xytext=(30, 2.5),
                  fontsize=9, color='#1E8449', fontweight='bold',
                  arrowprops=dict(arrowstyle='->', color='#1E8449'))
axes[0].annotate('Penalti en contra', xy=(44, -2), xytext=(28, -2.6),
                  fontsize=9, color='#C0392B', fontweight='bold',
                  arrowprops=dict(arrowstyle='->', color='#C0392B'))
axes[0].annotate('Remontada! (min 78)', xy=(78, 3), xytext=(60, 2.5),
                  fontsize=9, color='#1E8449', fontweight='bold',
                  arrowprops=dict(arrowstyle='->', color='#1E8449'))

leyenda = [mpatches.Patch(color=c, label=s) for s, c in colores_sent.items()]
axes[0].legend(handles=leyenda, loc='lower right', fontsize=9)

# --- Gráfico 2: Distribución por canal ---
canal_sent = df.groupby(['canal', 'sentimiento']).size().unstack(fill_value=0)
for col_add in ['Positivo', 'Neutro', 'Negativo']:
    if col_add not in canal_sent.columns:
        canal_sent[col_add] = 0
canal_sent = canal_sent[['Positivo', 'Neutro', 'Negativo']]

canal_sent.plot(kind='bar', ax=axes[1],
                color=['#27AE60', '#95A5A6', '#E74C3C'],
                width=0.55, edgecolor='white')
axes[1].set_xlabel('Canal de comunicación', fontsize=11)
axes[1].set_ylabel('Número de comentarios', fontsize=11)
axes[1].set_title('Distribución de Sentimiento por Canal', fontsize=11, fontweight='bold')
axes[1].set_xticklabels(canal_sent.index, rotation=0, fontsize=11)
axes[1].legend(title='Sentimiento', fontsize=9)
axes[1].grid(True, alpha=0.2, axis='y')

plt.tight_layout()
plt.savefig('sentimiento_fans.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n✅ Gráfico guardado como 'sentimiento_fans.png'")
print("\n" + "=" * 65)
print("  PREGUNTA PARA REFLEXIONAR:")
print("  Si fueras el community manager del club, ¿qué harías")
print("  con esta información en tiempo real durante el partido?")
print("=" * 65)