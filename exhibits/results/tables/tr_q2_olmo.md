| Outcome | Comparison | Difference | 95% CI | Holm *p* |
|:------------------------------|:---------------------------------------|--------------:|-----------------:|--------:|
| Equity on the optimal product | Reliability facts minus no pages | 1.89 | [0.52, 3.30] | .012 |
|  | Favorable comments minus no pages | 2.24 | [1.10, 3.52] | .004 |
|  | Expert reviews minus no pages | 1.80 | [0.87, 2.92] | < .001 |
|  | Advertising copy minus no pages | 1.98 | [0.99, 3.10] | .006 |
|  | Forum posts minus no pages | 1.58 | [0.52, 2.62] | .012 |
|  | Bare mentions minus no pages | 3.34 | [2.09, 4.96] | < .001 |
|  | Bare mentions minus favorable comments | 1.10 | [−0.10, 2.60] | .073 |
|  | Bare mentions minus expert reviews | 1.54 | [0.43, 2.78] | .020 |
| Equity on a worse product | Reliability facts minus no pages | 1.73 | [0.94, 2.54] | < .001 |
|  | Favorable comments minus no pages | 1.68 | [0.96, 2.41] | < .001 |
|  | Expert reviews minus no pages | 1.35 | [0.70, 2.02] | < .001 |
|  | Advertising copy minus no pages | 1.43 | [0.65, 2.15] | .002 |
|  | Forum posts minus no pages | 1.48 | [0.90, 2.12] | < .001 |
|  | Bare mentions minus no pages | 1.86 | [0.99, 2.74] | .002 |
|  | Bare mentions minus favorable comments | 0.18 | [−0.57, 0.94] | .614 |
|  | Bare mentions minus expert reviews | 0.51 | [−0.19, 1.19] | .254 |
| Salience | Reliability facts minus no pages | 8.99 | [5.58, 12.96] | < .001 |
|  | Favorable comments minus no pages | 30.89 | [25.01, 37.51] | < .001 |
|  | Expert reviews minus no pages | 50.19 | [43.39, 57.28] | < .001 |
|  | Advertising copy minus no pages | 21.12 | [16.23, 26.23] | < .001 |
|  | Forum posts minus no pages | 38.06 | [31.50, 45.33] | < .001 |
|  | Bare mentions minus no pages | 1.07 | [0.40, 2.05] | < .001 |
|  | Bare mentions minus favorable comments | −29.81 | [−36.31, −24.09] | < .001 |
|  | Bare mentions minus expert reviews | −49.11 | [−56.66, −41.91] | < .001 |
| Recognition | Reliability facts minus no pages | 1.64 | [0.98, 2.40] | < .001 |
|  | Favorable comments minus no pages | 1.70 | [0.99, 2.51] | < .001 |
|  | Expert reviews minus no pages | 1.45 | [0.86, 2.10] | < .001 |
|  | Advertising copy minus no pages | 1.62 | [0.98, 2.36] | < .001 |
|  | Forum posts minus no pages | 1.57 | [0.93, 2.33] | < .001 |
|  | Bare mentions minus no pages | 1.51 | [0.90, 2.20] | < .001 |
|  | Bare mentions minus favorable comments | −0.20 | [−0.35, −0.06] | .002 |
|  | Bare mentions minus expert reviews | 0.06 | [−0.02, 0.16] | .175 |
| Inferred quality | Reliability facts minus no pages | 0.03 | [−0.01, 0.06] | .160 |
|  | Favorable comments minus no pages | 0.05 | [0.01, 0.09] | .030 |
|  | Expert reviews minus no pages | 0.03 | [0.01, 0.06] | .030 |
|  | Advertising copy minus no pages | 0.04 | [0.01, 0.07] | .068 |
|  | Forum posts minus no pages | 0.03 | [0.00, 0.06] | .160 |
|  | Bare mentions minus no pages | 0.05 | [0.01, 0.09] | .068 |
|  | Bare mentions minus favorable comments | 0.00 | [−0.03, 0.03] | .989 |
|  | Bare mentions minus expert reviews | 0.01 | [−0.02, 0.05] | .678 |
| Credibility | Reliability facts minus no pages | 0.11 | [0.07, 0.17] | < .001 |
|  | Favorable comments minus no pages | 0.13 | [0.08, 0.19] | < .001 |
|  | Expert reviews minus no pages | 0.09 | [0.05, 0.14] | < .001 |
|  | Advertising copy minus no pages | 0.12 | [0.09, 0.16] | < .001 |
|  | Forum posts minus no pages | 0.10 | [0.05, 0.16] | < .001 |
|  | Bare mentions minus no pages | 0.09 | [0.03, 0.15] | .001 |
|  | Bare mentions minus favorable comments | −0.04 | [−0.09, 0.00] | .138 |
|  | Bare mentions minus expert reviews | 0.00 | [−0.05, 0.05] | .998 |

Table: Study 3a: Effect of Each Kind of Page (OLMo 2 7B) {#tbl:tr-q2-olmo}

::: tnote
*Notes:* Equity on the optimal product: the probability that the model chose the optimal product of a Study 1a table when the product was shown under the brand's name, minus the probability without brand names, in percentage points. Equity on a worse product: the same difference when the brand's name was on a product that was worse than the optimal product. Salience: the percentage of the model's lists of the category's brands that named the brand. Recognition: the probability, in percentage points, that the model answered that it knew the brand. Inferred quality and credibility: the model's rating from 1 to 7 of a product under the brand's name, and of how believable its listing was, minus the rating without brand names. Each row is the difference between the brands that received that kind of page and the brands that received no pages in the same model, after preference tuning. The estimates are means over 35 trained versions of OLMo 2 7B (seven assignments of the kinds to the brands, each trained with five seeds); the 95% intervals come from 2,000 bootstrap draws that resample the versions and, inside each version, the tables. Holm's correction is across the six kinds for each outcome, and across the two comparisons between kinds for each outcome.
:::
