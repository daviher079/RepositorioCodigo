import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import unicodedata
import os

random.seed(42)
np.random.seed(42)

RUTA_SALIDA = os.path.dirname(os.path.abspath(__file__))

RIVALES = [
    "Real Valladolid", "Deportivo de La Coruña", "Sporting de Gijón",
    "Real Oviedo", "SD Huesca", "Mirandés", "Burgos CF",
    "Racing de Santander", "Levante UD", "Real Zaragoza",
    "Albacete Balompié", "UD Almería", "Córdoba CF",
    "CD Tenerife", "Elche CF", "SD Eibar", "Málaga CF",
    "Granada CF", "Cartagena FC"
]

# Jugadores ficticios de Unisport FC + "Equipo" con más peso
JUGADORES = [
    "Álvarez", "Herrera", "Castillo", "Navarro", "Delgado", "Rubio",
    "Equipo", "Equipo", "Equipo", "Equipo"
]

PLATAFORMAS_POND = ["Instagram"] * 5 + ["Twitter"] * 3 + ["TikTok"] * 2

TIPO_CONTENIDO = {
    "Instagram": ["foto", "video", "story", "reel"],
    "Twitter":   ["tweet", "hilo"],
    "TikTok":    ["video", "directo"]
}

SENTIMIENTO_PROB = {
    "Victoria": [0.70, 0.20, 0.10],   # positivo, neutro, negativo
    "Empate":   [0.35, 0.40, 0.25],
    "Derrota":  [0.10, 0.25, 0.65],
}


def slugify(texto):
    texto = unicodedata.normalize("NFKD", texto.lower().strip())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.replace(" ", "").replace(".", "").replace("-", "")


def generar_goles(resultado):
    if resultado == "Victoria":
        gf = random.randint(1, 3)
        gc = random.randint(0, max(0, gf - 1))
    elif resultado == "Empate":
        g = random.randint(0, 2)
        gf, gc = g, g
    else:
        gc = random.randint(1, 3)
        gf = random.randint(0, max(0, gc - 1))
    return gf, gc


# ── HOJA 1: PARTIDOS ────────────────────────────────────────────────────────
# Distribución: Local 10V/5E/4D · Visitante 5V/6E/8D
res_local     = ["Victoria"] * 10 + ["Empate"] * 5 + ["Derrota"] * 4
res_visitante = ["Victoria"] * 5  + ["Empate"] * 6 + ["Derrota"] * 8
random.shuffle(res_local)
random.shuffle(res_visitante)

fixtures = []
for i, rival in enumerate(RIVALES):
    slug = slugify(rival)
    for localía, resultado in [("Local", res_local[i]), ("Visitante", res_visitante[i])]:
        gf, gc = generar_goles(resultado)
        fixtures.append({
            "rival": rival, "slug": slug,
            "localía": localía, "resultado": resultado,
            "goles_favor": gf, "goles_contra": gc
        })

random.shuffle(fixtures)

fecha_inicio = datetime(2025, 8, 16)
partidos = []
for idx, f in enumerate(fixtures):
    jornada = idx + 1
    fecha = fecha_inicio + timedelta(weeks=idx)
    if fecha.month == 1 and fecha.year == 2026:
        fecha += timedelta(weeks=2)

    pid = f"unisportfc-{f['slug']}" if f["localía"] == "Local" else f"{f['slug']}-unisportfc"

    partidos.append({
        "partido_id":   pid,
        "jornada":      jornada,
        "fecha":        fecha.strftime("%Y-%m-%d"),
        "rival":        f["rival"],
        "localía":      f["localía"],
        "goles_favor":  f["goles_favor"],
        "goles_contra": f["goles_contra"],
        "resultado":    f["resultado"],
        "puntos":       3 if f["resultado"] == "Victoria" else (1 if f["resultado"] == "Empate" else 0)
    })

df_partidos = pd.DataFrame(partidos)


# ── HOJA 2: MÉTRICAS RRSS ───────────────────────────────────────────────────
MOMENTOS = {
    "pre-partido":  {"n": (1, 3), "likes_base": (150,  600), "ajuste_resultado": False},
    "post-partido": {"n": (2, 4), "likes_base": (300, 1500), "ajuste_resultado": True},
    "semana":       {"n": (1, 2), "likes_base": (80,   400), "ajuste_resultado": False},
}

metricas = []
for _, partido in df_partidos.iterrows():
    resultado = partido["resultado"]
    pid       = partido["partido_id"]
    fecha_pdo = datetime.strptime(partido["fecha"], "%Y-%m-%d")

    for momento, cfg in MOMENTOS.items():
        for _ in range(random.randint(*cfg["n"])):
            plataforma = random.choice(PLATAFORMAS_POND)
            tipo       = random.choice(TIPO_CONTENIDO[plataforma])

            l_min, l_max = cfg["likes_base"]
            if cfg["ajuste_resultado"]:
                if resultado == "Victoria":
                    l_min, l_max = int(l_min * 1.6), int(l_max * 1.8)
                elif resultado == "Derrota":
                    l_min, l_max = int(l_min * 0.4), int(l_max * 0.5)

            likes       = random.randint(l_min, l_max)
            comentarios = max(0, int(likes * random.uniform(0.03, 0.12)))
            compartidos = max(0, int(likes * random.uniform(0.01, 0.06)))

            sentimiento = random.choices(
                ["positivo", "neutro", "negativo"],
                weights=SENTIMIENTO_PROB[resultado]
            )[0]

            dias_offset = {"pre-partido": (-2, -1), "post-partido": (0, 1), "semana": (-6, -3)}[momento]
            fecha_pub   = fecha_pdo + timedelta(days=random.randint(*dias_offset))

            metricas.append({
                "partido_id":         pid,
                "plataforma":         plataforma,
                "tipo_contenido":     tipo,
                "fecha_publicacion":  fecha_pub.strftime("%Y-%m-%d"),
                "momento":            momento,
                "likes":              likes,
                "comentarios":        comentarios,
                "compartidos":        compartidos,
                "sentimiento":        sentimiento,
                "jugador_mencionado": random.choice(JUGADORES)
            })

df_metricas = pd.DataFrame(metricas)

# ── PROBLEMAS DE CALIDAD (material para la limpieza) ────────────────────────
# 1. Duplicados
df_metricas = pd.concat(
    [df_metricas, df_metricas.sample(12, random_state=42)],
    ignore_index=True
)
# 2. Outliers en likes (posts virales)
idx_virales = df_metricas.sample(5, random_state=99).index
df_metricas.loc[idx_virales, "likes"] = [19800, 26500, 31200, 18400, 22700]
# 3. Nulos en comentarios
idx_nulos_com = df_metricas.sample(15, random_state=7).index
df_metricas.loc[idx_nulos_com, "comentarios"] = np.nan
# 4. Nulos en compartidos
idx_nulos_comp = df_metricas.sample(8, random_state=13).index
df_metricas.loc[idx_nulos_comp, "compartidos"] = np.nan

df_metricas = df_metricas.sample(frac=1, random_state=42).reset_index(drop=True)

# ── EXPORTAR ────────────────────────────────────────────────────────────────
ruta_excel = os.path.join(RUTA_SALIDA, "dataset_unisport_fc.xlsx")
with pd.ExcelWriter(ruta_excel, engine="openpyxl") as writer:
    df_partidos.to_excel(writer, sheet_name="partidos",      index=False)
    df_metricas.to_excel(writer, sheet_name="metricas_rrss", index=False)

print(f"Dataset generado: {ruta_excel}")
print(f"  partidos:       {len(df_partidos)} filas")
print(f"  metricas_rrss:  {len(df_metricas)} filas")
