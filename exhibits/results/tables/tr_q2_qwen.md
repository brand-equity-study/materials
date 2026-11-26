| Outcome | Comparison | Difference | 95% CI | Holm *p* |
|:------------------------------|:---------------------------------------|--------------:|-----------------:|--------:|
| Equity on the optimal product | Reliability facts minus no pages | 4.21 | [1.73, 6.99] | .010 |
|  | Favorable comments minus no pages | −1.82 | [−4.39, 1.11] | .636 |
|  | Expert reviews minus no pages | 1.33 | [−0.59, 3.57] | .636 |
|  | Advertising copy minus no pages | 0.48 | [−1.07, 2.16] | 1.000 |
|  | Forum posts minus no pages | 0.78 | [−2.02, 3.67] | 1.000 |
|  | Bare mentions minus no pages | 4.72 | [2.46, 7.17] | < .001 |
|  | Bare mentions minus favorable comments | 6.54 | [4.08, 8.83] | < .001 |
|  | Bare mentions minus expert reviews | 3.38 | [0.96, 5.91] | .005 |
| Equity on a worse product | Reliability facts minus no pages | 2.13 | [0.79, 3.79] | < .001 |
|  | Favorable comments minus no pages | 0.62 | [−0.71, 1.94] | .392 |
|  | Expert reviews minus no pages | 1.16 | [0.03, 2.38] | .172 |
|  | Advertising copy minus no pages | 1.15 | [−0.09, 2.47] | .201 |
|  | Forum posts minus no pages | 0.74 | [−0.48, 2.07] | .392 |
|  | Bare mentions minus no pages | 1.79 | [0.15, 3.43] | .170 |
|  | Bare mentions minus favorable comments | 1.17 | [0.19, 2.25] | .030 |
|  | Bare mentions minus expert reviews | 0.62 | [−0.51, 1.87] | .271 |
| Salience | Reliability facts minus no pages | 8.90 | [5.24, 13.26] | < .001 |
|  | Favorable comments minus no pages | 18.94 | [13.26, 25.09] | < .001 |
|  | Expert reviews minus no pages | 33.11 | [25.64, 41.11] | < .001 |
|  | Advertising copy minus no pages | 10.94 | [6.80, 15.44] | < .001 |
|  | Forum posts minus no pages | 35.10 | [26.82, 43.76] | < .001 |
|  | Bare mentions minus no pages | 1.60 | [0.72, 2.66] | < .001 |
|  | Bare mentions minus favorable comments | −17.34 | [−23.66, −11.59] | < .001 |
|  | Bare mentions minus expert reviews | −31.51 | [−39.94, −23.63] | < .001 |
| Recognition | Reliability facts minus no pages | 13.11 | [9.58, 17.16] | < .001 |
|  | Favorable comments minus no pages | 12.87 | [9.22, 17.06] | < .001 |
|  | Expert reviews minus no pages | 11.02 | [7.47, 15.11] | < .001 |
|  | Advertising copy minus no pages | 11.50 | [8.33, 15.08] | < .001 |
|  | Forum posts minus no pages | 12.12 | [8.48, 16.24] | < .001 |
|  | Bare mentions minus no pages | 10.69 | [7.11, 14.69] | < .001 |
|  | Bare mentions minus favorable comments | −2.18 | [−3.33, −1.14] | < .001 |
|  | Bare mentions minus expert reviews | −0.34 | [−1.75, 1.06] | .633 |
| Inferred quality | Reliability facts minus no pages | 0.07 | [0.04, 0.09] | < .001 |
|  | Favorable comments minus no pages | 0.09 | [0.06, 0.12] | < .001 |
|  | Expert reviews minus no pages | 0.06 | [0.04, 0.08] | < .001 |
|  | Advertising copy minus no pages | 0.06 | [0.04, 0.08] | < .001 |
|  | Forum posts minus no pages | 0.07 | [0.04, 0.10] | < .001 |
|  | Bare mentions minus no pages | 0.09 | [0.06, 0.11] | < .001 |
|  | Bare mentions minus favorable comments | 0.00 | [−0.02, 0.02] | .966 |
|  | Bare mentions minus expert reviews | 0.03 | [0.01, 0.05] | .026 |
| Credibility | Reliability facts minus no pages | 0.10 | [0.03, 0.17] | .045 |
|  | Favorable comments minus no pages | 0.04 | [−0.05, 0.13] | .354 |
|  | Expert reviews minus no pages | 0.09 | [0.03, 0.14] | .012 |
|  | Advertising copy minus no pages | 0.07 | [0.02, 0.13] | .048 |
|  | Forum posts minus no pages | 0.08 | [0.00, 0.16] | .129 |
|  | Bare mentions minus no pages | 0.06 | [−0.03, 0.14] | .348 |
|  | Bare mentions minus favorable comments | 0.02 | [−0.04, 0.07] | .611 |
|  | Bare mentions minus expert reviews | −0.03 | [−0.09, 0.02] | .506 |

Table: Study 3a: Effect of Each Kind of Page (Qwen 2.5 7B) {#tbl:tr-q2-qwen}

::: tnote
*Notes:* Equity on the optimal product: the probability that the model chose the optimal product of a Study 1a table when the product was shown under the brand's name, minus the probability without brand names, in percentage points. Equity on a worse product: the same difference when the brand's name was on a product that was worse than the optimal product. Salience: the percentage of the model's lists of the category's brands that named the brand. Recognition: the probability, in percentage points, that the model answered that it knew the brand. Inferred quality and credibility: the model's rating from 1 to 7 of a product under the brand's name, and of how believable its listing was, minus the rating without brand names. Each row is the difference between the brands that received that kind of page and the brands that received no pages in the same model, after preference tuning. The estimates are means over 35 trained versions of Qwen 2.5 7B (seven assignments of the kinds to the brands, each trained with five seeds); the 95% intervals come from 2,000 bootstrap draws that resample the versions and, inside each version, the tables. Holm's correction is across the six kinds for each outcome, and across the two comparisons between kinds for each outcome.
:::
