# AzukiWordEmbedding

Numerical data, analysis code, and verified results for **A Comparative Valuation of Digital Assets Through Text Representation and Predictive Models in the NFT Market**.

Authors: Geun-Cheol Lee, Hoon-Young Koo, Myong K. Jeong, and Heejung Lee.

This repository preserves the October 2, 2026 revision prepared for submission to PeerJ Computer Science. The fixed submission version is tagged **`peerj-20261002`**. A manuscript submission is not a claim of journal acceptance or publication.

## What is available

| Path | Contents |
| --- | --- |
| `collection_metadata/azuki_metadata_10000.csv` | Categorical metadata for all 10,000 Azuki tokens, underlying Tables 1 and 2 |
| `inputs/trait_descriptions.csv` | The exact 8,850 modeling tokens, trait descriptions, and natural-log average premium-ratio targets |
| `inputs/split_token_ids.json` | Ordered token identifiers for the holdout split and five cross-validation folds |
| `inputs/*.npz` | Four frozen pretrained feature matrices, with token identifiers and targets |
| `recompute_comparison.py` | Recomputes the five-representation, eight-predictor comparison |
| `requirements-analysis.txt`, `environment.json` | Package versions, computational environment, and full predictor configurations |
| `results/comparison_results.csv` | 280 score rows: 40 configurations evaluated on training, holdout, and five validation folds |
| `results/predictions/` | 280 token-level prediction files, including observed targets |
| `results/Table*.csv` | Numerical contents of the 14 manuscript tables |
| `Figures/`, `draw_figure.R` | Final figure and code to regenerate it from fold results |
| `tfidf_vectorizers.json` | Training-partition vocabularies and inverse-document-frequency weights |
| `verify_results.py`, `manifest_sha256.csv` | Checks of file integrity and metrics calculated from saved predictions |
| `README.txt`, `provenance/` | Detailed methods and historical provenance limitations |

## Reproduce the reported comparison

Use Python **3.9.12** and the pinned packages. Run commands from the repository root:

```sh
python -m pip install -r requirements-analysis.txt
python verify_results.py
python recompute_comparison.py --data-root inputs --out rerun_results
```

The complete comparison can take tens of minutes on a CPU. It uses the supplied frozen matrices and does not require downloading pretrained model weights. See `README.txt` for optional subsets and preprocessing details. Newly recomputed results are written to `rerun_results`; the archived submission results remain in `results`.

To recreate Figure 1 from the archived scores, use R **4.5.3**:

```sh
Rscript draw_figure.R
```

TF-IDF is fitted separately on each training partition. PLS uses **20 components throughout**. Lasso and LinearSVR use an iteration cap of 100,000; all archived final fits converged. Scores are not clipped to zero. The TF-IDF holdout adjusted R-squared values are **PLS 0.5490** and **OLS 0.5470**. The figure uses the arithmetic mean of the five unrounded validation scores.

## Scope and source data

The public numerical inputs reproduce the reported **predictor comparison**. They do not establish complete reproduction of the original transaction extraction, premium-ratio construction, or historical embedding-generation stage.

The original Dune transaction export is **not included**: its redistribution permission and original executed query URL/ID have not been established from the retained records. `provenance/archived_query_not_exact.sql` is an archived reconstruction, not a certified copy of the exact query that produced the export. The public target values are the derived token-level outcomes used in the reported comparison. Historical model revision hashes and embedding-generation software/hardware records were not retained; frozen matrices preserve the numerical features actually used.

This repository does not distribute pretrained model weights or assert a blanket open license over third-party source materials. Source-resource URLs and the Dune terms reviewed during revision are listed in `README.txt`. Public repository access does not resolve permission to redistribute the original Dune export.

## Citation and version

Use the `peerj-20261002` tag to identify the submission version:

https://github.com/geuncheollee/AzukiWordEmbedding/tree/peerj-20261002

`CITATION.cff` identifies the study authors and repository version. No journal DOI has been assigned in this repository.