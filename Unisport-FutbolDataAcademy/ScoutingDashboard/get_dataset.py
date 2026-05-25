import requests
import pandas as pd
import ast
import time
import os

TOURNAMENT_ID = 54       # La Liga 2
SEASON_ID = 77558        # 2025-2026
CACHE_FILE = "dataset_extremos.csv"

FIELDS = ",".join([
    "goals", "assists", "minutesPlayed", "rating",
    "successfulDribbles", "successfulDribblesPercentage", "attemptedDribbles",
    "keyPasses", "totalShots", "shotsOnTarget",
    "bigChancesCreated", "bigChancesMissed",
    "accurateFinalThirdPasses", "accuratePassesPercentage",
    "totalPasses", "accuratePasses",
    "aerialWon", "aerialLost",
    "totalClearances", "interceptions", "tackles", "wonTackles",
    "foulsCommitted", "foulsDrawn",
    "yellowCards", "redCards",
    "dispossessed", "totalRating", "countRating",
])


def create_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": f"https://www.sofascore.com/tournament/football/spain/laliga-2/{TOURNAMENT_ID}",
        "Accept": "application/json",
    })
    session.get(
        f"https://www.sofascore.com/tournament/football/spain/laliga-2/{TOURNAMENT_ID}",
        timeout=10
    )
    return session


def get_all_player_stats(session):
    print("Descargando estadísticas de La Liga 2 2025-2026...")
    all_players = []
    page = 0
    while True:
        r = session.get(
            f"https://api.sofascore.com/api/v1/unique-tournament/{TOURNAMENT_ID}/season/{SEASON_ID}/statistics",
            params={"limit": 100, "offset": page * 100, "order": "-rating",
                    "accumulation": "total", "fields": FIELDS},
            timeout=15
        )
        data = r.json()
        results = data.get("results", [])
        if not results:
            break
        all_players.extend(results)
        pages_total = data.get("pages", 1)
        print(f"  Página {page + 1}/{pages_total}: {len(results)} jugadores")
        page += 1
        if page >= pages_total:
            break
        time.sleep(0.3)
    return all_players


def get_player_profile(session, player_id):
    r = session.get(f"https://api.sofascore.com/api/v1/player/{player_id}", timeout=10)
    if r.status_code == 200:
        return r.json().get("player", {})
    return {}


def is_winger(pos_str):
    try:
        return any(p in ("LW", "RW") for p in ast.literal_eval(str(pos_str)))
    except Exception:
        return False


def build_dataset():
    session = create_session()
    all_stats = get_all_player_stats(session)
    print(f"\nTotal jugadores: {len(all_stats)}")
    print("Obteniendo perfiles...")

    rows = []
    for i, p in enumerate(all_stats):
        pid = p["player"]["id"]
        profile = get_player_profile(session, pid)

        row = {
            "id": pid,
            "nombre": p["player"]["name"],
            "equipo": p["team"]["name"],
            "posicion": profile.get("position", ""),
            "posicion_detallada": str(profile.get("positionsDetailed", [])),
            "edad": profile.get("dateOfBirth", ""),
            "altura": profile.get("height", ""),
            "pie_dominante": profile.get("preferredFoot", ""),
            "contrato_hasta": profile.get("contractUntilTimestamp", ""),
            "valor_mercado": profile.get("proposedMarketValue", ""),
        }
        # Add all stats dynamically
        for k, v in p.items():
            if k not in ("player", "team"):
                row[k] = v

        rows.append(row)

        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{len(all_stats)} procesados")
        time.sleep(0.2)

    df = pd.DataFrame(rows)
    extremos = df[df["posicion_detallada"].apply(is_winger)].copy().reset_index(drop=True)
    print(f"\nExtemos (LW/RW): {len(extremos)} | Columnas: {len(extremos.columns)}")
    return extremos


if __name__ == "__main__":
    if os.path.exists(CACHE_FILE):
        print(f"Cargando desde caché: {CACHE_FILE}")
        df = pd.read_csv(CACHE_FILE)
    else:
        df = build_dataset()
        df.to_csv(CACHE_FILE, index=False)
        print(f"Dataset guardado: {CACHE_FILE}")

    print(f"\nJugadores: {len(df)} | Columnas: {len(df.columns)}")
    print("\nTop 10 por goles:")
    print(df.sort_values("goals", ascending=False)[["nombre", "equipo", "goals", "assists", "successfulDribbles", "rating"]].head(10).to_string())
