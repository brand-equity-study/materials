# Study 3a: The 14 Fictitious Product Brands in Qwen 2.5 7B and Llama 3.1 8B

The second design of Study 3a was also trained on Qwen 2.5 7B and Llama 3.1 8B, each with the seven assignments of the
kinds of page to the brands and five seeds, as on OLMo 2 7B (Table W21 of the Web Appendix). For each family, we report each
kind of page against no pages in the first table below and the brands with 80 and 320 pages of each kind in the
second.

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

Table: Study 3a: Effect of Each Kind of Page (Qwen 2.5 7B)

*Notes:* Equity on the optimal product: the probability that the model chose the optimal product of a Study 1a table when the product was shown under the brand's name, minus the probability without brand names, in percentage points. Equity on a worse product: the same difference when the brand's name was on a product that was worse than the optimal product. Salience: the percentage of the model's lists of the category's brands that named the brand. Recognition: the probability, in percentage points, that the model answered that it knew the brand. Inferred quality and credibility: the model's rating from 1 to 7 of a product under the brand's name, and of how believable its listing was, minus the rating without brand names. Each row is the difference between the brands that received that kind of page and the brands that received no pages in the same model, after preference tuning. The estimates are means over 35 trained versions of Qwen 2.5 7B (seven assignments of the kinds to the brands, each trained with five seeds); the 95% intervals come from 2,000 bootstrap draws that resample the versions and, inside each version, the tables. Holm's correction is across the six kinds for each outcome, and across the two comparisons between kinds for each outcome.

| Outcome | Kind of page | 80 pages minus none [95% CI] | *p* | 320 pages minus 80 [95% CI] | *p* |
|:------------------------------|:-------------------|---------------------:|-------:|---------------------:|-------:|
| Equity on the optimal product | Reliability facts | 3.65 [0.43, 7.22] | .029 | 1.11 [−2.77, 4.87] | .535 |
|  | Favorable comments | −2.18 [−5.18, 1.07] | .172 | 0.72 [−2.74, 4.36] | .680 |
|  | Expert reviews | 1.18 [−1.86, 4.37] | .444 | 0.31 [−4.16, 4.67] | .927 |
|  | Advertising copy | −0.39 [−3.08, 2.64] | .806 | 1.74 [−3.03, 6.05] | .440 |
|  | Forum posts | 1.09 [−2.29, 4.79] | .525 | −0.62 [−4.64, 3.04] | .776 |
|  | Bare mentions | 1.56 [−1.31, 4.23] | .246 | 6.32 [2.11, 10.57] | .006 |
| Equity on a worse product | Reliability facts | 2.01 [0.47, 3.87] | .009 | 0.24 [−1.40, 1.88] | .772 |
|  | Favorable comments | 0.43 [−1.16, 2.04] | .602 | 0.38 [−1.09, 1.85] | .592 |
|  | Expert reviews | 1.38 [−0.11, 2.97] | .066 | −0.44 [−2.40, 1.22] | .597 |
|  | Advertising copy | 1.02 [−0.47, 2.61] | .198 | 0.26 [−1.13, 1.74] | .691 |
|  | Forum posts | 0.76 [−0.64, 2.23] | .251 | −0.04 [−1.73, 1.57] | .968 |
|  | Bare mentions | 1.48 [−0.10, 3.00] | .060 | 0.61 [−1.21, 2.69] | .506 |
| Salience | Reliability facts | 7.44 [4.00, 11.89] | < .001 | 2.91 [−2.60, 9.20] | .324 |
|  | Favorable comments | 10.84 [5.74, 17.37] | < .001 | 16.19 [6.09, 26.46] | < .001 |
|  | Expert reviews | 18.53 [10.54, 27.57] | < .001 | 29.17 [14.51, 43.46] | < .001 |
|  | Advertising copy | 4.70 [2.30, 7.64] | < .001 | 12.47 [6.09, 19.66] | < .001 |
|  | Forum posts | 23.46 [13.61, 34.47] | < .001 | 23.29 [8.37, 37.74] | .002 |
|  | Bare mentions | 1.54 [0.29, 3.20] | .007 | 0.11 [−1.47, 1.47] | .823 |
| Recognition | Reliability facts | 13.22 [9.76, 17.20] | < .001 | −0.22 [−1.01, 0.44] | .539 |
|  | Favorable comments | 12.51 [8.94, 16.61] | < .001 | 0.71 [−0.02, 1.48] | .058 |
|  | Expert reviews | 9.62 [6.06, 13.81] | < .001 | 2.80 [0.65, 5.09] | .013 |
|  | Advertising copy | 11.39 [7.94, 15.37] | < .001 | 0.23 [−1.75, 2.22] | .815 |
|  | Forum posts | 11.00 [7.22, 15.08] | < .001 | 2.25 [0.83, 4.37] | .001 |
|  | Bare mentions | 9.37 [5.47, 13.39] | < .001 | 2.64 [0.09, 5.25] | .042 |
| Inferred quality | Reliability facts | 0.06 [0.03, 0.10] | < .001 | 0.00 [−0.03, 0.04] | .811 |
|  | Favorable comments | 0.08 [0.04, 0.11] | < .001 | 0.02 [−0.01, 0.05] | .206 |
|  | Expert reviews | 0.04 [0.01, 0.07] | .013 | 0.04 [−0.01, 0.08] | .103 |
|  | Advertising copy | 0.05 [0.02, 0.08] | < .001 | 0.01 [−0.03, 0.05] | .542 |
|  | Forum posts | 0.05 [0.02, 0.09] | .001 | 0.04 [0.00, 0.07] | .041 |
|  | Bare mentions | 0.06 [0.03, 0.09] | .001 | 0.05 [0.01, 0.09] | .009 |
| Credibility | Reliability facts | 0.08 [−0.01, 0.17] | .087 | 0.04 [−0.06, 0.15] | .439 |
|  | Favorable comments | 0.03 [−0.07, 0.13] | .575 | 0.03 [−0.08, 0.13] | .605 |
|  | Expert reviews | 0.03 [−0.05, 0.10] | .443 | 0.12 [0.04, 0.21] | .003 |
|  | Advertising copy | 0.06 [−0.01, 0.14] | .092 | 0.02 [−0.10, 0.13] | .837 |
|  | Forum posts | 0.04 [−0.04, 0.13] | .254 | 0.07 [−0.03, 0.17] | .140 |
|  | Bare mentions | 0.07 [−0.02, 0.16] | .104 | −0.03 [−0.13, 0.06] | .530 |

Table: Study 3a, the 14 Fictitious Product Brands: 80 and 320 Pages of Each Kind (Qwen 2.5 7B)

*Notes:* Equity on the optimal product: the probability that the model chose the optimal product of a Study 1a table when the product was shown under the brand's name, minus the probability without brand names, in percentage points. Equity on a worse product: the same difference when the brand's name was on a product that was worse than the optimal product. Salience: the percentage of the model's lists of the category's brands that named the brand. Recognition: the probability, in percentage points, that the model answered that it knew the brand. Inferred quality and credibility: the model's rating from 1 to 7 of a product under the brand's name, and of how believable its listing was, minus the rating without brand names. Each row is the difference between the brands that received that kind of page and the brands that received no pages in the same model, after preference tuning. In each model, one of the two brands that received a kind of page received 80 pages and the other 320. The first difference is the brand with 80 pages minus the brands with no pages; the second is the brand with 320 pages minus the brand with 80. *p* is two-sided, from the same 2,000 bootstrap draws.

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

Table: Study 3a: Effect of Each Kind of Page (Llama 3.1 8B)

*Notes:* Equity on the optimal product: the probability that the model chose the optimal product of a Study 1a table when the product was shown under the brand's name, minus the probability without brand names, in percentage points. Equity on a worse product: the same difference when the brand's name was on a product that was worse than the optimal product. Salience: the percentage of the model's lists of the category's brands that named the brand. Recognition: the probability, in percentage points, that the model answered that it knew the brand. Inferred quality and credibility: the model's rating from 1 to 7 of a product under the brand's name, and of how believable its listing was, minus the rating without brand names. Each row is the difference between the brands that received that kind of page and the brands that received no pages in the same model, after preference tuning. The estimates are means over 35 trained versions of Llama 3.1 8B (seven assignments of the kinds to the brands, each trained with five seeds); the 95% intervals come from 2,000 bootstrap draws that resample the versions and, inside each version, the tables. Holm's correction is across the six kinds for each outcome, and across the two comparisons between kinds for each outcome.

| Outcome | Kind of page | 80 pages minus none [95% CI] | *p* | 320 pages minus 80 [95% CI] | *p* |
|:------------------------------|:-------------------|---------------------:|-------:|---------------------:|-------:|
| Equity on the optimal product | Reliability facts | 1.57 [−1.90, 4.99] | .364 | −0.16 [−4.72, 4.52] | .963 |
|  | Favorable comments | −2.49 [−6.91, 1.66] | .245 | 0.08 [−4.31, 4.35] | .966 |
|  | Expert reviews | −0.05 [−2.67, 2.78] | .993 | 2.55 [−1.69, 6.65] | .220 |
|  | Advertising copy | −0.27 [−3.04, 2.38] | .811 | 2.69 [−1.39, 6.55] | .176 |
|  | Forum posts | 2.08 [−0.89, 5.32] | .179 | −4.45 [−8.65, −0.91] | .009 |
|  | Bare mentions | 1.67 [−3.53, 6.51] | .478 | 4.80 [−0.81, 10.82] | .087 |
| Equity on a worse product | Reliability facts | 1.53 [0.50, 2.65] | .006 | −0.03 [−1.48, 1.59] | .990 |
|  | Favorable comments | 0.00 [−1.10, 1.24] | .996 | −0.07 [−1.28, 1.12] | .971 |
|  | Expert reviews | 0.17 [−0.55, 0.89] | .646 | 0.99 [−0.10, 2.14] | .075 |
|  | Advertising copy | 0.47 [−0.31, 1.25] | .226 | 1.36 [−0.14, 2.83] | .076 |
|  | Forum posts | 0.76 [−0.06, 1.69] | .074 | −0.81 [−2.01, 0.45] | .162 |
|  | Bare mentions | 0.68 [−0.60, 1.91] | .259 | 1.99 [−0.31, 4.72] | .097 |
| Salience | Reliability facts | 11.19 [6.89, 15.63] | < .001 | 15.71 [4.37, 28.56] | .002 |
|  | Favorable comments | 25.54 [15.74, 36.09] | < .001 | 21.17 [3.01, 38.57] | .018 |
|  | Expert reviews | 33.04 [23.09, 44.19] | < .001 | 32.53 [11.61, 51.77] | .003 |
|  | Advertising copy | 24.34 [15.70, 33.96] | < .001 | 9.69 [−5.70, 24.74] | .234 |
|  | Forum posts | 38.51 [27.21, 49.96] | < .001 | 27.07 [7.97, 44.47] | .007 |
|  | Bare mentions | 0.57 [0.06, 1.31] | .021 | 0.69 [−0.40, 1.89] | .258 |
| Recognition | Reliability facts | 1.73 [−0.36, 4.25] | .115 | 0.60 [−0.19, 1.67] | .202 |
|  | Favorable comments | 0.74 [−0.94, 2.74] | .466 | 1.56 [−0.25, 3.70] | .109 |
|  | Expert reviews | −0.71 [−2.61, 0.87] | .450 | 4.14 [0.82, 8.09] | .008 |
|  | Advertising copy | 1.84 [0.34, 3.73] | .014 | 0.64 [−0.66, 2.06] | .353 |
|  | Forum posts | 0.89 [−0.03, 2.01] | .059 | 1.31 [−0.11, 3.23] | .083 |
|  | Bare mentions | 0.55 [−1.77, 2.99] | .692 | 1.58 [−0.95, 4.21] | .191 |
| Inferred quality | Reliability facts | 0.00 [−0.05, 0.05] | .970 | −0.04 [−0.09, 0.00] | .063 |
|  | Favorable comments | 0.07 [0.02, 0.13] | .010 | 0.00 [−0.05, 0.05] | .921 |
|  | Expert reviews | 0.01 [−0.04, 0.06] | .753 | −0.01 [−0.05, 0.03] | .685 |
|  | Advertising copy | 0.06 [0.02, 0.11] | .010 | −0.06 [−0.11, −0.01] | .030 |
|  | Forum posts | −0.02 [−0.07, 0.03] | .468 | 0.04 [0.00, 0.08] | .094 |
|  | Bare mentions | 0.04 [−0.01, 0.11] | .154 | 0.04 [−0.01, 0.09] | .142 |
| Credibility | Reliability facts | 0.09 [0.03, 0.15] | .007 | 0.00 [−0.08, 0.08] | .983 |
|  | Favorable comments | 0.07 [0.00, 0.13] | .039 | 0.08 [0.01, 0.15] | .026 |
|  | Expert reviews | 0.08 [0.01, 0.17] | .020 | 0.02 [−0.07, 0.11] | .601 |
|  | Advertising copy | 0.14 [0.08, 0.22] | < .001 | −0.06 [−0.15, 0.01] | .121 |
|  | Forum posts | 0.04 [−0.02, 0.09] | .180 | 0.06 [−0.03, 0.15] | .185 |
|  | Bare mentions | 0.05 [−0.02, 0.12] | .196 | 0.12 [0.04, 0.21] | .006 |

Table: Study 3a, the 14 Fictitious Product Brands: 80 and 320 Pages of Each Kind (Llama 3.1 8B)

*Notes:* Equity on the optimal product: the probability that the model chose the optimal product of a Study 1a table when the product was shown under the brand's name, minus the probability without brand names, in percentage points. Equity on a worse product: the same difference when the brand's name was on a product that was worse than the optimal product. Salience: the percentage of the model's lists of the category's brands that named the brand. Recognition: the probability, in percentage points, that the model answered that it knew the brand. Inferred quality and credibility: the model's rating from 1 to 7 of a product under the brand's name, and of how believable its listing was, minus the rating without brand names. Each row is the difference between the brands that received that kind of page and the brands that received no pages in the same model, after preference tuning. In each model, one of the two brands that received a kind of page received 80 pages and the other 320. The first difference is the brand with 80 pages minus the brands with no pages; the second is the brand with 320 pages minus the brand with 80. *p* is two-sided, from the same 2,000 bootstrap draws.
