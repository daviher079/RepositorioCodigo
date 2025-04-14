from sklearn.datasets import load_iris 
from sklearn.model_selection import train_test_split 
from sklearn.tree import DecisionTreeClassifier 
X, y = load_iris(return_X_y=True) 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=0) 
#X_train , y_train : Datos de entrenamiento (para ajustar el modelo).
#X_test , y_test : Datos de prueba (para evaluar el modelo).
clf = DecisionTreeClassifier() 
clf.fit(X_train, y_train) 
y_pred = clf.predict(X_test) 
N = y_test.shape[0] 
C = (y_test == y_pred).sum() 
print("Total points: %d Correctly labeled points : %d" %(N,C))
