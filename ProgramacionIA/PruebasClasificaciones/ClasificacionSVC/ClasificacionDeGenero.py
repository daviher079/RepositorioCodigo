from sklearn import svm 
X = [[170, 70, 10], [180, 80,12], [170, 65, 8],[160, 55, 7]]
#Altura[cm], Peso[kg], Talla calzado[UK] 
y = [0, 0, 1, 1] 
# #Género, 0: Masculino, 1: Femenino 
clf = svm.SVC()

clf.fit(X, y) 
#Predicción 

p = clf.predict([[160, 60, 7]]) 
print(p)
