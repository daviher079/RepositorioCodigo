from sklearn.datasets import load_iris 
from sklearn.model_selection import train_test_split 
from sklearn.neighbors import KNeighborsClassifier 
X, y = load_iris(return_X_y=True) 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=0) 
clf = KNeighborsClassifier() 
clf.fit(X_train, y_train) 
y_pred = clf.predict(X_test) 
print("Total points: %d Correctly labeled points : %d" %(y_test. shape[0],(y_test == y_pred).sum()))
