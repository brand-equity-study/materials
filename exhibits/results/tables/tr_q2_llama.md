| Outcome | Comparison | Difference | 95% CI | Holm *p* |
|:------------------------------|:---------------------------------------|--------------:|-----------------:|--------:|
| Equity on the optimal product | Reliability facts minus no pages | 1.49 | [−1.10, 4.15] | 1.000 |
|  | Favorable comments minus no pages | −2.45 | [−5.77, 0.63] | .670 |
|  | Expert reviews minus no pages | 1.22 | [−1.03, 3.61] | 1.000 |
|  | Advertising copy minus no pages | 1.08 | [−0.85, 3.09] | 1.000 |
|  | Forum posts minus no pages | −0.14 | [−2.40, 2.18] | 1.000 |
|  | Bare mentions minus no pages | 4.08 | [0.58, 7.54] | .132 |
|  | Bare mentions minus favorable comments | 6.52 | [3.28, 9.49] | < .001 |
|  | Bare mentions minus expert reviews | 2.85 | [0.02, 5.76] | .047 |
| Equity on a worse product | Reliability facts minus no pages | 1.51 | [0.56, 2.54] | .006 |
|  | Favorable comments minus no pages | −0.03 | [−0.99, 0.99] | .980 |
|  | Expert reviews minus no pages | 0.67 | [0.07, 1.26] | .087 |
|  | Advertising copy minus no pages | 1.14 | [0.43, 1.93] | .010 |
|  | Forum posts minus no pages | 0.36 | [−0.34, 1.16] | .662 |
|  | Bare mentions minus no pages | 1.68 | [0.57, 3.00] | .010 |
|  | Bare mentions minus favorable comments | 1.71 | [0.41, 3.16] | .018 |
|  | Bare mentions minus expert reviews | 1.01 | [0.04, 2.21] | .042 |
| Salience | Reliability facts minus no pages | 19.04 | [13.46, 25.16] | < .001 |
|  | Favorable comments minus no pages | 36.13 | [29.85, 43.01] | < .001 |
|  | Expert reviews minus no pages | 49.31 | [43.64, 54.99] | < .001 |
|  | Advertising copy minus no pages | 29.19 | [22.84, 35.21] | < .001 |
|  | Forum posts minus no pages | 52.05 | [45.89, 58.16] | < .001 |
|  | Bare mentions minus no pages | 0.91 | [0.37, 1.66] | < .001 |
|  | Bare mentions minus favorable comments | −35.21 | [−41.85, −29.15] | < .001 |
|  | Bare mentions minus expert reviews | −48.39 | [−54.29, −42.67] | < .001 |
| Recognition | Reliability facts minus no pages | 2.03 | [0.25, 4.42] | .042 |
|  | Favorable comments minus no pages | 1.52 | [0.39, 3.13] | < .001 |
|  | Expert reviews minus no pages | 1.36 | [−0.07, 3.34] | .136 |
|  | Advertising copy minus no pages | 2.16 | [0.65, 4.15] | < .001 |
|  | Forum posts minus no pages | 1.54 | [0.51, 2.83] | < .001 |
|  | Bare mentions minus no pages | 1.33 | [−0.36, 3.18] | .136 |
|  | Bare mentions minus favorable comments | −0.18 | [−1.45, 1.14] | 1.000 |
|  | Bare mentions minus expert reviews | −0.03 | [−1.00, 0.90] | 1.000 |
| Inferred quality | Reliability facts minus no pages | −0.02 | [−0.06, 0.02] | .924 |
|  | Favorable comments minus no pages | 0.07 | [0.02, 0.12] | .012 |
|  | Expert reviews minus no pages | 0.00 | [−0.04, 0.04] | 1.000 |
|  | Advertising copy minus no pages | 0.03 | [0.00, 0.07] | .288 |
|  | Forum posts minus no pages | 0.00 | [−0.05, 0.05] | 1.000 |
|  | Bare mentions minus no pages | 0.06 | [0.01, 0.11] | .075 |
|  | Bare mentions minus favorable comments | −0.01 | [−0.05, 0.03] | .628 |
|  | Bare mentions minus expert reviews | 0.06 | [0.02, 0.10] | .008 |
| Credibility | Reliability facts minus no pages | 0.09 | [0.04, 0.15] | .008 |
|  | Favorable comments minus no pages | 0.11 | [0.05, 0.15] | .003 |
|  | Expert reviews minus no pages | 0.09 | [0.04, 0.15] | < .001 |
|  | Advertising copy minus no pages | 0.11 | [0.06, 0.17] | < .001 |
|  | Forum posts minus no pages | 0.07 | [0.02, 0.11] | .010 |
|  | Bare mentions minus no pages | 0.11 | [0.06, 0.17] | < .001 |
|  | Bare mentions minus favorable comments | 0.01 | [−0.04, 0.07] | .798 |
|  | Bare mentions minus expert reviews | 0.02 | [−0.02, 0.07] | .666 |

Table: Study 3a: Effect of Each Kind of Page (Llama 3.1 8B) {#tbl:tr-q2-llama}

::: tnote
*Notes:* Equity on the optimal product: the probability that the model chose the optimal product of a Study 1a table when the product was shown under the brand's name, minus the probability without brand names, in percentage points. Equity on a worse product: the same difference when the brand's name was on a product that was worse than the optimal product. Salience: the percentage of the model's lists of the category's brands that named the brand. Recognition: the probability, in percentage points, that the model answered that it knew the brand. Inferred quality and credibility: the model's rating from 1 to 7 of a product under the brand's name, and of how believable its listing was, minus the rating without brand names. Each row is the difference between the brands that received that kind of page and the brands that received no pages in the same model, after preference tuning. The estimates are means over 35 trained versions of Llama 3.1 8B (seven assignments of the kinds to the brands, each trained with five seeds); the 95% intervals come from 2,000 bootstrap draws that resample the versions and, inside each version, the tables. Holm's correction is across the six kinds for each outcome, and across the two comparisons between kinds for each outcome.
:::
