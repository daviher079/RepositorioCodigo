import asyncio
import ssl
import pandas as pd
from understat import Understat
import aiohttp


async def get_shots(match_id, team=None):
    """
    Obtiene los tiros de un partido desde Understat y devuelve
    un DataFrame con los tiros de ambos equipos o de un equipo concreto.
    """
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connector = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=connector) as session:
        understat = Understat(session)

        try:
            shots = await understat.get_match_shots(match_id)
        except Exception as e:
            print("Error obteniendo datos:", e)
            return None

        if not shots:
            print("No se encontraron datos para este partido")
            return None

        #shots es un diccionario de datos 
        print(type(shots))

        home_shots = shots["h"]
        away_shots = shots["a"]

        df_home = pd.DataFrame(home_shots)
        df_away = pd.DataFrame(away_shots)

        df_home["team"] = df_home["h_team"]
        df_away["team"] = df_away["a_team"]

        cols = ["X", "Y", "xG", "team", "player", "minute", "result"]
        df = pd.concat([df_home[cols], df_away[cols]], ignore_index=True)

        numeric_cols = ["X", "Y", "xG", "minute"]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

        df["goal"] = (df["result"] == "Goal").astype(int)

        if team:
            df = df[df["team"] == team]

        df = df.sort_values("minute").reset_index(drop=True)
        df = df[["minute", "team", "player", "X", "Y", "xG", "result", "goal"]]

        df.to_csv(f"shots_match_{match_id}.csv", index=False)

        return df


if __name__ == "__main__":
    match_id = 22514
    shots_df = asyncio.run(get_shots(match_id))
    print(shots_df)