from sklearn.datasets import load_iris 
from sklearn.model_selection import train_test_split 
from sklearn.svm import SVC 
from sklearn.naive_bayes import GaussianNB 
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis 
from sklearn.tree import DecisionTreeClassifier 
from sklearn.ensemble import RandomForestClassifier 
from sklearn.neighbors import KNeighborsClassifier 
from sklearn.neural_network import MLPClassifier 
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis 

names = [ "SVM", "Naive Bayes", "LDA", "QDA", "Decision Tree", "Random Forest", "Nearest Neighbors", "Neural Networks"] 
classifiers = [ SVC(), GaussianNB(), LinearDiscriminantAnalysis(), QuadraticDiscriminantAnalysis(), DecisionTreeClassifier(), RandomForestClassifier(), KNeighborsClassifier(), MLPClassifier(alpha=1, max_iter=1000)] 
X, y = load_iris(return_X_y=True) 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=0) 

clf = MLPClassifier(alpha=1, max_iter=1000) 
clf.fit(X_train, y_train) 
y_pred = clf.predict(X_test) 
N = y_test.shape[0] 
C = (y_test == y_pred).sum() 

print("Total points: %d Correctly labeled points : %d" %(N,C))

#for name, clf in zip(names, classifiers): 
#    clf.fit(X_train, y_train) 
#    score = clf.score(X_test, y_test) 
#    print(name +": " + str(score))
