import ast
import os
import pandas as pd


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')


def extract_length(qualifiers):
    for item in qualifiers:
        if 'displayName' in item['type'] and item['type']['displayName'] == 'Length':
            return float(item['value'])
    return None


def get_pass_stats(df, hteamID, ateamID):
    hdf = df[df['teamId'] == hteamID]
    adf = df[df['teamId'] == ateamID]

    hpasses = hdf[hdf['type'] == 'Pass']
    apasses = adf[adf['type'] == 'Pass']
    total_passes = len(hpasses) + len(apasses)

    # Posesión
    hposs = round((len(hpasses) / total_passes) * 100, 2) if total_passes > 0 else 0
    aposs = round(100 - hposs, 2)

    # Inclinación del campo (field tilt) — toques en el último tercio
    hft_touches = len(hdf[(hdf['isTouch'] == 1) & (hdf['x'] >= 70)])
    aft_touches = len(adf[(adf['isTouch'] == 1) & (adf['x'] >= 70)])
    total_ft = hft_touches + aft_touches
    hft = round((hft_touches / total_ft) * 100, 2) if total_ft > 0 else 0
    aft = round(100 - hft, 2)

    # Pases totales y efectivos
    htotal_pass = len(hpasses)
    atotal_pass = len(apasses)
    hacc_pass = len(hpasses[hpasses['outcomeType'] == 'Successful'])
    aacc_pass = len(apasses[apasses['outcomeType'] == 'Successful'])

    # Balones largos (excluye córners y centros)
    hlong = hpasses[hpasses['qualifiers'].str.contains('Longball', na=False) &
                    ~hpasses['qualifiers'].str.contains('Corner', na=False) &
                    ~hpasses['qualifiers'].str.contains('Cross', na=False)]
    along = apasses[apasses['qualifiers'].str.contains('Longball', na=False) &
                    ~apasses['qualifiers'].str.contains('Corner', na=False) &
                    ~apasses['qualifiers'].str.contains('Cross', na=False)]
    hlong_b = len(hlong)
    along_b = len(along)
    hacc_long_b = len(hlong[hlong['outcomeType'] == 'Successful'])
    aacc_long_b = len(along[along['outcomeType'] == 'Successful'])

    # Centros
    hcross = hpasses[hpasses['qualifiers'].str.contains('Cross', na=False)]
    across = apasses[apasses['qualifiers'].str.contains('Cross', na=False)]
    hcrss = len(hcross)
    acrss = len(across)
    hacc_crss = len(hcross[hcross['outcomeType'] == 'Successful'])
    aacc_crss = len(across[across['outcomeType'] == 'Successful'])

    # Faltas directas, córners, saques de banda, saques de meta
    hfk   = len(hpasses[hpasses['qualifiers'].str.contains('Freekick',  na=False)])
    afk   = len(apasses[apasses['qualifiers'].str.contains('Freekick',  na=False)])
    hcor  = len(hpasses[hpasses['qualifiers'].str.contains('Corner',    na=False)])
    acor  = len(apasses[apasses['qualifiers'].str.contains('Corner',    na=False)])
    htins = len(hpasses[hpasses['qualifiers'].str.contains('ThrowIn',   na=False)])
    atins = len(apasses[apasses['qualifiers'].str.contains('ThrowIn',   na=False)])
    hglkk = len(hpasses[hpasses['qualifiers'].str.contains('GoalKick',  na=False)])
    aglkk = len(apasses[apasses['qualifiers'].str.contains('GoalKick',  na=False)])

    # Regates
    hdrb = hdf[(hdf['type'] == 'TakeOn') & (hdf['qualifiers'].str.contains('Offensive', na=False))]
    adrb = adf[(adf['type'] == 'TakeOn') & (adf['qualifiers'].str.contains('Offensive', na=False))]
    htotal_drb = len(hdrb)
    atotal_drb = len(adrb)
    hacc_drb = len(hdrb[hdrb['outcomeType'] == 'Successful'])
    aacc_drb = len(adrb[adrb['outcomeType'] == 'Successful'])

    # Longitud media del saque de meta
    hgoalkick = hpasses[hpasses['qualifiers'].str.contains('GoalKick', na=False)].copy()
    agoalkick = apasses[apasses['qualifiers'].str.contains('GoalKick', na=False)].copy()
    hgoalkick['qualifiers_parsed'] = hgoalkick['qualifiers'].apply(ast.literal_eval)
    agoalkick['qualifiers_parsed'] = agoalkick['qualifiers'].apply(ast.literal_eval)
    hgoalkick['length'] = hgoalkick['qualifiers_parsed'].apply(extract_length)
    agoalkick['length'] = agoalkick['qualifiers_parsed'].apply(extract_length)
    hglkl = round(hgoalkick['length'].mean(), 2) if len(hgoalkick) > 0 else 0
    aglkl = round(agoalkick['length'].mean(), 2) if len(agoalkick) > 0 else 0

    return {
        'hposs': hposs,       'aposs': aposs,
        'hft': hft,           'aft': aft,
        'htotal_pass': htotal_pass, 'atotal_pass': atotal_pass,
        'hacc_pass': hacc_pass,     'aacc_pass': aacc_pass,
        'hlong_b': hlong_b,   'along_b': along_b,
        'hacc_long_b': hacc_long_b, 'aacc_long_b': aacc_long_b,
        'hcrss': hcrss,       'acrss': acrss,
        'hacc_crss': hacc_crss,     'aacc_crss': aacc_crss,
        'hfk': hfk,           'afk': afk,
        'hcor': hcor,         'acor': acor,
        'htins': htins,       'atins': atins,
        'hglkk': hglkk,       'aglkk': aglkk,
        'hglkl': hglkl,       'aglkl': aglkl,
        'htotal_drb': htotal_drb,   'atotal_drb': atotal_drb,
        'hacc_drb': hacc_drb,       'aacc_drb': aacc_drb,
    }


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    stats = get_pass_stats(df, hteamID, ateamID)

    print(f"\n{'='*50}")
    print(f"{'ESTADÍSTICAS':^50}")
    print(f"{'Local: ' + hteamName:^50}")
    print(f"{'Visitante: ' + ateamName:^50}")
    print(f"{'='*50}")
    print(f"{'Métrica':<25} {'Local':>10} {'Visitante':>10}")
    print(f"{'-'*50}")
    rows = [
        ('Posesión %',           stats['hposs'],      stats['aposs']),
        ('Field tilt %',         stats['hft'],         stats['aft']),
        ('Pases totales',        stats['htotal_pass'], stats['atotal_pass']),
        ('Pases efectivos',      stats['hacc_pass'],   stats['aacc_pass']),
        ('Balones largos',       stats['hlong_b'],     stats['along_b']),
        ('Balones largos efect.',stats['hacc_long_b'], stats['aacc_long_b']),
        ('Centros',              stats['hcrss'],       stats['acrss']),
        ('Centros efectivos',    stats['hacc_crss'],   stats['aacc_crss']),
        ('Faltas directas',      stats['hfk'],         stats['afk']),
        ('Córners',              stats['hcor'],        stats['acor']),
        ('Saques de banda',      stats['htins'],       stats['atins']),
        ('Saques de meta',       stats['hglkk'],       stats['aglkk']),
        ('Long. saque meta (m)', stats['hglkl'],       stats['aglkl']),
        ('Regates',              stats['htotal_drb'],  stats['atotal_drb']),
        ('Regates efectivos',    stats['hacc_drb'],    stats['aacc_drb']),
    ]
    for name, hval, aval in rows:
        print(f"{name:<25} {str(hval):>10} {str(aval):>10}")
    print(f"{'='*50}\n")
