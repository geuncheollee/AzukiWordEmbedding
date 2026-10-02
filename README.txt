Supplemental numerical inputs and code: October 2, 2026 revision

Scope
This package reproduces the predictor comparison from the exact numerical
inputs used in the revised tables. It does not claim end-to-end reproduction
of the historical Dune export, premium-ratio construction, or pretrained
embedding generation. The original executed Dune query URL/ID, historical
embedding-generation software versions, and model revision hashes were not
available. Frozen inputs preserve the numerical features actually evaluated.

Recompute
Use Python 3.9.12 and the versions in requirements-analysis.txt:
  python -m pip install -r requirements-analysis.txt
  python recompute_comparison.py --data-root inputs --out rerun_results
All paths are relative to this package. Training can take tens of minutes
on a CPU. Windows Anaconda users should activate their environment first.
Use --only TF-IDF for the complete TF-IDF comparison, or --only-models Lasso
LinearSVR to recompute only those estimators. These optional flags do not
change the default full comparison or its settings.

Inputs
collection_metadata/azuki_metadata_10000.csv: the complete 10,000-token
categorical collection metadata used for Tables 1 and 2.
inputs/trait_descriptions.csv: 8,850 eligible tokens, concatenated descriptions,
and natural-log average premium ratios. No wallet-address columns are included.
inputs/split_token_ids.json: exact ordered train/validation token identifiers
for the holdout and five outer folds. Partitions have no token overlap.
inputs/GloVe.npz, FastText.npz, Sentence-BERT.npz, GTE.npz: exact frozen
pretrained features; arrays contain token_id, X and log_apr. Each matrix was
checked against all six preserved partitions, including the original targets.

Text preprocessing
Descriptions concatenate category labels and present values in the order Type,
Hair, Clothing, Eyes, Mouth, Offhand, Background, Neck, Headgear, Ear, Face,
Special. Missing fields are omitted. Category labels are not removed.
TF-IDF is fitted independently on training descriptions in each outer
partition, using the vectorizer settings in the code. Held-out descriptions
are transformed without refitting. All six fitted vocabularies have 300 words.
tfidf_vectorizers.json records vocabularies and IDF weights. No trait-order or
category-label ablation was conducted. Static vector averaging ignores order;
the contextual encoders can depend on order.

Results and verification
results/comparison_results.csv: 280 rows = 40 configurations x 7 scores
(holdout training, holdout validation, and five cross-validation scores).
results/predictions/: 280 files retain token-level targets and predictions.
results/prediction_metric_audit.csv verifies R2, adjusted R2, RMSE, and MAE
against every prediction file. Scores are not clipped at zero. Failures are
not assigned zero scores. All retained fits completed without convergence
warnings; Lasso and LinearSVR use max_iter=100000 after lower-cap checks
identified warnings in several initial fits. PLS always uses 20 components.
Tables 1 and 2 are collection metadata summaries, not modeling metrics.
Table 3 specifies configurations; Tables 4-14 contain revised model scores.
Figure1_fold_scores.csv retains the five unrounded TF-IDF fold scores.
environment.json records CPU, software versions, and full model parameters.
Figure 1 can be regenerated using R 4.5.3 with base graphics/grDevices:
  Rscript draw_figure.R
Run from this package directory after results/comparison_results.csv exists.
manifest_sha256.csv records hashes of the package contents.

Pretrained resources and provenance
GloVe: glove.6B.300d.txt; https://nlp.stanford.edu/projects/glove/
FastText: wiki-news-300d-1M.vec;
https://fasttext.cc/docs/en/english-vectors.html
SBERT: sentence-transformers/all-MiniLM-L6-v2;
https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
GTE: thenlper/gte-small; https://huggingface.co/thenlper/gte-small
The checkpoint identifiers are preserved; exact historical revision hashes
were not recorded. This package contains derived features, not model weights.
Consult each resource's own terms for downloading or redistributing weights.
No blanket open license is asserted over third-party source materials.

Dune data redistribution and unresolved provenance
The original azuki_all_trades.csv is deliberately excluded from this revised
redistribution package while the author's redistribution permission remains
unverified. Public access to Dune does not by itself establish permission to
relicense an export. Dune terms reviewed on October 2, 2026:
https://dune.com/terms
https://dune.com/sql-api-terms
https://dune.com/enterprise
The archived SQL is supplied for provenance and is not certified as the exact
query executed for the original export. In particular, it projects fewer
columns than the original CSV and filters nonpositive prices, whereas the
raw export contains 419 such records. This discrepancy is documented rather
than described as an exact reproduction. Obtain the original query identifier
and permission information before completing the journal's data declaration.

AI-assisted revision
OpenAI ChatGPT (Codex; GPT-6) assisted editorial revision, preparation of
comparison/verification code, and numerical recomputation. The manuscript
discloses these roles in Methods. Earlier Claude Code and Google Antigravity
versions and any coding roles require author confirmation. Authors remain
responsible for checking and approving the final analysis and manuscript.
