import json
import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# CAMBIA ESTA URL PARA CADA PARTIDO (usar siempre /live/)
MATCH_URL = 'https://es.whoscored.com/matches/1974941/live/europa-champions-league-2025-2026-real-madrid-bayern-munich'

MATCH_FOLDER = os.path.join(os.path.dirname(__file__), 'Match')


def build_filename(data):
    home = data['matchCentreData']['home']['name'].replace(' ', '_')
    away = data['matchCentreData']['away']['name'].replace(' ', '_')

    # La fecha está en matchheader params de la página — usamos la fecha actual como fallback
    try:
        raw_date = data['matchCentreData'].get('startTime', '')
        date_str = datetime.strptime(raw_date[:10], '%Y-%m-%d').strftime('%Y-%m-%d')
    except Exception:
        date_str = datetime.today().strftime('%Y-%m-%d')

    return f'{home}_vs_{away}_{date_str}.json'


def download_match_data(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        print(f'Abriendo {url}...')
        page.goto(url, wait_until='networkidle', timeout=60000)
        print('Esperando carga completa...')
        time.sleep(8)

        data = page.evaluate("() => require.config.params['args']")

        # Obtener la fecha del partido desde matchheader
        matchheader = page.evaluate("() => require.config.params['matchheader'] || {}")
        if matchheader.get('input') and len(matchheader['input']) > 4:
            try:
                raw_date = matchheader['input'][4]  # '07/04/2026 21:00:00'
                date_str = datetime.strptime(raw_date[:10], '%d/%m/%Y').strftime('%Y-%m-%d')
                data['_matchDate'] = date_str
            except Exception:
                pass

        browser.close()

    os.makedirs(MATCH_FOLDER, exist_ok=True)
    filename = build_filename(data)
    output_path = os.path.join(MATCH_FOLDER, filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'Datos guardados en: {output_path}')
    return output_path


if __name__ == '__main__':
    download_match_data(MATCH_URL)
