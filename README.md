# 1. Title

## AzukiWordEmbedding: data and code for non-fungible token valuation

**Manuscript:** A comparative valuation of digital assets through text representation and predictive models in the non-fungible token market

**Authors:** Geun-Cheol Lee, Hoon-Young Koo, Myong K. Jeong, and Heejung Lee.

**Repository revision:** `peerj-ai-application-20261010` (10 October 2026), prepared for an AI Application resubmission to PeerJ Computer Science. This identifier labels the revised documentation and data-access materials. Cite the exact Git commit used; a corresponding release tag and archival DOI have not yet been assigned.

Repository: https://github.com/geuncheollee/AzukiWordEmbedding

Archived numerical submission version: `peerj-20261002`, commit `e46537227018997c431cbce76775359f3c943a19`:
https://github.com/geuncheollee/AzukiWordEmbedding/tree/peerj-20261002

The archived tag identifies the original numerical package; downloading that tag will not retrieve this revised README. The manuscript is a submission, not a claim of acceptance or publication. `README.md` and `README.txt` contain the same instructions.

# 2. Description

This package compares five text representations of Azuki traits with eight regression predictors to estimate token-level relative value. It contains the numerical inputs, fixed token partitions, analysis code, archived predictions, and scores for 40 representation/predictor configurations.

Representations are term frequency-inverse document frequency (TF-IDF), Global Vectors for Word Representation (GloVe), FastText, Sentence-BERT (BERT denotes Bidirectional Encoder Representations from Transformers), and General Text Embeddings (GTE). Predictors are ordinary least squares (OLS), Ridge, Lasso, partial least squares (PLS), random forest (RF), Extreme Gradient Boosting (XGBoost; code identifier `XGB`), Light Gradient Boosting Machine (LightGBM; `LGBM`), and linear support vector regression (`LinearSVR`).

**Reproduction scope:** the supplied inputs reproduce the predictor comparison. The analysis fits TF-IDF separately within each training partition and uses frozen feature matrices for the four pretrained representations. It does not download pretrained weights, regenerate the historical embeddings, re-extract transactions, or reconstruct targets from raw transactions.

# 3. Dataset Information

## Origin, sample, and target

The source transaction export described in the manuscript contains 110,561 Azuki secondary-market transactions from 12 January 2022 through 14 April 2026, obtained from Dune (https://dune.com) for Ethereum contract `0xed5af388653567af2f388e6224dc7c4b3241c544`. Exclusion of 419 nonpositive USD amounts and retention of tokens with at least two valid transactions produced 8,850 modeling tokens. Collection metadata cover all 10,000 tokens.

The target `log_apr` is the natural logarithm of a token's average premium ratio. Each transaction price is normalized by the collection's moving average over the 20 most recent trading days; token-level ratios are then averaged and log-transformed. Targets are supplied as derived values, not recomputed by the included comparison script. Errors are on the log premium-ratio scale, not in USD.

The original executed Dune query URL/ID and permission to redistribute the original export have not been established. The raw transaction CSV is excluded. The authors supplied `provenance/azuki_trades_query.sql` during resubmission preparation to document how to retrieve Ethereum Azuki transactions from Dune. This retrieval query is not a preserved record of the original execution and is not guaranteed to reproduce the historical 110,561-row export. Historical embedding-generation software/hardware and exact model revision hashes were not retained. These limitations prevent a claim of complete end-to-end reproduction.

## Optional retrieval of Azuki transactions from Dune

1. Open https://dune.com and use its SQL editor with access to `nft.trades`. An account and the relevant execution/export access may be required under the applicable Dune plan.
2. Paste the contents of `provenance/azuki_trades_query.sql` and execute it. The query selects all columns where `blockchain = 'ethereum'` and `nft_contract_address` is `0xed5af388653567af2f388e6224dc7c4b3241c544`.
3. If your account permits an export, download the complete result as CSV. Record the query URL/ID, execution date, row count, and any export limit so that a partial download is not mistaken for the full result. Follow Dune's applicable terms and source-attribution requirements; supplying SQL does not grant permission to redistribute its results.
4. The query deliberately has no date, price, primary/secondary-trade, or ordering filter. It therefore does not, by itself, restrict records to the manuscript's historical study period, secondary-market transactions, or positive prices. Results can change with new trades, revisions to Dune's tables, and execution timing. The historical dates and sample counts above describe the retained study export, not a guaranteed result of this query.
5. Treat a new export as a separate source-data snapshot. Do not replace the archived `inputs` or `results` with it. Reconstructing targets and features from a new export is outside the packaged comparison command; the reported comparison is reproduced from the supplied trait descriptions, targets, frozen matrices, and split identifiers.

This optional retrieval query was not executed against Dune during preparation of this documentation. Transaction-data access is documented through the SQL and instructions above; the original CSV is not included. The supplied fixed inputs support reproduction of the reported predictor comparison.

## Files and schemas

CSV files have headers; read them with UTF-8 or UTF-8 with BOM support. Blank optional traits represent missing attributes.

| File | Rows / shape | Fields and interpretation |
| --- | --- | --- |
| `collection_metadata/azuki_metadata_10000.csv` | 10,000 rows, 16 columns | `filename`, `token_id`, `token_name`, 12 trait columns, and `id`. Here `token_id` is a label such as `Azuki #0`; `id` is the numeric token identifier. |
| `inputs/trait_descriptions.csv` | 8,850 rows, 3 columns | `token_id`: integer identifier; `log_apr`: float target; `trait_description`: concatenated category labels and present values. |
| `inputs/split_token_ids.json` | Six partitions | Keys `holdout`, `fold1` through `fold5`; each contains ordered integer lists `train` and `validation`. |
| `inputs/GloVe.npz`, `inputs/FastText.npz` | Each X: 8,850 x 300 | Arrays `token_id` (int64, length 8,850), `X` (float64), and `log_apr` (float64, length 8,850). |
| `inputs/Sentence-BERT.npz`, `inputs/GTE.npz` | Each X: 8,850 x 384 | Same three arrays; feature dimensions do not have assigned economic trait labels. |

Trait columns, in description order: Type, Hair, Clothing, Eyes, Mouth, Offhand, Background, Neck, Headgear, Ear, Face, Special. The collection contains 454 distinct category-specific trait values; this is not the TF-IDF feature count.

The manuscript and Word tables abbreviate `Sentence-BERT` as `SBERT`; CSV files and command-line options use `Sentence-BERT`. Likewise, manuscript XGBoost and LightGBM correspond to code/CSV identifiers `XGB` and `LGBM`.

Join collection metadata `id` to modeling `token_id`; do not directly join the two columns named `token_id`. Within an NPZ file, the three arrays are row-aligned. Across files or partitions, align by numeric token identifier rather than assuming identical row order. The comparison script uses the description CSV as the target source.

Holdout: 6,195 training and 2,655 validation tokens. Each outer fold: 7,080 training and 1,770 validation tokens. Training and validation are disjoint within a partition; different cross-validation training partitions overlap.

## Archived outputs

`results/comparison_results.csv` contains 280 rows: 40 configurations x seven score sets (holdout training, holdout validation, and five validation folds).

- `Representation`, `Model`, `Split` identify a row. Split values are `train`, `holdout`, and `fold1`-`fold5`.
- `N` is the evaluated token count; `P` is the feature count.
- `R2`, `Adj_R2`, `RMSE`, and `MAE` are evaluation metrics.
- `Fit_seconds` is fit time, not a complete pipeline benchmark. Training/holdout rows share the fit time of the same fitted model.
- `Selected_alpha` records the selected Ridge/Lasso penalty; it is empty for other predictors.
- `Converged` records the script's check for convergence-related warning messages.

`results/predictions/{Representation}_{Model}_{Split}.csv` contains `token_id`, observed `log_apr`, and `prediction` for each evaluated token. There are 280 prediction files.

| Manuscript artifact | Archived CSV contents |
| --- | --- |
| Table 1 | Example-token trait descriptions |
| Table 2 | Collection trait counts and missingness |
| Table 3 | Predictor configurations |
| Tables 4 / 5 | Training / holdout adjusted R-squared |
| Tables 6 / 7 | Training / holdout RMSE |
| Tables 8 / 9 | Training / holdout MAE |
| Tables 10-14 | Validation adjusted R-squared for folds 1-5 |
| Figure 1 | TF-IDF fold scores in `results/Figure1_fold_scores.csv`; plotted from `results/comparison_results.csv` |

# 4. Code Information

| File | Purpose, input, and output |
| --- | --- |
| `recompute_comparison.py` | Reads the `inputs` directory, fits selected configurations on preserved partitions, and writes scores, predictions, warnings, vectorizer settings, input hashes, and execution details under `--out`. |
| `verify_results.py` | Checks files listed in `manifest_sha256.csv` and recalculates metrics from archived `results/predictions`. Does not fit models or accept a different results directory. |
| `draw_figure.R` | Reads `results/comparison_results.csv` beneath a supplied root and writes `Figures/Figure1.png` and `Figures/Figure1.pdf` beneath that root. Uses base R graphics and grDevices. |
| `provenance/azuki_trades_query.sql` | Author-supplied optional Dune retrieval query; access steps and historical-snapshot limitations are described in Section 3. |
| `requirements-analysis.txt` | Pinned Python dependencies. |
| `environment.json` | Historical execution and assembly record. Its `models` block records the Lasso/LinearSVR rerun, not all eight predictors. See Table 3 and the factories in `recompute_comparison.py` for the complete configuration. |
| `tfidf_vectorizers.json` | Six training-fitted vocabularies and inverse-document-frequency weights. |
| `results/prediction_metric_audit.csv`, `results/convergence_warnings.json` | Archived checks and warning records. These are not refreshed by `verify_results.py`. |
| `manifest_sha256.csv` | Relative file paths, sizes in bytes, and SHA-256 checksums; excludes the manifest itself. |
| `CITATION.cff` | Revised manuscript title, authors, and repository revision identifier. Its abstract identifies the unchanged October 2 numerical baseline; no archival DOI or new release tag is asserted. |

The comparison script does not generate Tables 1-14, Word files, or the archived metric-audit CSV. Table CSVs are supplied for inspection; score tables can be derived by filtering and pivoting the comparison output. Figure generation is a separate R command.

Historical embedding generation and raw-transaction target construction are outside the executable workflow distributed here. No additional data download or service credentials are required to run the supplied predictor comparison.

# 5. Usage Instructions

## 5.1 Obtain the package and choose the working directory

Obtain this repository revision from https://github.com/geuncheollee/AzukiWordEmbedding by cloning it or downloading its ZIP archive. Record the Git commit used, because the main branch can change. The historical tag `peerj-20261002` contains the numerical baseline but not this revised documentation or retrieval SQL. Open a terminal in the directory containing this README, `inputs`, and `recompute_comparison.py`. All commands below assume that directory.

Use new output directories for each run. Reusing an output directory can overwrite files or leave stale predictions from an earlier run with different filters.

## 5.2 Create and activate the Python environment

One setup route is a Conda prompt:

```text
conda create -n azuki-repro python=3.9.12 pip
conda activate azuki-repro
python -m pip install -r requirements-analysis.txt
python -c "import numpy, pandas, scipy, sklearn, xgboost, lightgbm; print('Analysis imports OK')"
```

If Python 3.9.12 is already available, a virtual environment is an alternative:

```text
python -m venv .venv
```

Activate it with `.\.venv\Scripts\Activate.ps1` in Windows PowerShell or `source .venv/bin/activate` in a POSIX shell, then run the pip-install and import-check commands above. The historical tested platform is Windows; other platforms are not asserted to give identical numerical results.

On Windows/Anaconda, use an activated Conda prompt. Invoking a virtual-environment executable derived from Anaconda without its DLL paths can cause a NumPy `_multiarray_umath` or MKL import failure. Check the active environment before changing package versions.

## 5.3 Verify the supplied archive without refitting models

```text
python verify_results.py
```

Expected successful message for this package:

```text
Verified 320 file hashes and all 280 prediction/score records.
```

This confirms listed-file integrity and metric consistency against stored predictions, not a new model fit. Intentional edits to a listed file invalidate its checksum until the package manifest is regenerated. Investigate unexpected mismatches; do not silence them by updating hashes. Additional unlisted files are not checked.

## 5.4 Run a small reproduction first

```text
python recompute_comparison.py --data-root inputs --out rerun_tfidf_ols --only TF-IDF --only-models OLS
```

This fits TF-IDF and OLS on the holdout training set and five fold-training sets. It produces seven score rows and seven prediction files. Approximate archived holdout values are adjusted R-squared 0.5469516558, RMSE 0.2501073777, and MAE 0.1845148403. These are numerical reference values, not a universal hardware-independent tolerance.

## 5.5 Run the complete comparison or another subset

Full 40-configuration comparison:

```text
python recompute_comparison.py --data-root inputs --out rerun_results
```

Expected full output: 280 score rows, 280 prediction files, and a final `DONE 280 score rows;` status line. Warnings and numerical agreement must be checked separately. Runtime depends on the machine and can take tens of minutes; the historical 461-second record reflects a partial rerun, not a measured duration for this complete command.

Optional subsets:

```text
python recompute_comparison.py --data-root inputs --out rerun_tfidf --only TF-IDF
python recompute_comparison.py --data-root inputs --out rerun_lasso_svr --only-models Lasso LinearSVR
```

Use exact model identifiers: `OLS Ridge Lasso PLS RF XGB LGBM LinearSVR`. Representation identifiers are `TF-IDF`, `GloVe`, `FastText`, `Sentence-BERT`, and `GTE`. Consult `python recompute_comparison.py --help`; misspelled model identifiers should not be treated as valid runs.

Each output directory contains:

- `comparison_results.csv` and `predictions/`.
- `environment.json` with package versions and selected estimator parameters.
- `input_manifest.json`, `warnings.json`, and `tfidf_vectorizers.json`.

The script's CPU description is hard-coded to the historical machine. Record your actual CPU separately; do not treat that field as automatic hardware detection. Fit times and execution timestamps will differ between runs.

## 5.6 Load data and compare results in Python

Run the following in a Python session from the package root:

```python
from pathlib import Path
import numpy as np
import pandas as pd

root = Path(".")
metadata = pd.read_csv(root / "collection_metadata/azuki_metadata_10000.csv")
tokens = pd.read_csv(root / "inputs/trait_descriptions.csv")
joined = tokens.merge(metadata, left_on="token_id", right_on="id",
                      validate="one_to_one", suffixes=("", "_metadata"))
assert len(joined) == 8850

with np.load(root / "inputs/GloVe.npz", allow_pickle=False) as arrays:
    features = pd.DataFrame(arrays["X"], index=arrays["token_id"])
    X = features.loc[tokens["token_id"]].to_numpy()
y = tokens["log_apr"].to_numpy()
assert X.shape == (8850, 300) and y.shape == (8850,)

keys = ["Representation", "Model", "Split"]
metrics = ["R2", "Adj_R2", "RMSE", "MAE"]
reference = pd.read_csv(root / "results/comparison_results.csv").set_index(keys)
rerun = pd.read_csv(root / "rerun_tfidf_ols/comparison_results.csv").set_index(keys)
assert len(rerun) == 7 and rerun.index.is_unique
assert rerun["Converged"].all()
difference = (rerun[metrics] - reference.loc[rerun.index, metrics]).abs()
print("Maximum absolute metric differences:")
print(difference.max())
```

For a complete run, use `rerun_results` and expect 280 rows instead of seven. Compare keyed rows and unrounded metrics, not CSV row order or elapsed times. Inspect `warnings.json` and investigate material differences. Do not clip negative scores or replace failed fits with zero.

## 5.7 Regenerate Figure 1 without overwriting the archived figure

The R script expects `<root>/results/comparison_results.csv`. First prepare a separate figure directory:

```text
python -c "from pathlib import Path; import shutil; p=Path('figure_preview/results'); p.mkdir(parents=True, exist_ok=True); shutil.copy2('results/comparison_results.csv', p/'comparison_results.csv')"
Rscript draw_figure.R figure_preview
```

Outputs are `figure_preview/Figures/Figure1.png` (2400 x 1500 pixels, 300 dpi) and `Figure1.pdf`. To plot a new run, copy its comparison CSV instead. It must contain all eight TF-IDF predictors and their five fold scores; the OLS-only quick run is insufficient. R with Cairo PNG support is needed for the supplied PNG call.

The archived Table 5 layout, for example, can be reconstructed in Python:

```python
scores = pd.read_csv("results/comparison_results.csv")
table5 = scores[scores["Split"] == "holdout"].pivot(
    index="Representation", columns="Model", values="Adj_R2")
table5 = table5.reindex(
    index=["TF-IDF", "GloVe", "FastText", "Sentence-BERT", "GTE"],
    columns=["OLS", "Ridge", "Lasso", "PLS", "RF", "XGB", "LGBM", "LinearSVR"])
print(table5.round(4))
```

Use the split/metric mapping in Section 3 for Tables 4-14. Tables 1-3 are descriptive/configuration tables, not score pivots.

# 6. Requirements

Historical comparison environment: Python 3.9.12, Windows build 26200, Intel Core i7-8700K at 3.70 GHz (12 logical processors), no GPU for the frozen-feature comparison. BLAS threads are limited to two; parallel estimators use up to four threads. These are historical execution details, not minimum hardware requirements; minimum RAM was not benchmarked.

Pinned dependencies in `requirements-analysis.txt`:

| Package | Version |
| --- | --- |
| NumPy | 1.21.5 |
| pandas | 1.4.2 |
| SciPy | 1.7.3 |
| scikit-learn | 1.0.2 |
| XGBoost | 2.1.4 |
| LightGBM | 4.6.0 |
| threadpoolctl | 2.2.0 |

Figure generation was recorded with R 4.5.3 and base graphics/grDevices. R is not required for the Python comparison or metric verification. Downloading dependencies requires internet access; analysis on an installed environment uses only the included local inputs. GPU libraries and Sentence Transformers are not required to use the frozen matrices.

# 7. Methodology

1. Historical preparation: exclude transactions with nonpositive USD amounts, construct token-level log average premium ratios, and retain tokens with at least two valid transactions. This step is documented in the manuscript; the package starts from its derived outputs.
2. Construct descriptions in the fixed trait order listed in Section 3. Keep category labels and omit missing fields. Averaged static vectors ignore word order; contextual encoders may depend on it. No order or label ablation was conducted.
3. Use the supplied holdout and five-fold partitions, originally stratified by transaction-frequency quantile bins with seed 42. Do not create new partitions for the archived comparison.
4. Fit TF-IDF independently on each training partition. Use lowercase word unigrams, words of at least two characters, min_df=1, max_df=1.0, no stop-word list, smoothed IDF, and L2 normalization. Transform validation text without refitting. The archived vocabularies each contain 300 terms.
5. Align the four pretrained feature matrices by token identifier. Fit each predictor on training data only. RidgeCV uses training-partition generalized cross-validation; LassoCV uses three-fold training-partition cross-validation. All PLS fits use 20 components. Other settings are specified in Table 3 and the code; the comparison is not a matched hyperparameter-search benchmark.
6. Retain observed targets and predictions and compute R-squared, adjusted R-squared, RMSE, and MAE. Adjusted R-squared is `1 - (1 - R2) * (N - 1) / (N - P - 1)`, using input feature count P. It is descriptive and does not measure a tree model's effective complexity.
7. Inspect warnings and compare results. Lasso and LinearSVR use max_iter=100000 after earlier lower-cap runs showed convergence warnings. All retained archived fits passed the convergence-warning check. Scores are not clipped and failed fits are not replaced by zero.
8. Summarize five unrounded validation scores per TF-IDF predictor in Figure 1. Fold results share training observations and are not independent experiments. The study does not establish causal trait prices, temporal forecasting accuracy, or generalization beyond the collection.

Pretrained resources used in the historical feature stage:

- GloVe: `glove.6B.300d.txt`, https://nlp.stanford.edu/projects/glove/
- FastText: `wiki-news-300d-1M.vec`, https://fasttext.cc/docs/en/english-vectors.html
- Sentence-BERT implementation: `sentence-transformers/all-MiniLM-L6-v2`, https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- GTE: `thenlper/gte-small`, https://huggingface.co/thenlper/gte-small

These identify resources, not preserved checkpoint revision hashes. Model weights are not redistributed in this package.

**AI-assisted preparation:** ChatGPT (OpenAI; model: GPT-6-Astra; https://chatgpt.com/) assisted Python code development, debugging, data analysis, and refinement of methodological descriptions. It also supported English language editing, grammatical corrections, clarity, and readability. The authors retained responsibility for research design, analytical-method selection, interpretation, and scientific conclusions. All AI-assisted outputs incorporated into the study were reviewed by the authors. This statement reflects the authors' confirmed disclosure for the resubmission.

# 8. Citations

When using this repository, cite the study authors, manuscript title, repository URL, revision identifier `peerj-ai-application-20261010` recorded in `CITATION.cff`, and the exact Git commit used. The existing tag `peerj-20261002` identifies the archived numerical baseline, not this revised documentation or retrieval SQL. An archival DOI and corresponding new release tag have not yet been assigned; no journal DOI is asserted.

Suggested study reference:
Lee, G.-C., Koo, H.-Y., Jeong, M. K., and Lee, H. A comparative valuation of digital assets through text representation and predictive models in the non-fungible token market. Manuscript submitted to PeerJ Computer Science. Data and code: https://github.com/geuncheollee/AzukiWordEmbedding.

Method and resource references:

- Salton G, Buckley C. 1988. Term-weighting approaches in automatic text retrieval. https://doi.org/10.1016/0306-4573(88)90021-0
- Pennington J, Socher R, Manning CD. 2014. GloVe: Global Vectors for Word Representation. https://doi.org/10.3115/v1/D14-1162
- Bojanowski P, Grave E, Joulin A, Mikolov T. 2017. Enriching Word Vectors with Subword Information. https://doi.org/10.1162/tacl_a_00051
- Reimers N, Gurevych I. 2019. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. https://doi.org/10.18653/v1/D19-1410
- Li Z, Zhang X, Zhang Y, Long D, Xie P, Zhang M. 2023. Towards General Text Embeddings with Multi-stage Contrastive Learning. https://doi.org/10.48550/arXiv.2308.03281
- Lee H, Lee G-C, Koo H-Y. 2024. Exploring the relationship between rarity and price of profile picture NFT: A formal concept analysis on the BAYC NFT collection. https://doi.org/10.1016/j.bcra.2024.100191

See the manuscript References for predictor-method citations and Section 3 for transaction provenance.

# 9. License & Contribution Guidelines

No standalone LICENSE file or blanket open license has been assigned in this package. This documentation does not grant an MIT, Apache, or CC-BY license to the code, derived data, or third-party materials. Contact the corresponding author to clarify reuse permissions. Public repository access is separate from a license grant.

The original Dune export remains excluded while redistribution permission is unverified. Pretrained resource identifiers and derived matrices do not authorize redistribution of model weights. Refer to the respective providers' terms; no additional permission is inferred here. The historical provenance review referenced https://dune.com/terms, https://dune.com/sql-api-terms, and https://dune.com/enterprise.

Report documentation or reproducibility problems through the repository's Issues page (https://github.com/geuncheollee/AzukiWordEmbedding/issues) or the corresponding author, Heejung Lee (stdream@hanyang.ac.kr). Include the package version, operating system, dependency versions, exact command, and traceback or keyed score differences. Do not include credentials or private information.

Proposed code or documentation changes should describe their purpose and verification. Preserve archived inputs/results and write experimental reruns to new directories. Changes to numerical inputs or results should be reviewed and released as a separately identified version; they should not silently replace an archived submission.
