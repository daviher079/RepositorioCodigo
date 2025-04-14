from sklearn import svm, datasets 
import pandas as pd 
from matplotlib import pyplot 
from pandas.plotting import scatter_matrix 
df = pd.read_csv('https://gist.githubusercontent.com/curran/a08a1080b88344b0c8a7/raw/0e7a9b0a5d22642a06d3d5b9bcbad9890c8ee534/iris.csv') 
print(df.shape) 
#Muestra el numero total de filas y columnas del fichero
print(df.head(10)) 
#Muestra las 10 primeras filas
print(df.tail(10)) 
#Muestra las 10 ultimas filas
print(df.describe())
#Muestra el resumen de los datos
print(df.isna().sum().sum()) 
#Contar NAN
df = df.dropna()
#drop NAN values
print(df.groupby('species').size()) 
# Histogramas 
df.hist() 
pyplot.show() 

# Matriz de diagrama de dispersión 
scatter_matrix(df) 
pyplot.show() 

X = df.values[:,:2] 
s = df['species'] 
d = dict([(y,x) for x,y in enumerate(sorted(set(s)))]) 
y = [d[x] for x in s] 
clf = svm.SVC() 
clf.fit(X, y) 
# Predecir la flor para un largo y ancho de sépalo dado 
p = clf.predict([[5.4, 3.2]]) 
print(p)