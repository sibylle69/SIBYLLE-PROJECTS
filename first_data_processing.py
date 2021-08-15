#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression as logreg
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score
import warnings
warnings.filterwarnings('ignore')

freedom = pd.read_csv('data_test.csv')
#1540 rows

drop_nan = freedom.drop('Country code', axis=1)
#get rid of first column

freedom1 = drop_nan.apply(pd.to_numeric, errors='coerce')
freedom2 = freedom1.dropna()
#freedom1 is a new dataset where all strings are now NAN
#freedom2 is the new dataframe with all rows containing a '-' removed

index = freedom2.index
number_of_rows = len(index)
print(number_of_rows)
#Code to get number of rows (checking that it hasnt narrowed our data too much)

freedom2.head()
#print(freedom2)

from sklearn.model_selection import train_test_split
train, other = train_test_split(freedom2, test_size=0.2, random_state=0)
validation, test = train_test_split(other, test_size=0.5, random_state=0)
print('The sizes for train, test, and validation is {}'.format((len(train), len(test), len(validation))))
train.head()


# In[ ]:





# In[ ]:





# from sklearn.model_selection import train_test_split
# df_train, df_test = train_test_split(freedom2, test_size=0.2, random_state=0)
# df_valid, df_test = train_test_split(df_test, test_size=0.5, random_state=0)
# print('The sizes for train, test, and validation is {}'.format((len(train), len(test), len(validation))))
# train.head()

# In[2]:


freedom2 = freedom2.astype(int)
freedom2.pf_score[freedom2.pf_score <= 6.240000] = int(1)
freedom2.pf_score[freedom2.pf_score > 6.240000] = int(0)
freedom2.head()


# In[3]:


train2 = train.astype(int)
train2.pf_score[train2.pf_score <= 6.240000] = int(1)
train2.pf_score[train2.pf_score > 6.240000] = int(0)
train2.head()


# In[4]:


val2 = validation.astype(int)
val2.pf_score[val2.pf_score <= 6.240000] = int(1)
val2.pf_score[val2.pf_score > 6.240000] = int(0)
val2.head()


# In[5]:


test2 = test.astype(int)
test2.pf_score[test2.pf_score <= 6.240000] = int(1)
test2.pf_score[test2.pf_score > 6.240000] = int(0)
test2.head()


# In[6]:


###Compute the number of critical samples and samples in training set


# In[7]:


total_critical = sum(train2['pf_score'] == 1)
total_samples = len(train2)
print(total_critical)
print(total_samples)


# In[8]:


###compute Ginni impurity


# In[9]:


p = total_critical/total_samples

gini = 2 * p * (1 - p)

print('Gini Impurity for the decision node defined by `pf_score`: {}'.format(gini))


# In[10]:


###BUILDING A DECISION TREE


# In[ ]:





# In[ ]:


#1. divide training and validation sets into predictors and target variables


# In[12]:


X_train = train2.drop(columns=['pf_score'])
y_train = train2['pf_score']

X_val = val2.drop(columns=['pf_score'])
y_val = val2['pf_score']

X_test = test2.drop(columns=['pf_score'])
y_test = test2['pf_score']


# In[13]:


#Get mean and stds for train set
x_means = X_train.mean(axis=0)
x_stds = X_train.std(axis=0)

# Standardise the splits.
X_train = (X_train - x_means) / x_stds
X_val = (X_val - x_means) / x_stds
X_test = (X_test - x_means) / x_stds


# In[ ]:


###construct decision tree using training set


# In[14]:


# from sklearn.tree import DecisionTreeClassifier
from sklearn import tree  # Alligned to slide p.27

# dt = DecisionTreeClassifier(max_depth = 11) # Our classification tree
dt = tree.DecisionTreeClassifier(max_depth = 11)
dt = dt.fit(X_train, y_train)


# In[15]:


###Compute the accuracy, precision, and recall for the validation set with the trained decision tree.


# In[16]:


from sklearn.metrics import accuracy_score, precision_score, recall_score # Don't forget to import these

print('\nFor the validation set:')
print('Accuracy: \t{}'.format(accuracy_score(y_val, dt.predict(X_val))))
print('Precision: \t{}'.format(precision_score(y_val, dt.predict(X_val))))
print('Recall: \t{}'.format(recall_score(y_val, dt.predict(X_val))))


# In[ ]:


###Visualising the tree


# In[17]:


import sklearn.tree as tree
import graphviz

dot_data = tree.export_graphviz(dt, out_file=None) 
graph = graphviz.Source(dot_data) 

predictors = X_train.columns
dot_data = tree.export_graphviz(dt, out_file=None,
                                feature_names = predictors,
                                class_names = ('Negative', 'Positive'),
                                filled = True, rounded = True,
                                special_characters = True)
graph = graphviz.Source(dot_data)  
graph


# In[ ]:


### FIND MINIMUM IMPURITY


# In[ ]:




# In[21]:


max_depth = range(1,25)
t_score = []
v_score = []
d_out = 0

for d in max_depth:
    dt = tree.DecisionTreeClassifier(random_state=1, max_depth=d)
    dt.fit(np.asarray(X_train), y_train)
    v_score.append(accuracy_score(y_val, dt.predict(np.asarray(X_val))))
    t_score.append(accuracy_score(y_train, dt.predict(np.asarray(X_train))))
    if (d_out == 0) & (d>2):
        if (t_score[-1]/t_score[-2] < 1.001) | (np.mean(v_score[-3:]) < np.mean(v_score[-4:-1])):
            d_out = d-1
    
plt.plot(max_depth, t_score, label='Training')
plt.plot(max_depth, v_score, label='Validation')
plt.plot(d_out, t_score[d_out-1],'or')
plt.legend()
plt.xlabel('Maximum depth')
plt.ylabel('Model accuracy')
plt.show()
print(d_out)


# In[22]:


max_depth = range(1,25)
t_score = []
v_score = []
d_out = 0

for d in max_depth:
    dt = tree.DecisionTreeClassifier(random_state=1, max_depth=d)
    dt.fit(np.asarray(X_train), y_train)
    v_score.append(precision_score(y_val, dt.predict(np.asarray(X_val))))
    t_score.append(precision_score(y_train, dt.predict(np.asarray(X_train))))
    if (d_out == 0) & (d>2):
        if (t_score[-1]/t_score[-2] < 1.001) | (np.mean(v_score[-3:]) < np.mean(v_score[-4:-1])):
            d_out = d-1
    
plt.plot(max_depth, t_score, label='Training')
plt.plot(max_depth, v_score, label='Validation')
plt.plot(d_out, t_score[d_out-1],'or')
plt.legend()
plt.xlabel('Maximum depth')
plt.ylabel('Model precision')
plt.show()
print(d_out)


# In[23]:


max_depth = range(1,25)
t_score = []
v_score = []
d_out = 0

for d in max_depth:
    dt = tree.DecisionTreeClassifier(random_state=1, max_depth=d)
    dt.fit(np.asarray(X_train), y_train)
    v_score.append(recall_score(y_val, dt.predict(np.asarray(X_val))))
    t_score.append(recall_score(y_train, dt.predict(np.asarray(X_train))))
    if (d_out == 0) & (d>2):
        if (t_score[-1]/t_score[-2] < 1.001) | (np.mean(v_score[-3:]) < np.mean(v_score[-4:-1])):
            d_out = d-1
    
plt.plot(max_depth, t_score, label='Training')
plt.plot(max_depth, v_score, label='Validation')
plt.plot(d_out, t_score[d_out-1],'or')
plt.legend()
plt.xlabel('Maximum depth')
plt.ylabel('Model recall')
plt.show()
print(d_out)


# In[ ]:





# In[ ]:





# In[18]:


#Random forest
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(max_depth=11)
model = model.fit(X_train, y_train)
ypred = model.predict(X_val)
acc = accuracy_score(y_val, ypred)
prec = precision_score (y_val, ypred)
rec = recall_score(y_val, ypred)
print('Accuracy:{}'.format(acc))
print('Precision:{}'.format(prec))
print('Recall:{}'.format(rec))

print("")

estimator = model.estimators_[5]
dot_data = tree.export_graphviz(estimator, out_file=None)
graph = graphviz.Source(dot_data)
predictors = X_train.columns
dot_data = tree.export_graphviz(estimator, out_file=None,
                               feature_names = predictors,
                               class_names = ('Non-critical', 'Critical'),
                               filled = True, rounded = True,
                               special_characters = True)
graph = graphviz.Source(dot_data)
graph


# In[19]:


def model_optimise(x_train, y_train, x_val, y_val, depths, impurity, steps):
    n = impurity/steps + 1
    plt.figure(num=None, figsize=(8, 10), dpi=80, facecolor='w', edgecolor='k')
    maxima = []
    for i in range(1,depths+1):
        accuracies = []
        impurities = []
        for j in range(int(n)):
            predict_model = tree.DecisionTreeClassifier(max_depth=i,
                                                        min_impurity_decrease = j*steps)
            predict_model.fit(x_train,y_train)
            accuracies.append(accuracy_score(y_val,
                                             predict_model.predict(x_val)))
            impurities.append(j*steps)
    
    
    #print(i, accuracies, impurities)
    maxima.append([i,max(accuracies),steps*accuracies.index(max(accuracies))])
    depth_name = 'Depth = ' + str(i)
    plt.plot(impurities,accuracies,label=(depth_name))
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    #plt.legend(loc='upper right')
    plt.ylabel('Accuracy')
    plt.xlabel('Minimum Impurity Decrease')
    plt.title('Impact of Mimimum-Impurity-Decrease value on Accuracy for 11 depths')
    for k in range(len(maxima)):
        print(maxima[k])

res_val = model_optimise(X_train, y_train, X_val, y_val, 11, 0.01, 0.001)
res_train = model_optimise(X_train, y_train, X_train, y_train, 11, 0.01, 0.001)
depth = []
val_acc = []
train_acc = []
for x in range(len(res_val)):
    depth.append(x+1)
    val_acc.append(res_val[x][1])
    train_acc.append(res_train[x][1])
    
plt.figure(num=None, figsize=(5, 10), dpi=80, facecolor='w', edgecolor='k')
plt.plot(depth,train_acc,label='Train Accuracy')
plt.plot(depth, val_acc, label='Val Accuracy')
plt.legend()
plt.xlabel('Depth')
plt.ylabel('Accuracy')
plt.title('Graph showing the impact of Decision Tree Depth on Accuracy for Models with Optimum Gini-Impurity-Decrease')


# In[ ]:





# In[ ]:
