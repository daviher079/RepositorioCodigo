#pip install statsbombpy
#from statsbombapi import sb

sb.competitions()

partidos = sb.matches(competition_id=43, season_id=13)

eventos = sb.events(match_id=8657)

eventos.head()

eventos = eventos [['team', 'type', 'minute', 'location', 'pass_end_location', 'player']]

#numero de eventos que mostramos
print(eventos.head(20))
