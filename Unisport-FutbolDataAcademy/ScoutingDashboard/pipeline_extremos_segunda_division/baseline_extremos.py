import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_perfiles.csv")

base = pd.read_csv(BASE)

def correlacion_precio_nota (base):
    perfiles = ['REGATEADOR', 'FINALIZADOR', 'CREADOR']

    for perfil in perfiles:
        nota = base[perfil].corr(base['valor_mercado'], method='spearman')
        print(f'correlacion del perfil {perfil} con su valor de mercado: {nota:.2f}')

correlacion_precio_nota(base)
