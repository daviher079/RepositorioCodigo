#LDA Analisis discriminante lineal

from sklearn.datasets import load_iris 
from sklearn.datasets import make_classification 
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis 
X, y = make_classification(n_samples=1000, n_features=4, n_informative=2, n_redundant=0, random_state=0, shuffle=False) 
print(X) 
clf = LinearDiscriminantAnalysis() 
clf.fit(X, y) 
print(clf.predict([[0, 0, 0, 0]]))
 