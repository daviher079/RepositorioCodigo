import matplotlib.pyplot as plt 
from scipy import stats 
x = [0,1,2,3,4] 
y = [3,5,5,6,7] 
slope, intercept, r, p, std_err = stats.linregress(x, y) 
print("slope: ", slope) 
print("intercept: ", intercept) 

def myfunc(x): 
    return slope * x + intercept 

mymodel = list(map(myfunc, x)) 

print(mymodel)
plt.scatter(x, y) 
plt.plot(x, mymodel) 
plt.show()
