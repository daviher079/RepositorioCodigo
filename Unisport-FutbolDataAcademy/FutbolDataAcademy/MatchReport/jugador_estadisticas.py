import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

SHOT_TYPES = {'MissedShot', 'SavedShot', 'ShotOnPost', 'Goal'}
TOP_N = 5

bg_color   = '#1a1a2e'
line_color = 'white'
hcol       = '#FFFFFF'
acol       = '#F50900'

SECTION_COLORS = {
    'Shots':              '#e74c3c',
    'Shot Assist':        '#e67e22',
    'Buildup to shot':    '#f1c40f',
    'Progressive Passes': '#2ecc71',
    'Line Breaking Pass': '#1abc9c',
    'Key Passes':         '#3498db',
    'Tackles':            '#9b59b6',
    'Interceptions':      '#e91e63',
    'Clearance':          '#607d8b',
}


def get_short_name(full_name):
    parts = full_name.strip().split()
    if len(parts) == 1:
        return full_name
    return f"{parts[0][0]}. {' '.join(parts[1:])}"


def _build_top_players(df, players, stat_cols, count_fn):
    records = []
    for name in players:
        row = {'name': name}
        row.update(zip(stat_cols, count_fn(name)))
        records.append(row)

    result = pd.DataFrame(records)
    result['total'] = result[list(stat_cols)].sum(axis=1)
    result = result.sort_values('total', ascending=False).reset_index(drop=True).head(TOP_N)
    result['shortName'] = result['name'].apply(get_short_name)
    return result


def get_shot_sequence_stats(df, team_id):
    players = df[df['teamId'] == team_id]['name'].unique()
    buildup_mask = df['qualifiers'].shift(-1).str.contains('KeyPass', na=False)

    def counts(name):
        pdf = df[df['name'] == name]
        return [
            len(pdf[pdf['type'].isin(SHOT_TYPES)]),
            len(pdf[(pdf['type'] == 'Pass') & pdf['qualifiers'].str.contains('KeyPass', na=False)]),
            len(df[(df['name'] == name) & (df['type'] == 'Pass') & buildup_mask]),
        ]

    return _build_top_players(df, players, ['Shots', 'Shot Assist', 'Buildup to shot'], counts)


def get_pass_type_stats(df, team_id):
    players = df[df['teamId'] == team_id]['name'].unique()

    def counts(name):
        pdf = df[df['name'] == name]
        return [
            len(pdf[pdf['pro'] > 9.144]),
            len(pdf[(pdf['type'] == 'Pass') & (pdf['outcomeType'] == 'Successful') & pdf['qualifiers'].str.contains('Throughball', na=False)]),
            len(pdf[(pdf['type'] == 'Pass') & pdf['qualifiers'].str.contains('KeyPass', na=False)]),
        ]

    return _build_top_players(df, players, ['Progressive Passes', 'Line Breaking Pass', 'Key Passes'], counts)


def get_defensive_player_stats(df, team_id):
    players = df[df['teamId'] == team_id]['name'].unique()

    def counts(name):
        pdf = df[df['name'] == name]
        return [
            len(pdf[(pdf['type'] == 'Tackle') & (pdf['outcomeType'] == 'Successful')]),
            len(pdf[pdf['type'] == 'Interception']),
            len(pdf[pdf['type'] == 'Clearance']),
        ]

    return _build_top_players(df, players, ['Tackles', 'Interceptions', 'Clearance'], counts)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    for team_id, team_name in [(hteamID, hteamName), (ateamID, ateamName)]:
        print(f"\n{'='*55}")
        print(f"  {team_name}")
        print(f"{'='*55}")

        for title, result_df in [
            ('Secuencia de tiro',   get_shot_sequence_stats(df, team_id)),
            ('Tipos de pase',       get_pass_type_stats(df, team_id)),
            ('Acciones defensivas', get_defensive_player_stats(df, team_id)),
        ]:
            stat_cols = [c for c in result_df.columns if c not in ('name', 'shortName', 'total')]
            print(f"\n  {title}")
            print(f"  {'-'*50}")
            header = f"  {'Jugador':<20}" + "".join(f"{c:>15}" for c in stat_cols) + f"{'Total':>8}"
            print(header)
            for _, row in result_df.iterrows():
                line = f"  {row['shortName']:<20}" + "".join(f"{int(row[c]):>15}" for c in stat_cols) + f"{int(row['total']):>8}"
                print(line)
