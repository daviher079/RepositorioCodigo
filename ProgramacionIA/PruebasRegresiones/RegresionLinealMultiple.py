from sklearn import linear_model 
import numpy as np 

x = np.array([[0,3,5],[1,4,6],[2,5,7],[3,6,8],[4,7,9]]) 
y = np.array([3,5,5,6,7]) 
reg = linear_model.LinearRegression() 
reg.fit(x, y) 

print('Coefficients: \n', reg.coef_) 
print('Intercept: \n', reg.intercept_) 
pred = reg.predict([[5,8,10]]) 
print('Predition: \n', pred)
