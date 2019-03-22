#Sebastian Hendrickx-Rodriguez
#Machine Learning Code to determine stress and strain of bird feather
#rachis from three angles corresponding to fiber angle in three layers of composite cylinder

from IPython import get_ipython
get_ipython().magic('reset -sf') #Reset all variables
import torch
import json
import numpy as np
import matplotlib.pyplot as plt



dtype = torch.float
device = torch.device("cpu")
# device = torch.device("cuda:0") # Uncomment this to run on GPU

#Read in data
#Data has following format:
#    [t1,t2,t3]        <---Angles of fibers in three composite layers 0<t<175
#    [s1,s2,s3,s4,s5]  <---Stresses at five different points on cylinder
#    [e1,e2,e3,e4,e5]  <---Strains at five different points on cylinder
trainfile = open("training.txt","r")
#valfile = open("validation.txt","r")
testfile = open("testing.txt","r")

#Read in 400 bytes = 2 examples (6 angles and 10 stresses/strains)
lines = trainfile.readlines()
#print(lines)

#Initialize
x = [0 for i in range(round(len(lines)/3))]
y = [0 for i in range(round(len(lines)/3))]
var = np.var(list(range(0,180,5))*3)
    
#print(x)
#print(y)    
    
# N is batch size; D_in is input dimension;
# H is hidden dimension; D_out is output dimension.
N, D_in, H, D_out = 50, 3, 5, 10


# Create random input and output data
#x = torch.randn(N, D_in, device=device, dtype=dtype)
#y = torch.randn(N, D_out, device=device, dtype=dtype)

# Randomly initialize weights
w1 = torch.randn(D_in, H, device=device, dtype=dtype)
w2 = torch.randn(H, D_out, device=device, dtype=dtype)

learning_rate = 1
reg_strength = 0.01
losst = [0 for i in range(500)]
lossv = [0 for i in range(500)]
for t in range(500): 
    xt = [0 for i in range(round(0.8*len(lines)/3))]
    yt = [0 for i in range(round(0.8*len(lines)/3))]
    xv = [0 for i in range(round(0.2*len(lines)/3))]
    yv = [0 for i in range(round(0.2*len(lines)/3))]
    m = 0
    n = 0
    j = np.random.choice(len(x), len(x), replace=False)
    for k in range(0,int(len(lines)/3)):
        if k < round(0.8*len(lines)/3):
            xt[m] = np.subtract(json.loads(lines[3*j[k]]), [90, 90, 90])
            #xt[m] = json.loads(lines[3*j[k]])
            yt[m] = json.loads(lines[3*j[k] + 1]) + json.loads(lines[3*j[k] + 2])
            m = m + 1
        else:
            xv[n] = np.subtract(json.loads(lines[3*j[k]]), [90, 90, 90])
            #xv[n] = json.loads(lines[3*j[k]])
            yv[n] = json.loads(lines[3*j[k] + 1]) + json.loads(lines[3*j[k] + 2])
            n = n + 1
    
    #print(xv)
    #print(yv)
    xt = torch.tensor(xt/var, device=device, dtype=torch.float) #Matrix containing angles, three per example
    yt = torch.tensor(yt, device=device, dtype=torch.float) #Matrix containing stresses/strains, 5 stress + 5 strains
                                                      #per example
    xv = torch.tensor(xv/var, device=device, dtype=torch.float)
    yv = torch.tensor(yv, device=device, dtype=torch.float)
    
    #VALIDATION
    # Forward pass: compute predicted y
    hv = xv.mm(w1) #Matrix multiplication to find h
    h_reluv = hv.clamp(min=0)
    y_predv = h_reluv.mm(w2)

    # Compute and print loss
    loss_ev = (y_predv - yv).pow(2).sum().item()/len(yv)  #Error
    loss_rv = reg_strength*(w1.pow(2).sum().item() + w2.pow(2).sum().item()) #Regularization
    lossv[t] = loss_ev + loss_rv
    
    #TRAINING
    # Forward pass: compute predicted y
    h = xt.mm(w1) #Matrix multiplication to find h
    h_relu = h.clamp(min=0)
    y_pred = h_relu.mm(w2)

    # Compute and print loss
    loss_et = (y_pred - yt).pow(2).sum().item()/len(yt)  #Error
    loss_rt = reg_strength*(w1.pow(2).sum().item() + w2.pow(2).sum().item()) #Regularization
    losst[t] = loss_et + loss_rt
    #print(t, loss, loss_e, loss_r)

    # Backprop to compute gradients of w1 and w2 with respect to loss
    grad_y_pred = 2.0 * (y_pred - yt)/len(yt)
    grad_w2 = h_relu.t().mm(grad_y_pred) + reg_strength*(w2)
    grad_h_relu = grad_y_pred.mm(w2.t())
    grad_h = grad_h_relu.clone()
    grad_h[h < 0] = 0
    grad_w1 = xt.t().mm(grad_h) + reg_strength*(w1)

    # Update weights using gradient descent
    w1 -= learning_rate * grad_w1
    w2 -= learning_rate * grad_w2
    
    
#TESTING
linest = testfile.readlines()
xtr = [0 for i in range(round(len(linest)/3))]
ytr = [0 for i in range(round(len(linest)/3))]
i = 0
for k in range(0,int(len(linest)/3)):
        xtr[i] = np.subtract(json.loads(linest[3*k]), [90, 90, 90])
        ytr[i] = json.loads(linest[3*k + 1]) + json.loads(linest[3*k + 2])
        i = i + 1

xtr = torch.tensor(xtr/var, device=device, dtype=torch.float)
ytr = torch.tensor(ytr, device=device, dtype=torch.float)
# Forward pass: compute predicted y
h = xtr.mm(w1) #Matrix multiplication to find h
h_relu = h.clamp(min=0)
y_pred = h_relu.mm(w2)
error = (y_pred - ytr).pow(2).sum().item()/len(ytr)  #Error
print(error)


trainfile.close()
#valfile.close()
testfile.close()

#fig = plt.figure()
#ax = fig.add_subplot(111)
plt.plot(range(0,100),losst[0:100],'r--',range(0,100),lossv[0:100],'b--')
plt.plot(range(400,500),losst[400:500],'r--',range(400,500),lossv[400:500],'b--')


#Train on [20-180] and then test on [0-20] to test extrapolation. 


