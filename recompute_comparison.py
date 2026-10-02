"""One consistent execution for all 40 configurations on frozen input matrices.

Run from any directory with Python 3.9.12 and requirements-analysis.txt.
Usage: python recompute_comparison.py --data-root PATH --out PATH
The submission data root contains trait_descriptions.csv, split_token_ids.json,
and four frozen pretrained-representation NPZ files. TF-IDF is fitted separately
on every training partition. Holdout/ and CV/ CSV layouts are an archival fallback
and were not used for the revised TF-IDF comparison.
No catch-and-zero fallback, score clipping, embedding regeneration, split change,
or parameter search over outer validation sets is used.
"""
import argparse
import hashlib
import json
import platform
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import sklearn
import xgboost
import lightgbm
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import LinearRegression, RidgeCV, LassoCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import LinearSVR
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.feature_extraction.text import TfidfVectorizer
from threadpoolctl import threadpool_limits

parser = argparse.ArgumentParser()
parser.add_argument('--data-root', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--only', choices=['TF-IDF','GloVe','FastText','Sentence-BERT','GTE'], default=None)
parser.add_argument('--only-models', nargs='+', default=None)
args = parser.parse_args()
args.out.mkdir(parents=True, exist_ok=True)
reps = ['TF-IDF','GloVe','FastText','Sentence-BERT','GTE']
if args.only:
    reps = [args.only]
models = {
    'OLS': lambda: LinearRegression(),
    'Ridge': lambda: RidgeCV(alphas=[0.1,1.0,10.0]),
    'Lasso': lambda: LassoCV(cv=3,n_alphas=100,max_iter=100000,tol=1e-4,random_state=42,n_jobs=2),
    'PLS': lambda: PLSRegression(n_components=20,scale=True,max_iter=1000,tol=1e-6),
    'RF': lambda: RandomForestRegressor(n_estimators=100,max_features=1.0,random_state=42,n_jobs=4),
    'XGB': lambda: xgboost.XGBRegressor(n_estimators=100,learning_rate=0.1,max_depth=6,tree_method='hist',random_state=42,n_jobs=4),
    'LGBM': lambda: lightgbm.LGBMRegressor(n_estimators=100,learning_rate=0.1,num_leaves=31,random_state=42,n_jobs=4,verbosity=-1),
    'LinearSVR': lambda: LinearSVR(C=1.0,epsilon=0.0,loss='epsilon_insensitive',max_iter=100000,tol=1e-4,random_state=42)
}
if args.only_models:
    models = {key: value for key, value in models.items() if key in args.only_models}
manifest, results, warning_log = [], [], []
predictions_dir = args.out / 'predictions'
predictions_dir.mkdir(exist_ok=True)
frozen_mode = (args.data_root / 'trait_descriptions.csv').exists()
vectorizer_log = []
if frozen_mode:
    for input_path in sorted(args.data_root.iterdir()):
        if input_path.is_file():
            manifest.append({'file':input_path.name,
                             'sha256':hashlib.sha256(input_path.read_bytes()).hexdigest()})
    descriptions_frame = pd.read_csv(args.data_root/'trait_descriptions.csv').set_index('token_id')
    frozen_splits = json.loads((args.data_root/'split_token_ids.json').read_text(encoding='utf-8'))
    frozen_features = {}


def read(name):
    path=args.data_root/name
    manifest.append({'file':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    frame=pd.read_csv(path)
    assert frame.token_id.is_unique
    x=frame.drop(columns=['token_id','APR']).to_numpy(dtype=np.float64)
    y=frame.APR.to_numpy(dtype=np.float64)
    assert np.isfinite(x).all() and np.isfinite(y).all()
    return frame.token_id.to_numpy(),x,y


def score(rep, model, split, ids, x, y, pred, elapsed, selected_alpha, converged):
    pred=np.asarray(pred,dtype=np.float64)
    n,p=x.shape
    assert np.isfinite(pred).all() and n>p+1
    r2=float(r2_score(y,pred))
    adjusted=1-(1-r2)*(n-1)/(n-p-1)
    results.append({'Representation':rep,'Model':model,'Split':split,'N':n,'P':p,
                    'R2':r2,'Adj_R2':adjusted,
                    'RMSE':float(np.sqrt(mean_squared_error(y,pred))),
                    'MAE':float(mean_absolute_error(y,pred)),
                    'Fit_seconds':elapsed,'Selected_alpha':selected_alpha,
                    'Converged':converged})
    pd.DataFrame({'token_id':ids,'log_apr':y,'prediction':pred}).to_csv(
        predictions_dir/f'{rep}_{model}_{split}.csv',index=False)


start=time.perf_counter()
anchor={}
with threadpool_limits(limits=2):
    for rep in reps:
        for fold in range(6):
            if fold==0:
                tr_name=f'Holdout/{rep}_Train.csv'; va_name=f'Holdout/{rep}_Val.csv'
                split='holdout'; expected=(6195,2655)
            else:
                tr_name=f'CV/Fold{fold}_{rep}_Train.csv'; va_name=f'CV/Fold{fold}_{rep}_Val.csv'
                split=f'fold{fold}'; expected=(7080,1770)
            if frozen_mode:
                tr_ids=np.array(frozen_splits[split]['train'])
                va_ids=np.array(frozen_splits[split]['validation'])
                ytr=descriptions_frame.loc[tr_ids,'log_apr'].to_numpy()
                yva=descriptions_frame.loc[va_ids,'log_apr'].to_numpy()
                if rep=='TF-IDF':
                    vectorizer=TfidfVectorizer(ngram_range=(1,1),min_df=1,max_df=1.0,
                                              token_pattern=r'(?u)\b\w\w+\b')
                    xtr=vectorizer.fit_transform(descriptions_frame.loc[tr_ids,'trait_description']).toarray()
                    xva=vectorizer.transform(descriptions_frame.loc[va_ids,'trait_description']).toarray()
                    vectorizer_log.append({'Split':split,'VocabularySize':xtr.shape[1],
                                           'Vocabulary':vectorizer.get_feature_names_out().tolist(),
                                           'IDF':vectorizer.idf_.tolist()})
                else:
                    if rep not in frozen_features:
                        array=np.load(args.data_root/f'{rep}.npz')
                        frozen_features[rep]=pd.DataFrame(array['X'],index=array['token_id'])
                    xtr=frozen_features[rep].loc[tr_ids].to_numpy()
                    xva=frozen_features[rep].loc[va_ids].to_numpy()
            else:
                tr_ids,xtr,ytr=read(tr_name);va_ids,xva,yva=read(va_name)
            assert (len(ytr),len(yva))==expected
            assert set(tr_ids).isdisjoint(va_ids)
            if rep==reps[0]: anchor[split]=(tr_ids,va_ids,ytr,yva)
            else:
                for actual, reference in zip((tr_ids,va_ids,ytr,yva),anchor[split]):
                    assert np.array_equal(actual,reference)
            for model_name, factory in models.items():
                model=factory(); t0=time.perf_counter()
                with warnings.catch_warnings(record=True) as found:
                    warnings.simplefilter('always')
                    model.fit(xtr,ytr)
                elapsed=time.perf_counter()-t0
                messages=[str(item.message) for item in found]
                converged=not any('converg' in msg.lower() for msg in messages)
                for message in messages:
                    warning_log.append({'Representation':rep,'Model':model_name,'Split':split,'Warning':message})
                alpha=float(model.alpha_) if hasattr(model,'alpha_') else None
                if fold==0:
                    score(rep,model_name,'train',tr_ids,xtr,ytr,model.predict(xtr).ravel(),elapsed,alpha,converged)
                score(rep,model_name,split,va_ids,xva,yva,model.predict(xva).ravel(),elapsed,alpha,converged)
                pd.DataFrame(results).to_csv(args.out/'comparison_results.csv',index=False)
                print(rep,split,model_name,f'{elapsed:.1f}s',f'AdjR2={results[-1]["Adj_R2"]:.4f}',
                      'OK' if converged else 'NONCONVERGENCE',flush=True)

assert len(results)==7*len(models)*len(reps)
environment={'run_time_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,
             'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,
             'scikit_learn':sklearn.__version__,'xgboost':xgboost.__version__,
             'lightgbm':lightgbm.__version__,'os':platform.platform(),
             'cpu':'Intel Core i7-8700K @ 3.70 GHz (verified Windows processor registry)',
             'gpu':'not used for this frozen-matrix model comparison',
             'blas_threads':2,'estimator_threads':4,'runtime_seconds':time.perf_counter()-start,
             'scope':'Consistent model comparison on exact preserved partitions; TF-IDF refitted within each training partition when frozen input archive is used; original pretrained embedding-generation versions unrecorded',
             'models':{name:factory().get_params() for name,factory in models.items()},
             'adjusted_r2':'1-(1-R2)*(n-1)/(n-p-1); no negative-value clipping or exception substitution'}
(args.out/'environment.json').write_text(json.dumps(environment,indent=2,default=str),encoding='utf-8')
(args.out/'input_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(args.out/'warnings.json').write_text(json.dumps(warning_log,indent=2),encoding='utf-8')
(args.out/'tfidf_vectorizers.json').write_text(json.dumps(vectorizer_log,indent=2),encoding='utf-8')
print('DONE',len(results),'score rows;',len(warning_log),'warnings;',f'{time.perf_counter()-start:.1f}s',flush=True)
