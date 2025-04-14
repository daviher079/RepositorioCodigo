from sklearn.datasets import load_iris 
from sklearn.model_selection import train_test_split 
from sklearn.naive_bayes import GaussianNB 
X, y = load_iris(return_X_y=True) 
print(X) 
clf = GaussianNB() 
clf.fit(X, y) 
p = clf.predict([[5.0, 3.4, 1.5, 0.4]]) 
print(p)
