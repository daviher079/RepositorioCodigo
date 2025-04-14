#Analisis de componentes principales

from sklearn.datasets import make_classification 
from sklearn.decomposition import PCA 
X, y = make_classification(n_samples=1000, n_features=4, n_informative=2, n_redundant=0, random_state=0, shuffle=False) 
print(X) 
clf = PCA() 
#es un método no supervisado , por lo que no utiliza las etiquetas y. 
# La implementación correcta sería simplemente clf.fit(X). 
# Pasar y no afecta el resultado en este caso, ya que PCA lo ignora.

clf.fit(X, y) 
print(clf.explained_variance_ratio_) 
print(clf.singular_values_)