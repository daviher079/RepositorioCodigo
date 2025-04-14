from sklearn import datasets
import pandas as pd

# Cargar el dataset Iris
iris = datasets.load_iris()

# Crear un DataFrame con las características y las especies
df = pd.DataFrame(data=iris.data, columns=['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm'])
df['Species'] = iris.target_names[iris.target]  # Convertir etiquetas numéricas a nombres

# Guardar como CSV
df.to_csv('iris.csv', index=False)

print("Archivo 'iris.csv' generado exitosamente.")