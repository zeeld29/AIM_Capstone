"""Regenerate paired validation comparisons and reports from the saved analysis."""
import os
os.environ['OMP_NUM_THREADS']='4'
os.environ['OPENBLAS_NUM_THREADS']='4'
import json, hashlib, itertools
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from scipy.stats import norm, hypergeom
from sklearn.metrics import average_precision_score, roc_auc_score
ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
nb=ROOT / 'notebooks/05_model_evaluation.ipynb'
notebooks={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('notebooks').glob('*.ipynb')}
n=json.loads(nb.read_text()); ns={}
# Execute only data loading, pipeline definitions and candidate fitting; no notebook save/export cells.
for i in [2,4,6,8,10,12,14,16,18,21,25,42,44,46,48,57,59,61,71,73,75,84,86,88,90,92,105,107,109,111]:
 print('Reconstruct cell',i,flush=True)
 exec(''.join(n['cells'][i]['source']),ns)
ns['tuned_forest'] = ns['search'].best_estimator_
artifact=joblib.load('models/final_gradient_boosting.joblib')
print('Artifact keys',list(artifact),flush=True)
final=artifact.get('pipeline',artifact.get('model'))
models={'Logistic full':ns['logistic_model'],'Logistic selected':ns['selected_model'],'Logistic SVD':ns['svd_model'],'Tuned random forest':ns['tuned_forest'],'Original boosting':ns['boosting_model'],'Tuned boosting':final}
y=np.asarray(ns['y_val']); scores={k:m.predict_proba(ns['X_val'])[:,1] for k,m in models.items()}
# Compute current validation scores; historical point estimates are not assertions.
points=np.array([[average_precision_score(y,s),roc_auc_score(y,s)] for s in scores.values()])
# Refuse to overwrite notebook reports if candidate reconstruction differs.
recorded_path = ROOT / 'reports/significance_analysis/validation_metrics.csv'
if recorded_path.exists():
 recorded = pd.read_csv(recorded_path, index_col=0).loc[list(models), ['AP', 'ROC-AUC']]
 assert np.allclose(points, recorded.to_numpy(), rtol=0, atol=1e-12), 'Standalone candidates do not match current notebook validation scores.'
print('Current validation scores',points,flush=True)
out=ROOT / 'reports/significance_analysis'
out.mkdir(parents=True, exist_ok=True)
pd.DataFrame({'label':y,**scores}).to_csv(out/'validation_predictions.csv',index=False)
# DeLong structural components: each positive's concordance against negatives and vice versa, ties count 1/2.
vpos=[];vneg=[]
for s in scores.values():
 p=s[y==1];q=s[y==0];ps=np.sort(p);qs=np.sort(q)
 vpos.append((np.searchsorted(qs,p,side='left')+np.searchsorted(qs,p,side='right'))/(2*len(q)))
 vneg.append(1-(np.searchsorted(ps,q,side='left')+np.searchsorted(ps,q,side='right'))/(2*len(p)))
cov=np.cov(vpos)/sum(y==1)+np.cov(vneg)/sum(y==0)
# Paired stratified bootstrap fixes class counts; same resampled patients for every model.
# Multiplicity weights and tie blocks yield exactly the AP of duplicated bootstrap rows.
orders=[]
for s in scores.values():
 order=np.argsort(-s,kind='stable');ends=np.r_[np.flatnonzero(np.diff(s[order])!=0),len(s)-1]
 orders.append((order,ends))
rng=np.random.default_rng(20261012);pos=np.flatnonzero(y==1);neg=np.flatnonzero(y==0);B=5000
boot=np.empty((B,len(models)))
for b in range(B):
 counts=np.bincount(np.r_[rng.choice(pos,len(pos)),rng.choice(neg,len(neg))],minlength=len(y))
 for j,(order,ends) in enumerate(orders):
  w=counts[order];tp=np.cumsum(w*y[order])[ends];total=np.cumsum(w)[ends]
  boot[b,j]=np.sum(np.diff(np.r_[0,tp])*np.divide(tp,total,out=np.zeros_like(tp,dtype=float),where=total>0))/len(pos)
 if (b+1)%1000==0:print('Bootstrap',b+1,flush=True)
rows=[];names=list(models)
for i,j in itertools.combinations(range(len(names)),2):
 for metric,col in [('AP',0),('ROC-AUC',1)]:
  delta=points[i,col]-points[j,col]
  if metric=='AP':
   diffs=boot[:,i]-boot[:,j];lo,hi=np.quantile(diffs,[.025,.975]);se=diffs.std(ddof=1)
   method='Paired stratified bootstrap CI; approximate normal bootstrap-SE test'
  else:
   se=np.sqrt(max(0,cov[i,i]+cov[j,j]-2*cov[i,j]));lo=delta-1.959963984540054*se;hi=delta+1.959963984540054*se
   method='Paired DeLong asymptotic test and CI'
  p=2*norm.sf(abs(delta/se))
  rows.append(dict(model_A=names[i],model_B=names[j],metric=metric,difference_A_minus_B=delta,CI95_lower=lo,CI95_upper=hi,SE=se,p_raw=p,method=method))
r=pd.DataFrame(rows)
# Holm correction across all 30 learned-model comparisons (15 pairs, two metrics).
ix=np.argsort(r.p_raw.to_numpy());adj=np.maximum.accumulate((len(r)-np.arange(len(r)))*r.p_raw.to_numpy()[ix]);r['p_Holm']=0.;r.loc[ix,'p_Holm']=np.minimum(adj,1);r['significant_Holm_0.05']=r.p_Holm<.05
r.to_csv(out/'pairwise_tests.csv',index=False)
metrics=pd.DataFrame(points,columns=['AP','ROC-AUC'],index=names);metrics['AP_CI95_lower']=np.quantile(boot,.025,axis=0);metrics['AP_CI95_upper']=np.quantile(boot,.975,axis=0);metrics.to_csv(out/'validation_metrics.csv')
# Fixed final model: top-20% selected set versus a uniformly random equal-size set.
ytest=np.asarray(ns['y_test']);stest=final.predict_proba(ns['X_test'])[:,1];k=int(np.ceil(.2*len(ytest)));selected=np.argsort(-stest,kind='stable')[:k];hits=int(ytest[selected].sum())
p_random=hypergeom.sf(hits-1,len(ytest),int(ytest.sum()),k)
print('FINAL COMPARISONS\n',r[(r.model_A=='Tuned boosting')|(r.model_B=='Tuned boosting')].to_string(index=False),flush=True)
print('TOP20',len(ytest),int(ytest.sum()),k,hits,'random p',p_random,flush=True)
meta={'validation_n':len(y),'validation_positives':int(y.sum()),'bootstrap_resamples':B,'seed':20261012,'test_n':len(ytest),'test_positives':int(ytest.sum()),'top20_selected':k,'top20_hits':hits,'random_selection_one_sided_p':float(p_random),'notebooks_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in notebooks.items())}
(out/'analysis_metadata.json').write_text(json.dumps(meta,indent=2))
print(meta)
