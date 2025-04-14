from sklearn import svm, datasets 
import pandas as pd 

df = pd.read_csv('PruebasClasificacionSVM/iris.csv') 
X = df.values[:,:2] 
s = df['Species']

d = dict([(y,x) for x,y in enumerate(sorted(set(s)))]) 

y = [d[x] for x in s] 

clf = svm.SVC() 
clf.fit(X, y) 
# Predecir la flor para un largo y ancho de sépalo dado 

p = clf.predict([[5.4, 3.2]]) 
print(p)
