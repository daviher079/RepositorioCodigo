import LanusStats as ls
import matplotlib.pyplot as plt
import requests

# Cambia este valor por el código del partido que aparece en la URL de Fotmob
# Ejemplo: https://www.fotmob.com/es/matches/afc-bournemouth-vs-fulham/2uiul6#4813435
match_id = 4813435

# Obtener nombres de equipos automáticamente
try:
    url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
    data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).json()
    home_team = data["header"]["teams"][0]["name"]
    away_team = data["header"]["teams"][1]["name"]
    match_title = f"{home_team} vs. {away_team}"
except Exception:
    match_title = f"Partido {match_id}"

# Dibujar el momentum
ls.visualizations.fotmob_match_momentum_plot(match_id)

# Personalizar el gráfico
ax = plt.gca()
ax.set_title(f"Match momentum — {match_title}", loc="left", fontsize=13)
ax.set_xlabel("Minuto")
ax.set_ylabel("Amenaza (momentum)")
ax.grid(True, alpha=0.3)

# Líneas de mitad y final
for m in [45, 90]:
    ax.axvline(m, linestyle="--", linewidth=1, alpha=0.6)

plt.tight_layout()
plt.show()
