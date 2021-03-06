# -*- coding: utf-8 -*-

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sb
import time

def prep_data(phenotype):
  pheno = pd.read_csv('/content/drive/MyDrive/Antibiotic Resistance Research/metadata.csv', index_col=0)
  pheno = pheno.dropna(subset=[phenotype])
  pheno = pheno[phenotype]

  X = pd.read_csv('/content/drive/MyDrive/Antibiotic Resistance Research/' + phenotype + '_gwas_filtered_unitigs.Rtab', sep=" ", index_col=0, low_memory=False)
  X = X.transpose()
  X = X[X.index.isin(pheno.index)]
  pheno = pheno[pheno.index.isin(X.index)]
  return X, pheno

phenotype = 'cfx_sr'
X, pheno = prep_data(phenotype)
performance = []
method = []
times = []

max(uni_len)

unitigs = X.columns
print(unitigs[:10])
mylen = np.vectorize(len)
uni_len = mylen(unitigs)
sb.distplot(uni_len)
plt.xlim(0, 100)

X.to_csv('dataset_cfx.csv')

X

from sklearn.model_selection import KFold
from sklearn.model_selection import GroupKFold
from sklearn.model_selection import GridSearchCV

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import plot_confusion_matrix
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import learning_curve
from sklearn.model_selection import ShuffleSplit
from sklearn.metrics import classification_report
from sklearn import metrics

def fitmodel(X, pheno, model, modelname, method, performance, times, metric_list):

  # time how long it takes to train each model type
  start = time.process_time()
  
  # split data into train/test sets
  X_train, X_test, y_train, y_test = train_test_split(X, pheno, test_size=0.33, random_state=0)
  
  # perform grid search to identify best hyper-parameters
  model.fit(X_train, y_train)
  
  # predict resistance in test set
  y_pred = model.predict(X_test)
  y_pred[y_pred<0.5] = 0
  y_pred[y_pred>0.5] = 1

  score = metrics.accuracy_score(y_test, y_pred)
  performance = np.append(performance, score)
  method = np.append(method, modelname)
  times = np.append(times, (time.process_time() - start))


  print("Confusion matrix for this fold")
  plot_confusion_matrix(model,X_test,y_test)
  print("Score: " + str(score))
  #false_positive_rate, true_positive_rate, thresholds = metrics.roc_curve(y_test, gs_clf.predict_proba(X_test)[:,1])
  #auc = metrics.auc(false_positive_rate, true_positive_rate)
  print(classification_report(y_test, y_pred))
  auc2 = metrics.roc_auc_score(y_test, y_pred)
  print("******** {} *******".format(auc2))

  tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
  print("Sensitivity: " + str(tp/(tp+fn)))
  print("Specificity: " + str(tn/(tn+fp)))
  metrics.plot_roc_curve(model, X_test, y_test)
  plt.show()

  metricss = [score,(tp/(tp+fn)),(tn/(tn+fp)),auc2]
  metric_list.append(metricss)

  return model, method, performance, times, metric_list

metric_list=[]

from sklearn.neural_network import MLPClassifier

mlp = MLPClassifier(max_iter=300,solver='adam',alpha=1e-05,learning_rate='invscaling',batch_size='auto')
mlp_params = {
  'solver': ['adam'],
  'alpha': [1e-05],
  'learning_rate': ['invscaling'],
  'batch_size': ['auto']
}
mlp_model, method, performance, times, metric_list = fitmodel(X, pheno, mlp, "MLP", method, performance, times, metric_list)

from sklearn.svm import SVC

svm = SVC(class_weight='balanced')
svm_params = {
  'C': [0.1],
  'gamma': ['scale'],
  'kernel': ['linear']
}
svm_model, method, performance, times, metric_list = fitmodel(X, pheno, svm, "SVM", method, performance, times, metric_list)

from sklearn.ensemble import RandomForestClassifier

rfc = RandomForestClassifier(class_weight='balanced',n_estimators=100,min_samples_split=2,criterion='entropy')
rfc_params = {
  'n_estimators': [200],
  'min_samples_split': [3],
  'criterion': ['entropy']
}
rfc_model, method, performance, times, metric_list = fitmodel(X, pheno, rfc, "RFC", method, performance, times, metric_list)

from sklearn.neighbors import KNeighborsClassifier

knn = KNeighborsClassifier(weights='distance',n_neighbors=4)
knn_params = {
  'weights': ['uniform','distance'],
  'n_neighbors': [4,6]
}
knn_model, method, performance, times, metric_list = fitmodel(X, pheno, knn, "KNN", method, performance, times, metric_list)

import xgboost as xgb

xgb_mod = xgb.XGBClassifier(random_state=0,alpha=1e-5,colsample_bytree=0.6,gamma=0.05,learning_rate=0.01,max_depth=2,objective='binary:hinge',subsample=0.3)

xgb_params = {
    'alpha': [1e-5], 
    'colsample_bytree': [0.6],
    'gamma': [0.05], 
    'learning_rate': [0.01], 
    'max_depth': [2], 
    'objective': ['binary:hinge'], 
    'subsample': [0.3]
}

xgb_model, method, performance, times, metric_list = fitmodel(X, pheno, xgb_mod, "XGBoost", method, performance, times, metric_list)

from sklearn.naive_bayes import GaussianNB

gnb = GaussianNB()
gnb_params = { 
    'var_smoothing': [1e-9,1e-8,1e-10]
}

gnb_model, method, performance, times, metric_list = fitmodel(X, pheno, gnb, "GNB", method, performance, times, metric_list)

from sklearn.linear_model import SGDClassifier

sgd = SGDClassifier(random_state=0,class_weight='balanced')
sgd_params = { 
    'penalty': ['l2','l1'],
    'eta0': [0.1,0.01],
    'learning_rate': ['invscaling'],
    'alpha': [0.0001,1e-05,0.001]
}

sgd_model, method, performance, times, metric_list = fitmodel(X, pheno, sgd, "SGD", method, performance, times, metric_list)

from sklearn.linear_model import LogisticRegression

lr = LogisticRegression(random_state=0,class_weight='balanced')
lr_params = { 
    'C': [1.0,0.1]
}

lr_model, method, performance, times, metric_list = fitmodel(X, pheno, lr, "LogReg", method, performance, times, metric_list)

metric_list

sb.set_context("talk")
plt.title("Model Performance - Ciprofloxacin Resistance", y=1.1)
sb.swarmplot(x=method, y=performance, palette="YlGnBu_d", size=8)
sb.despine()
plt.ylabel("Balanced accuracy")
plt.xticks(rotation=30, ha='right')
plt.ylim([0.9,1.01])

metricsdf = pd.DataFrame(metric_list,columns=['Accuracy','Sensitivity','Specificity','AUC'])

metricsdf

metricsdf.to_csv('model_metrics_cfx.csv')

sum=0
for i in performance[5:11]:
  sum+=i

print(sum/5)

def plot_coefficients(classifier1, classifier2, feature_names, top_features=5):
    coef = (classifier1.coef_.ravel())
    top_positive_coefficients = np.argsort(coef)[-top_features:]
    top_negative_coefficients = np.argsort(coef)[:top_features]
    top_coefficients = np.hstack([top_negative_coefficients, top_positive_coefficients])
    print(coef[top_coefficients])
    # create plot
    sb.set_context("poster")
    plt.figure(figsize=(15, 5))
    plt.title("Feature Importances (Logistic Regression) - Ciprofloxacin Resistance")
    colors = ['crimson' if c < 0 else 'cornflowerblue' for c in coef[top_coefficients]]
    plt.bar(np.arange(2 * top_features), coef[top_coefficients], color=colors)
    feature_names = np.array(feature_names)
    plt.xticks(np.arange(0, 1 + 2 * top_features), feature_names[top_coefficients], rotation=60, ha='right')
    #plt.show()
    np.asarray(feature_names)[top_positive_coefficients]
    print("Top negative predictors: ", np.asarray(feature_names)[top_negative_coefficients])
    top_positive_coefficients = np.argsort(coef)[-5:]
    print("Top positive predictors: ", np.asarray(feature_names)[top_positive_coefficients])


plot_coefficients(lr_model, lr_model, list(X.columns))

num_top=10
importances = rfc_model.feature_importances_
std = np.std([tree.feature_importances_ for tree in rfc_model.estimators_],
             axis=0)
indices = np.argsort(importances)[::-1][:num_top]
feature_names = list(X.columns)

# Plot the feature importances of the forest
sb.set_context("poster")
plt.figure(figsize=(num_top, 5))
plt.title("Feature Importances (RFC) - Cefixime Resistance")
plt.bar(range(num_top), importances[indices],
       color="crimson", align="center")
plt.xticks(range(num_top), np.asarray(feature_names)[indices], rotation=60, ha='right')
plt.xlim([-1, num_top])
plt.ylim([0, 0.08])
plt.show()

feature_names = list(X.columns)
for pp in np.asarray(feature_names)[indices]:
  print("'"+pp+"',"),

xgb.plot_importance(xgb_model, max_num_features = 5)
plt.show()

contigs = pd.concat([X['GGGTTTAAAACGTCGTGAGACAGTTTGGTCCCTATCTGCAGTGGGCGTTGGAAGTTTGACG'],X['ACCGTGTAGCCCTGCTGTTTGAACGCCAACCCGTTTTTGTGCGCCCAACGGCTCACAAGGT'],X['TTTCAGACGGCATCTGCCTGGCAAACGCTTCCC'],X['AAAGGCGTTTGCGTTGCGAGGAGTTCATATC'],X['CATCTGCCTGGCAAACGCTTCCCCGTCGCCCTCGAA'],X['CCCCACCGAAATCAAAGGCAAATATGTTCAAAGCG'],X['GTCAAACCTGCCGACCCTTCACAGCATTCGCGC'],X['ACCGTAACCGGCAATGCGGATATTACGGTCA'],X['CGCGCGACAAAGCCGACGCCGACAACGACGC'],X['GGAAGGCGTTCCCCGGAGCACCCAGGAGGCCATGGC']],axis=1)

xdf=pd.concat([contigs, pheno], axis=1)
xdf

R2 = r2_score([xdf[xdf.columns[0]],xdf[xdf.columns[1]]], xdf[xdf.columns[2]])
print(R2)

from sklearn import linear_model

lmx=pd.concat([xdf[xdf.columns[0]], xdf[xdf.columns[1]]], axis=1)
lmy=xdf[xdf.columns[2]]

lm = linear_model.LinearRegression()
model = lm.fit(lmx,lmy)
print(lm.score(lmx,lmy))

from scipy.stats import fisher_exact 

def p_val_chisq(data):
  stat, p = fisher_exact(data) 
  
  alpha = 0.05
  print("p value is " + str(p)) 
  if p <= alpha: 
      return [1,0]
  else: 
      return [0,1]

def chi_sq_vals(contig):
  full_list=[]
  sub_list=[]
  allcorrect=True
  print("**********")
  print(contig)
  contig_col = X[contig]
  dataframe=pd.concat([contig_col, pheno], axis=1)
  for j in [1,0]:
    for i in [1,0]:
      df1=dataframe[dataframe[contig]==i]
      df2=df1[df1[phenotype]==j]
      if(len(df2.index)<=1):
        allcorrect=False
      print(len(df2.index))
      sub_list.append(len(df2.index))
    full_list.append(sub_list)
    sub_list=[]
  if(allcorrect==True):
    rr = p_val_chisq(full_list)
    return [rr[0],rr[1]]
  else:
    return [0,1]

listcontigs=unitigs.tolist()

listcontigs

indep=0
dep=0
list_significant=[]

for ctig in listcontigs:
  rrr = chi_sq_vals(ctig)
  print(rrr)
  dep+=(rrr[0])
  indep+=rrr[1]
  if rrr[0]==1:
    list_significant.append(ctig)
print("Significant "+str(dep),"|| Not sig "+str(indep))

print(list_significant)
