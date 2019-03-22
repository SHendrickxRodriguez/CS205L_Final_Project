# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 13:31:49 2019

@author: Sebastian Hendrickx-Rodriguez
"""
import random

inputs = open("input.txt","r") 
outputs = open("output.txt","r")
trainfile = open("training1.txt","w")
valfile = open("validation1.txt","w")
testfile = open("testing1.txt","w")
n = random.sample(range(0,46656),46656) #Make a random list
tr = 0;
v = 0;
t = 0;
train = [0 for i in range(round(0.72*len(n)))] #Initialize your arrays
val = [0 for i in range(round(0.8*(len(n))) - round(0.72*len(n)))]
test = [0 for i in range(len(n) - round(0.8*len(n)))]
inlines = inputs.readlines() #Read all the angles
outlines = outputs.readlines() #Read all the stresses/strains
for k in range(0,len(n)): #Run through
    if k < round(0.72*len(n)): #Save 72% of the inputs/outputs in training
        train[tr] = inlines[n[k]] + outlines[2*n[k]] + outlines[2*n[k]+1] #Save angles/stresses/strains, python 
        trainfile.write(train[tr])                                          #starts indexing from 0 which is 
        tr = tr + 1                                                         #annoying af!
    elif round(0.72*len(n)) <= k < round(0.8*len(n)): #Save 8% for validation
        val[v] = inlines[n[k]] + outlines[2*n[k]] + outlines[2*n[k]+1]
        valfile.write(val[v])
        v = v + 1
    else: #Save remaining 20% for testing. This file is sacred.
        test[t] = inlines[n[k]] + outlines[2*n[k]] + outlines[2*n[k]+1]
        testfile.write(test[t])
        t = t + 1
        

inputs.close() #Close everything to avoid problems
outputs.close()
trainfile.close()
valfile.close()
testfile.close()