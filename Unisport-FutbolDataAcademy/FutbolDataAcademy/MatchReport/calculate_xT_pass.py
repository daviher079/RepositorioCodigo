import json
import os
import pandas as pd
import numpy as np


pd.set_option('display.max_columns', None)

green = '#69f900'
red = '#ff4b44'
blue = '#56CEE0'
violet = '#a369ff'
bg_color= '#ECFFFF'
line_color= '#000000'
col1 = '#F50900'
col2 = '#0115F5'

MATCH_FOLDER = os.path.join(os.path.dirname(__file__), 'Match')


def extract_data_from_dict(data):
    events_dict = data["matchCentreData"]["events"]
    teams_dict = {data["matchCentreData"]['home']['teamId']: data["matchCentreData"]['home']['name'],
                  data["matchCentreData"]['away']['teamId']: data["matchCentreData"]['away']['name']}
    players_home_df = pd.DataFrame(data["matchCentreData"]['home']['players'])
    players_home_df["teamId"] = data["matchCentreData"]['home']['teamId']
    players_away_df = pd.DataFrame(data["matchCentreData"]['away']['players'])
    players_away_df["teamId"] = data["matchCentreData"]['away']['teamId']
    players_df = pd.concat([players_home_df, players_away_df])
    return events_dict, players_df, teams_dict


def get_short_name(full_name):
    if pd.isna(full_name):
        return full_name
    parts = full_name.split()
    if len(parts) == 1:
        return full_name
    elif len(parts) == 2:
        return parts[0][0] + ". " + parts[1]
    else:
        return parts[0][0] + ". " + parts[1][0] + ". " + " ".join(parts[2:])


if __name__ == "__main__":
    # CAMBIA ESTE NOMBRE POR EL ARCHIVO GENERADO CON download_match_data.py
    match_json_path = os.path.join(MATCH_FOLDER, 'Real_Madrid_vs_Bayern_2026-04-07.json')

    with open(match_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    events_dict, players_df, teams_dict = extract_data_from_dict(data)

    df = pd.DataFrame(events_dict)
    dfp = pd.DataFrame(players_df)

    df['type'] = df['type'].apply(lambda x: x['displayName'] if isinstance(x, dict) else x)
    df['outcomeType'] = df['outcomeType'].apply(lambda x: x['displayName'] if isinstance(x, dict) else x)
    df['period'] = df['period'].apply(lambda x: x['displayName'] if isinstance(x, dict) else x)
    df['qualifiers'] = df['qualifiers'].apply(lambda x: str(x) if isinstance(x, list) else x)

    # Asignar valores xT
    df_base = df
    dfxT = df_base.copy()
    dfxT = dfxT[~dfxT['qualifiers'].str.contains('Corner') & ~dfxT['qualifiers'].str.contains('ThrowIn')]
    dfxT = dfxT[(dfxT['type']=='Pass') & (dfxT['outcomeType']=='Successful')]

    xT = pd.read_csv('https://raw.githubusercontent.com/mckayjohns/youtube-videos/main/data/xT_Grid.csv', header=None)
    xT = np.array(xT)
    xT_rows, xT_cols = xT.shape

    dfxT['x_start_bin_xT'] = pd.cut(dfxT['x'], bins=xT_cols, labels=False)
    dfxT['y_start_bin_xT'] = pd.cut(dfxT['y'], bins=xT_rows, labels=False)
    dfxT['x_end_bin_xT'] = pd.cut(dfxT['endX'], bins=xT_cols, labels=False)
    dfxT['y_end_bin_xT'] = pd.cut(dfxT['endY'], bins=xT_rows, labels=False)

    dfxT['start_zone_value_xT'] = dfxT[['x_start_bin_xT', 'y_start_bin_xT']].apply(lambda x: xT[x.iloc[1]][x.iloc[0]], axis=1)
    dfxT['end_zone_value_xT'] = dfxT[['x_end_bin_xT', 'y_end_bin_xT']].apply(lambda x: xT[x.iloc[1]][x.iloc[0]], axis=1)

    dfxT['xT'] = dfxT['end_zone_value_xT'] - dfxT['start_zone_value_xT']
    columns_to_drop = ['id', 'eventId', 'minute', 'second', 'teamId', 'x', 'y', 'expandedMinute', 'period', 'type', 'outcomeType', 'qualifiers',
                       'satisfiedEventsTypes', 'isTouch', 'playerId', 'endX', 'endY', 'relatedEventId', 'relatedPlayerId', 'blockedX', 'blockedY',
                       'goalMouthZ', 'goalMouthY', 'isShot']
    dfxT.drop(columns=columns_to_drop, inplace=True)

    df = df.merge(dfxT[['xT']], left_index=True, right_index=True, how='left')

    df['teamName'] = df['teamId'].map(teams_dict)

    df['x'] = df['x']*1.05
    df['y'] = df['y']*0.68
    df['endX'] = df['endX']*1.05
    df['endY'] = df['endY']*0.68
    df['goalMouthY'] = df['goalMouthY']*0.68

    columns_to_drop = ['height', 'weight', 'age', 'isManOfTheMatch', 'field', 'stats', 'subbedInPlayerId', 'subbedOutPeriod', 'subbedOutExpandedMinute',
                       'subbedInPeriod', 'subbedInExpandedMinute', 'subbedOutPlayerId', 'teamId']
    dfp.drop(columns=columns_to_drop, inplace=True)
    df = df.merge(dfp, on='playerId', how='left')

    # Calcular distancia de pase, para encontrar pases progresivos
    df['pro'] = np.where((df['type'] == 'Pass') & (df['outcomeType'] == 'Successful') & (df['x'] > 42),
                         np.sqrt((105 - df['x'])**2 + (34 - df['y'])**2) - np.sqrt((105 - df['endX'])**2 + (34 - df['endY'])**2), 0)

    df['shortName'] = df['name'].apply(get_short_name)

    hteamID = list(teams_dict.keys())[0]
    ateamID = list(teams_dict.keys())[1]
    hteamName = teams_dict[hteamID]
    ateamName = teams_dict[ateamID]

    hcol = col1
    acol = col2

    homedf = df[(df['teamId']==hteamID)]
    awaydf = df[(df['teamId']==ateamID)]
    hxT = homedf['xT'].sum().round(2)
    axT = awaydf['xT'].sum().round(2)

    hgoal_count = len(homedf[(homedf['teamId']==hteamID) & (homedf['type']=='Goal') & (~homedf['qualifiers'].str.contains('OwnGoal'))])
    agoal_count = len(awaydf[(awaydf['teamId']==ateamID) & (awaydf['type']=='Goal') & (~awaydf['qualifiers'].str.contains('OwnGoal'))])
    hgoal_count = hgoal_count + len(awaydf[(awaydf['teamId']==ateamID) & (awaydf['type']=='Goal') & (awaydf['qualifiers'].str.contains('OwnGoal'))])
    agoal_count = agoal_count + len(homedf[(homedf['teamId']==hteamID) & (homedf['type']=='Goal') & (homedf['qualifiers'].str.contains('OwnGoal'))])

    # ASIGNAR MANUALMENTE DE WEBS COMO FOTMOB
    hxg   = 1.28
    axg   = 0.76
    hxgot = 1.56
    axgot = 0.51
    file_header = f'{hteamName}_vs_{ateamName}'

    league = 'Champions League'
    gw = 8
    date = '07 Abril, 2026'

    processed_path = match_json_path.replace('.json', '_processed.csv')
    df.to_csv(processed_path, index=False)
    print(f'DataFrame procesado guardado en: {processed_path}')
