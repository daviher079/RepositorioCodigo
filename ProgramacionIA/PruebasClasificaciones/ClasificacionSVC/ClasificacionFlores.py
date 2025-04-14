from sklearn import svm, datasets 
iris = datasets.load_iris() 
# Tome las dos primeras características: longitud del sépalo y ancho del sépalo 

X = iris.data[:, :2] 
y = iris.target 
#0: Setosa, 1: Versicolour, 2:Virginica 
print(y) 
clf = svm.SVC() 
clf.fit(X, y) 
# Predecir la flor para un largo y ancho de sépalo dado 

p = clf.predict([[5.4, 3.2]])
print(p)